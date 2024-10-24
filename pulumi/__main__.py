import json
import urllib.parse

import config
import pulumi_random as random
from database import create_rds
from pulumi_aws import ec2, ecr, elasticache, get_caller_identity, iam, secretsmanager

from pulumi import Output, ResourceOptions

caller_identity = get_caller_identity()

password = random.RandomPassword(
    "metric-metadata-service-db-password",
    override_special="!#$%&*()-_=+[]{}<>:?",
    length=50,
)

db = create_rds(
    instance_name=f"metric-metadata-service-db-{config.ENV}",
    database_name="metric_metadata_service",
    master_user="metric_metadata_service_db_user",
    master_password=password.result,
    instance_class=config.DB_INSTANCE_CLASS,
    pulumi_identifier=f"metric-metadata-service-db-{config.ENV}",
    options=ResourceOptions(depends_on=[password]),
    deletion_protection=False,
)

cache_security_group = ec2.SecurityGroup(
    "metric-metadata-service-cache",
    description="Security group for Metric Metadata Service Cache",
    ingress=[
        ec2.SecurityGroupIngressArgs(
            description="Allow access from VPN VPC",
            from_port=6379,
            to_port=6379,
            protocol="tcp",
            cidr_blocks=["0.100.0.0/16"],
        ),
        ec2.SecurityGroupIngressArgs(
            description="Allow access from EKS Cluster",
            from_port=6379,
            to_port=6379,
            protocol="tcp",
            security_groups=[config.SG_BASTION, config.SG_EKS_CLUSTER],
        ),
    ],
    vpc_id=config.CACHE_VPC_ID,
    tags={"Name": "andromeda | palantir"},
)

cache_cluster = elasticache.Cluster(
    "metric-metadata-service-cache",
    num_cache_nodes=1,
    node_type="cache.t2.micro",
    engine="redis",
    subnet_group_name=config.CACHE_SUBNET_GROUP_NAME,
    security_group_ids=[cache_security_group.id],
)

repo = ecr.Repository(
    "metric-metadata-service-ecr-repository",
    name="core_services/metric-metadata-service",
    image_scanning_configuration={"scan_on_push": True},
)

secrets_stack = secretsmanager.Secret(
    "metric-metadata-service-secrets-stack",
    name="core.eks.metric-metadata-service.stack",
    description="Stack generated Kubernetes Secret Values for metric-metadata-service",
)

secrets_manual = secretsmanager.Secret(
    "metric-metadata-service-secrets-manual",
    name="core.eks.metric-metadata-service.manual",
    description="Manually added Kubernetes Secret Values for metric-metadata-service",
)

cache_endpoint = Output.all(cache_cluster.cache_nodes).apply(lambda args: args[0][0]["address"])

secretsmanager.SecretVersion(
    "metric-metadata-service-secrets-stack-eks-version",
    secret_id=secrets_stack.name,
    secret_string=Output.all(
        password.result,
        db.address,
        db.port,
        db.db_name,
        cache_endpoint,
        cache_cluster.port,
    ).apply(
        lambda args: json.dumps(
            {
                "DB_USERNAME": f"{config.DB_USERNAME}",
                "DB_PASSWORD": args[0],  # password.result
                "DB_HOST": args[1],  # db.address
                "DB_PORT": args[2],  # db.port
                "DB_NAME": args[3],  # db.db_name
                "DB_URL": f"postgresql+asyncpg://{config.DB_USERNAME}:{urllib.parse.quote_plus(args[0])}@{args[1]}:{args[2]}/{args[3]}",
                "MIGRATIONS_FOLDER": "app/database/migrations",
                "CELERY_BROKER_URL": "sqs://",
                "CELERY_DEAD_LETTER_QUEUE": "metric-metadata-service-dlqs",
                "ENABLE_METRICS": "true",
                "ENV": config.ENV,
                "ENVIRONMENT": config.ENVIRONMENT,
                "AUTH_API_URL": "http://auth-api:8080",
                "CACHE_ENDPOINT_URL": args[4],  # cache.cluster_address
                "CACHE_PORT": args[5],  # cache.port
                "PROMETHEUS_PUSH_GATEWAY_HOST": config.PROMETHEUS_PUSH_GATEWAY_HOST,
            },
            separators=(",", ":"),
        )
    ),
    opts=ResourceOptions(
        parent=secrets_stack,
        depends_on=[secrets_stack],
    ),
)

policy = iam.Policy(
    "metric-metadata-service-policy",
    name="MetricMetadataServicePolicy",
    policy=Output.all(secrets_stack.arn, secrets_manual.arn)
    .apply(
        lambda args: {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": ["secretsmanager:GetSecretValue"], "Resource": [args[0], args[1]]},
                {
                    "Effect": "Allow",
                    "Action": ["sqs:*"],
                    "Resource": f"arn:aws:sqs:*:{caller_identity.account_id}:metric-metadata-service-*",
                },
                {
                    "Effect": "Allow",
                    "Action": "sqs:ListQueues",
                    "Resource": f"arn:aws:sqs:*:{caller_identity.account_id}:*",
                },
            ],
        }
    )
    .apply(json.dumps),
)

iam.Role(
    "metric-metadata-service-role",
    name="metric-metadata-service",
    description="The role assumed by the metric-metadata-service",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Federated": f"arn:aws:iam::{caller_identity.account_id}:oidc-provider/oidc.eks.eu-central-1.amazonaws.com/id/{config.K8S_OIDC_PROVIDER_ID}",
                    },
                    "Action": "sts:AssumeRoleWithWebIdentity",
                    "Condition": {
                        "StringEquals": {
                            f"oidc.eks.eu-central-1.amazonaws.com/id/{config.K8S_OIDC_PROVIDER_ID}:sub": f"system:serviceaccount:{config.K8S_NAMESPACE}:metric-metadata-service-account"
                        }
                    },
                }
            ],
        }
    ),
    managed_policy_arns=[policy.arn],
)
