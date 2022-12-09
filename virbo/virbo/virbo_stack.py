from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2, Tags, Fn, CfnTag
)
from aws_cdk.aws_ec2 import(
    Vpc, CfnRouteTable, RouterType, CfnRoute, CfnInternetGateway, CfnVPCGatewayAttachment, \
    CfnSubnet, CfnSubnetRouteTableAssociation, CfnSecurityGroup, CfnInstance, CfnNetworkInterface
)
from constructs import Construct
from . import config
import os
dirname = os.path.dirname(__file__)
class VirboStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.subnets = {}
        self.vpc = ec2.Vpc(self, 
            "VPC",
            cidr="10.0.0.0/16",
            max_azs=4,
            nat_gateways=0,
            subnet_configuration=[],
            enable_dns_hostnames=True,
            enable_dns_support=True
        )
        Tags.of(self.vpc).add(config.NAME, config.PROJECT + "-" +  config.ENVIRONMENT[0] + "-vpc")

        # Create internetGateway
        igw=ec2.CfnInternetGateway(self, "InternetGatewat",
            tags=[
                CfnTag(key=config.NAME,value=config.PROJECT + "-" +  config.ENVIRONMENT[0] + "-igw"),
                CfnTag(key=config.ENV,value=config.PROJECT + ":" + config.ENVIRONMENT[0])
            ]
        )
        # Attch igw to vpc
        ec2.CfnVPCGatewayAttachment(self,"VPCGatewayAttachment",
            vpc_id=self.vpc.vpc_id,
            internet_gateway_id=igw.attr_internet_gateway_id
        )

        # Create Route table
        self.rtb = ec2.CfnRouteTable(self,'RouteTable',
            vpc_id=self.vpc.vpc_id,
            tags=[
                CfnTag(key=config.NAME,value=config.PROJECT + "-" +  config.ENVIRONMENT[0] + "-routetable"),
                CfnTag(key=config.ENV,value=config.PROJECT + ":" + config.ENVIRONMENT[0])
            ]
        )

        # Route table
        ec2.CfnRoute(self, 'RouteTablepublic',
            route_table_id= self.rtb.ref,
            gateway_id=igw.attr_internet_gateway_id,
            destination_cidr_block=config.CIDR_INTERNET
        )
        
        # Subnet
        self.create_subnets(count=4)
        # Subnet associate to route table
        self.create_subnet_route_table_associate(count=4)

        # security groups
        sg = CfnSecurityGroup(self,"SecurityGroupEC2",
            vpc_id=self.vpc.vpc_id,
            group_description="Security group for ec2",
            security_group_ingress=[
                CfnSecurityGroup.IngressProperty(
                    ip_protocol=config.TCP,
                    cidr_ip=config.CIDR_INTERNET,
                    from_port=config.PORT_REAT_JS,
                    to_port=config.PORT_REAT_JS
                ),
                CfnSecurityGroup.IngressProperty(
                    ip_protocol=config.TCP,
                    cidr_ip=config.CIDR_PUBLIC_IP,
                    from_port=config.PORT_SSH,
                    to_port=config.PORT_SSH
                ),
                CfnSecurityGroup.IngressProperty(
                    ip_protocol=config.TCP,
                    cidr_ip=config.CIDR_INTERNET,
                    from_port=config.PORT_RDS_MYSQL,
                    to_port=config.PORT_RDS_MYSQL
                ),
                CfnSecurityGroup.IngressProperty(
                    ip_protocol=config.TCP,
                    cidr_ip=config.CIDR_INTERNET,
                    from_port=config.PORT_HTTP,
                    to_port=config.PORT_HTTP,
                )

            ],
            security_group_egress=[
                CfnSecurityGroup.EgressProperty(
                    ip_protocol='-1',
                    cidr_ip=config.CIDR_INTERNET
                )   
            ],
            tags=[
                CfnTag(key=config.NAME,value=config.PROJECT + "-" +  config.ENVIRONMENT[0] + "-ec2-sg"),
                CfnTag(key=config.ENV,value=config.PROJECT + ":" + config.ENVIRONMENT[0])
            ]
        )

        sg1 = CfnSecurityGroup(self,"SecurityGroupRDS",
            vpc_id=self.vpc.vpc_id,
            group_description="Security group for RDS",
            security_group_ingress=[
                CfnSecurityGroup.IngressProperty(
                    ip_protocol=config.TCP,
                    from_port=config.PORT_RDS_MYSQL,
                    to_port=config.PORT_RDS_MYSQL,
                    source_security_group_id=sg.ref
                )
            ],
            security_group_egress=[
                CfnSecurityGroup.EgressProperty(
                    ip_protocol='-1',
                    cidr_ip=config.CIDR_INTERNET,
                )   
            ],
            tags=[
                CfnTag(key="Name",value=config.PROJECT + "-" +  config.ENVIRONMENT[0] + "-rds-sg"),
                CfnTag(key=config.ENV,value=config.PROJECT + ":" + config.ENVIRONMENT[0])
            ]
        )
        
        # ec2 instance
        with open(os.path.join(dirname, "user-data.sh"), 'r', encoding='utf-8') as file_user_data:
           user_datas = file_user_data.readlines()

        cfinstance = CfnInstance(self,"InstanceFE",
            key_name=config.KEY_EC2,
            disable_api_termination=False,
            image_id=config.AMI_EC2,
            instance_type=config.INSTANCE_TYPE[0], # t2.micro
            network_interfaces=[
                ec2.CfnInstance.NetworkInterfaceProperty(
                    device_index="0",
                    associate_public_ip_address=True,
                    group_set=[sg.ref],
                    subnet_id=self.subnets['subnet1'].ref
                )
            ],
            user_data=Fn.base64(
                "".join(user_datas)
            ),
            # user_data=Fn.base64(open(os.path.join(dirname, "user-data.sh"), "r")),
            tags=[
                CfnTag(key=config.NAME,value=config.PROJECT + "-" +  config.ENVIRONMENT[0] + "-fe-ec2"),
                CfnTag(key=config.ENV,value=config.PROJECT + ":" + config.ENVIRONMENT[0])
            ] 
        )
        
    def create_subnets(self, count):
        """ Create subnets of the VPC """
        for i in range(count):
            subnet =  CfnSubnet(self, 'Subnet' + str(i+1),
                vpc_id=self.vpc.vpc_id,
                cidr_block='10.0.' + str(i+1) + '.0/24',
                availability_zone=Fn.select(i,Fn.get_azs()),
                map_public_ip_on_launch=False,
                tags=[
                    CfnTag(key="Name",value=config.PROJECT + "-" +  config.ENVIRONMENT[0] + "-sub-" + str(i+1)),
                    CfnTag(key=config.ENV,value=config.PROJECT + ":" + config.ENVIRONMENT[0])
                ]
            )
            self.subnets['subnet' + str(i+1)] = subnet

    
    def create_subnet_route_table_associate(self, count):
        for i in range(count):
                CfnSubnetRouteTableAssociation(self,"SubnetRouteTableAssociation" + str(i),
                    route_table_id=self.rtb.ref,
                    subnet_id=self.subnets['subnet' + str(i+1)].ref
        )
    

