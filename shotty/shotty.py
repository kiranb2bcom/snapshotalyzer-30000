import boto3
import botocore
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

def filter_instances(project) :
    instances=[]

    if project:
        filters=[{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else :
        instances = ec2.instances.all()

    return instances

def has_pending_snapshots(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots and snapshots[0].state=='pending'

@click.group()
def cli():
    """Shotty manages Snapshots"""

@cli.group("volumes")
def volumes():
    """Commands for Volumes"""

@volumes.command('list')
@click.option('--project', default=None, help="Only volumes for project (tag Projet:<name>)")
def list_volumes(project) :
    "list EC2 volumes"

    instances = filter_instances(project)
    for i in instances:
        for v in i.volumes.all():
            print(", ".join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "Gib",
                v.encrypted and "Encrypted" or "Not Encrypted")))
    return

@cli.group("snapshots")
def snapshots():
    """Commands for Snapshots"""

@snapshots.command('list')
@click.option('--project', default=None, help="Only Snapshots for project (tag Projet:<name>)")
@click.option('--all', 'list_all', default=False, is_flag=True, help="Show all Snapshots for each volume, not just the recent one.")
def list_snapshots(project, list_all) :
    "list EC2 snapshots"

    instances = filter_instances(project)
    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ".join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime('%c'))))
                if s.state=='completed' and not list_all : break
    return

@cli.group("instances")
def instances():
    """Commands for Instances"""

@instances.command('list')
@click.option('--project', default=None, help="Only instances for project (tag Projet:<name>)")
def list_instances(project) :
    "list EC2 instances"

    instances = filter_instances(project)
    for i in instances:
        tags = {t['Key']:t['Value'] for t in i.tags or []}
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Project', '<No Project>'))))

    return

@instances.command('stop')
@click.option('--project', default=None, help="Only instances for project (tag Projet:<name>)")
def stop_instances(project) :
    "stop EC2 instances"

    instances = filter_instances(project)
    for i in instances:
        print("Stopping {0}...".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print("Could not stop instance {0}. ".format(i.id) + str(e))
            continue

    return

@instances.command('start')
@click.option('--project', default=None, help="Only instances for project (tag Projet:<name>)")
def stop_instances(project) :
    "start EC2 instances"

    instances = filter_instances(project)
    for i in instances:
        print("Starting {0}...".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print("Could not start instance {0}. ".format(i.id) + str(e))
            continue
    return

@instances.command('snapshot', help="Create Snapshot of all volumes")
@click.option('--project', default=None, help="Only instances for project (tag Projet:<name>)")
def create_snapshots(project) :
    "Create Snapshots for EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Stopping instance {0} ....".format(i.id))
        i.stop()
        i.wait_until_stopped()
        for v in i.volumes.all():
            if has_pending_snapshots(v):
                print("  Skipping volume {0}, snapshot already in progress".format(v.id))
                continue
            print("Creating snapshot for {0} volume of {1} instance".format(v.id, i.id))
            v.create_snapshot(Description="Created by snapshotalyzer 30000")
        print("Starting instance {0} ....".format(i.id))
        i.start()
        i.wait_until_running()
    print("Jobs's Done!")

    return

if __name__ == '__main__':
    cli()
