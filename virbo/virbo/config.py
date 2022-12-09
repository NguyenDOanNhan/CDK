from aws_cdk import(
    CfnTag
)
# variable
ENV='Env'
NAME='Name'
ENVIRONMENT=['stg', 'pro', 'test']
PROJECT='virbo'



# port & cidr

CIDR_PUBLIC_IP='118.70.52.39/32'
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
INSTANCE_TYPE=['t2.micro', 't2.small', 't3.micro', 't3.small']