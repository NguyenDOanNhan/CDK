from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2, Tags, Fn, CfnTag
)
from aws_cdk.aws_ec2 import(
    Vpc, CfnRouteTable, RouterType, CfnRoute, CfnInternetGateway, CfnVPCGatewayAttachment, \
    CfnSubnet, CfnSubnetRouteTableAssociation, CfnSecurityGroup, CfnInstance
)
from constructs import Construct
from . import config

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
                CfnTag(
                    key=config.NAME,
                    value=config.PROJECT + "-" +  config.ENVIRONMENT[0] + "-igw" 
                ),
                CfnTag(
                    key=config.ENV,
                    value=config.PROJECT + ":" + config.ENVIRONMENT[0]
                )
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
                CfnTag(
                    key=config.NAME,
                    value=config.PROJECT + "-" +  config.ENVIRONMENT[0] + "-routetable" 
                ),
                CfnTag(
                    key=config.ENV,
                    value=config.PROJECT + ":" + config.ENVIRONMENT[0]
                )
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

    def create_subnets(self, count):
        """ Create subnets of the VPC """
        for i in range(count):
            subnet =  CfnSubnet(self, 'Subnet' + str(i+1),
                vpc_id=self.vpc.vpc_id,
                cidr_block='10.0.' + str(i+1) + '.0/24',
                availability_zone=Fn.select(i,Fn.get_azs()),
                map_public_ip_on_launch=False,
                tags=[
                    CfnTag(
                        key="Name",
                        value=config.PROJECT + "-" +  config.ENVIRONMENT[0] + "-sub-" + str(i+1)
                    ),
                    CfnTag(
                        key=config.ENV,
                        value=config.PROJECT + ":" + config.ENVIRONMENT[0]
                     )
                ]
            )
            # subnet_route_table_associationscdk
            # CfnSubnetRouteTableAssociation(self,"SubnetRouteTableAssociation" + str(i),
            #     route_table_id=self.rtb.ref,
            #     subnet_id=subnet.ref
            # )
            self.subnets['subnet' + str(i+1)] = subnet

        for i in range(count):
            CfnSubnetRouteTableAssociation(self,"SubnetRouteTableAssociation" + str(i),
                route_table_id=self.rtb.ref,
                subnet_id=self.subnets['subnet' + str(i+1)].ref
            )
