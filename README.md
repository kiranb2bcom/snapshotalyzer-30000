# snapshotalyzer-30000
Demo project to manage aws ec2 instance snapshots

## About

This project is a demo, uses boto3 to manage AWS EC2 instance snapshots

## Configuring

Shotty uses the configuration created by AWS cli e.g.

`aws configure --profile shotty`

## Running
`pipenv run py shotty/shotty.py <command> <subcommand> <--project=PROJECT>

*command* is instances, volumes, snapshots

*subcommand* - depends on command

*project* is optional
