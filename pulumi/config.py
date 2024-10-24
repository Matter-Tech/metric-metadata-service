import pulumi

CONFIG = pulumi.Config("metric-metadata-service")
ENV = CONFIG.require("env")
ENVIRONMENT = CONFIG.require("environment")
DB_NAME = CONFIG.require("db_name")
DB_USERNAME = CONFIG.require("db_username")
DB_INSTANCE_CLASS = CONFIG.require("db_instance_class")
K8S_NAMESPACE = CONFIG.require("k8s_namespace")
K8S_OIDC_PROVIDER_ID = CONFIG.require("k8s_oidc_provider_id")
SG_BASTION = CONFIG.require("sg_bastion")
SG_EKS_CLUSTER = CONFIG.require("sg_eks_cluster")
PROMETHEUS_PUSH_GATEWAY_HOST = CONFIG.require("prometheus_push_gateway_host")
CACHE_SUBNET_GROUP_NAME = CONFIG.require("cache_subnet_group_name")
CACHE_VPC_ID = CONFIG.require("cache_vpc_id")

app_stack = pulumi.StackReference(CONFIG.require("app_stack"))
RDS_SUBNET_GROUP_NAME = app_stack.require_output("rds-subnet-group-name")
RDS_SECURITY_GROUP = app_stack.require_output("rds-security-group-id")
