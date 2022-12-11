from aws_cdk import(
    CfnTag
)
# variable
ENV='Env'
NAME='Name'
ENVIRONMENT=['stg', 'pro', 'test']
PROJECT='virbo'
# port & cidr
CIDR_PUBLIC_IP='27.67.15.145/32'
PORT_REAT_JS=3000
PORT_HTTP=80
PORT_SSH=22
PORT_RDS_MYSQL=3306
CIDR_INTERNET='0.0.0.0/0'
# protocal
TCP='tcp'
# EC2
KEY_EC2='NhanND'
AMI_EC2='ami-0a6b2839d44d781b2' # Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2022-12-01
EBS_SNAPSHOT_ID='snap-00c1ef076bdfa9780'
INSTANCE_TYPE=['t2.micro','t2.small','t3.micro','t3.small']
RDS_INSTANCE_TYPE=['db.t3.micro','db.t3.small','db.t3.medium','db.t3.large']
EBS_SIZE=20
VOLUME_TYPE=['io1','gp2']
#RDS
RDS_MYSQL_DATABASE_NAME = 'virbo'
RDS_MYSQL_MASTER_USERNAME='VirboAdmin'
RDS_MYSQL_MASTER_USER_PASSWORD='virboAdmin!123'
RDS_MYSQL_ALLOCATED_STORAGE="20"
RDS_MYSQL_ENGINE='mysql'
RDS_MYSQL_ENGINE_VERSION='5.7.38'
RDS_BACKUP_RETENTION_PERIOD=0 # Retention_period=0 is disable backup