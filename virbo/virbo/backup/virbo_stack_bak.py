from aws_cdk import (
    # Duration,
    Stack, Tags, Fn, CfnTag,
    aws_ec2 as ec2,
)
from aws_cdk.aws_ec2 import(
    Vpc, CfnRouteTable, CfnRoute, CfnInternetGateway, CfnVPCGatewayAttachment,
    CfnSubnet, CfnSubnetRouteTableAssociation, CfnSecurityGroup, CfnInstance
)
from aws_cdk.aws_rds import CfnDBInstance, CfnDBSubnetGroup
from aws_cdk.aws_iam import CfnRole, CfnPolicy, PolicyDocument, PolicyStatement, ServicePrincipal, Effect, CfnInstanceProfile
from aws_cdk.aws_s3 import CfnBucket, BlockPublicAccess
from constructs import Construct
from .. import config
import os
dirname = os.path.dirname(__file__)
class VirboStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # S3
        cfnBucket=CfnBucket(self,"s3Bucket",
                bucket_name=config.PROJECT  + '-' + config.ENVIRONMENT[0],
                public_access_block_configuration=BlockPublicAccess.BLOCK_ALL,            
            )
        # Role
        cfnRole=CfnRole(self,"Role",
                role_name= config.PROJECT + "-" + config.ENVIRONMENT[0] + "-ec2-role",
                managed_policy_arns=[
                    "arn:aws:iam::aws:policy/CloudWatchAgentAdminPolicy",
                    "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
                ],
                assume_role_policy_document=PolicyDocument(
                    statements=[
                        PolicyStatement(
                            effect=Effect.ALLOW,
                            principals=[ServicePrincipal("ec2.amazonaws.com")],
                            actions=["sts:AssumeRole"]
                        )
                    ]
                ),
                path="/"
            )
        cfnRole2=CfnRole(self,"Role2",
                role_name='GlueServiceRole-' + config.PROJECT + "-" + config.ENVIRONMENT[0],
                managed_policy_arns=["arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"],
                assume_role_policy_document=PolicyDocument(
                    statements=[
                        PolicyStatement(
                            effect=Effect.ALLOW,
                            principals=[ServicePrincipal("glue.amazonaws.com")],
                            actions=["sts:AssumeRole"]
                        )
                    ]
                ),
                path="/"
            )
        # Policy
        cfnpolicy=CfnPolicy(self, "policy",
                policy_name='AWSGlueServicePolicy-' + config.PROJECT + "-" + config.ENVIRONMENT[0] + '-s3Policy',
                roles=[cfnRole2.ref],
                policy_document=PolicyDocument(
                    statements=[
                        PolicyStatement(
                            effect= Effect.ALLOW,
                            actions=[
                                "s3:GetObject",
                                "s3:PutObject"
                            ],
                            resources=[cfnBucket.attr_arn + '*'],
                        )
                    ]
                )
            )
        cfnpolicy2=CfnPolicy(self, "policy2",
                policy_name='EC2ServicePolicy-' + config.PROJECT + "-" + config.ENVIRONMENT[0] + '-s3Policy',
                roles=[cfnRole.ref],
                policy_document=PolicyDocument(
                    statements=[
                        PolicyStatement(
                            effect= Effect.ALLOW,
                            actions=[
                                "s3:GetObject",
                                "s3:PutObject",
                                "s3:ListBucket",
                                "s3:GetBucketAcl",
                                "s3:DeleteObject"
                            ],
                            resources=[cfnBucket.attr_arn + '*'],
                        )
                    ]
                )
            )
        self.subnets = {} # dict subnet
        self.cfnVpc = Vpc(self, 
                "VPC",
                cidr="10.0.0.0/16",
                max_azs=4,
                nat_gateways=0,
                subnet_configuration=[],
                enable_dns_hostnames=True,
                enable_dns_support=True
            )
        Tags.of(self.cfnVpc).add(config.NAME, config.PROJECT + "-" +  config.ENVIRONMENT[0] + "-vpc")
        # Create internetGateway
        cfnIgw=CfnInternetGateway(self, "InternetGatewat",tags=[CfnTag(key=config.NAME,value=config.PROJECT + "-" +  config.ENVIRONMENT[0] + "-igw")])
        # Attch igw to vpc
        CfnVPCGatewayAttachment(self,"VPCGatewayAttachment",
                vpc_id=self.cfnVpc.vpc_id,
                internet_gateway_id=cfnIgw.attr_internet_gateway_id
            )
        # Create Route table
        self.cfnRtb = CfnRouteTable(self,'RouteTable',
                vpc_id=self.cfnVpc.vpc_id,
                tags=[CfnTag(key=config.NAME,value=config.PROJECT + "-" +  config.ENVIRONMENT[0] + "-routetable")]
            )
        # Route table
        CfnRoute(self, 'RouteTablepublic',
                route_table_id= self.cfnRtb.ref,
                gateway_id=cfnIgw.attr_internet_gateway_id,
                destination_cidr_block=config.CIDR_INTERNET
            )
        # Subnet
        self.create_subnets(count=4)
        # Subnet associate to route table
        self.create_subnet_route_table_associate(count=4)
        # Security groups
        cfnSg = CfnSecurityGroup(self,"SecurityGroupEC2",
                vpc_id=self.cfnVpc.vpc_id,
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
                tags=[CfnTag(key=config.NAME,value=config.PROJECT + "-" +  config.ENVIRONMENT[0] + "-ec2-sg")]
            )
        cfnSg2 = CfnSecurityGroup(self,"SecurityGroupRDS",
                vpc_id=self.cfnVpc.vpc_id,
                group_description="Security group for RDS",
                security_group_ingress=[
                    CfnSecurityGroup.IngressProperty(
                        ip_protocol=config.TCP,
                        from_port=config.PORT_RDS_MYSQL,
                        to_port=config.PORT_RDS_MYSQL,
                        source_security_group_id=cfnSg.ref
                    )
                ],
                security_group_egress=[
                    CfnSecurityGroup.EgressProperty(
                        ip_protocol='-1',
                        cidr_ip=config.CIDR_INTERNET,
                    )   
                ],
                tags=[CfnTag(key="Name",value=config.PROJECT + "-" +  config.ENVIRONMENT[0] + "-rds-sg")]
            )
        # Load user data
        with open(os.path.join(dirname, "user-data.sh"), 'r', encoding='utf-8') as file_user_data:
           user_datas = file_user_data.readlines()
        # EC2 instance Profile
        cfnInstanceProfile=CfnInstanceProfile(self, "CfnInstanceProfile",
                roles=[cfnRole.ref],
                instance_profile_name=config.PROJECT
            )
        # EC2 instance
        cfInstance = CfnInstance(self,"InstanceFE",
                key_name=config.KEY_EC2,
                disable_api_termination=False,
                image_id=config.AMI_EC2,
                instance_type=config.INSTANCE_TYPE[0], # t2.micro
                iam_instance_profile=cfnInstanceProfile.ref,
                block_device_mappings=[ec2.CfnInstance.BlockDeviceMappingProperty(
                    device_name="/dev/sda1",
                    # the properties below are optional
                    ebs=ec2.CfnInstance.EbsProperty(
                        delete_on_termination=False,
                        encrypted=False,
                        snapshot_id=config.EBS_SNAPSHOT_ID,
                        volume_size=config.EBS_SIZE,
                        volume_type=config.VOLUME_TYPE[1]
                    ),
                    no_device=ec2.CfnInstance.NoDeviceProperty(),
                    virtual_name="ephemeral0"
                )],
                network_interfaces=[
                    ec2.CfnInstance.NetworkInterfaceProperty(
                        device_index="0",
                        associate_public_ip_address=True,
                        group_set=[cfnSg.ref],
                        subnet_id=self.subnets['subnet1'].ref
                    )
                ],
                user_data=Fn.base64("".join(user_datas)),
                tags=[CfnTag(key=config.NAME,value=config.PROJECT + "-" +  config.ENVIRONMENT[0] + "-fe-ec2")] 
            )
        # RDS sunet group
        CfnDbSG=CfnDBSubnetGroup(self,"CfnDBSubnetGroup",
                db_subnet_group_description="Rds MySQL Db Subnet Group for " + config.PROJECT + '-' + config.ENVIRONMENT[0],
                db_subnet_group_name=config.PROJECT + "-" + config.ENVIRONMENT[0] + "-db-sub-group",
                subnet_ids=[self.subnets['subnet1'].ref,self.subnets['subnet2'].ref]
            )
        # RDS instance
        cfnRdsMySQL=CfnDBInstance(self,"CfnDBInstance",
                db_instance_identifier=config.PROJECT + "-" +  config.ENVIRONMENT[0] + "-rds",
                db_name=config.RDS_MYSQL_DATABASE_NAME,
                master_username=config.RDS_MYSQL_MASTER_USERNAME,
                master_user_password=config.RDS_MYSQL_MASTER_USER_PASSWORD,
                multi_az=False,
                db_instance_class=config.RDS_INSTANCE_TYPE[0],
                engine=config.RDS_MYSQL_ENGINE,
                engine_version=config.RDS_MYSQL_ENGINE_VERSION,
                db_subnet_group_name=CfnDbSG.ref,
                vpc_security_groups=[cfnSg2.ref],
                deletion_protection=False,
                storage_type=config.VOLUME_TYPE[1],
                backup_retention_period=config.RDS_BACKUP_RETENTION_PERIOD,
                enable_cloudwatch_logs_exports=['error'],
                allocated_storage=config.RDS_MYSQL_ALLOCATED_STORAGE,
                port=str(config.PORT_RDS_MYSQL),
                publicly_accessible=False,
                tags=[CfnTag(key=config.NAME,value=config.PROJECT + "-" +  config.ENVIRONMENT[0] + "-rds")]
            )

    def create_subnets(self, count):
        """ Create subnets of the VPC """
        for i in range(count):
            subnet =  CfnSubnet(self, 'Subnet' + str(i+1),
                vpc_id=self.cfnVpc.vpc_id,
                cidr_block='10.0.' + str(i+1) + '.0/24',
                availability_zone=Fn.select(i,Fn.get_azs()),
                map_public_ip_on_launch=False,
                tags=[CfnTag(key="Name",value=config.PROJECT + "-" +  config.ENVIRONMENT[0] + "-sub-" + str(i+1))]
            )
            self.subnets['subnet' + str(i+1)] = subnet

    def create_subnet_route_table_associate(self, count):
        for i in range(count):
            CfnSubnetRouteTableAssociation(self,"SubnetRouteTableAssociation" + str(i),
                route_table_id=self.cfnRtb.ref,
                subnet_id=self.subnets['subnet' + str(i+1)].ref
            )