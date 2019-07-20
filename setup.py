from setuptools import setup

setup(
    name='snapshotalyzer-30000',
    version='0.1',
    author='kiran konathala',
    author_email='kiranb2bcom@gmail.com',
    description="snapshotalyzer is a tool used to manage aws ec2 snapshots",
    license="GPLv3+",
    packages=['shotty'],
    url="https://github.com/kiranb2bcom/snapshotalyzer-30000",
    install_requires=[
        'click',
        'boto3'
    ],
    entry_point='''
        [comsole_scripts]
        shotty=shotty.shotty:cli
    ''',
)
