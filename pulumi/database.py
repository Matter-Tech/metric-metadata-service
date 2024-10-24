import config
from pulumi_aws import rds

from pulumi import Output, ResourceOptions


def create_rds(
    instance_name: str,
    database_name: str,
    master_user: Output[str] | str,
    master_password: Output[str] | str | None = None,
    pulumi_identifier: str | None = None,
    instance_class: str = "db.t3.small",
    version: str = "16.1",
    storage: int = 20,
    storage_encrypted: bool = True,
    deletion_protection: bool = True,
    performance_insights_enabled=True,
    monitoring_interval: int = None,
    options: ResourceOptions | None = None,
) -> rds.Instance:
    if bool(pulumi_identifier) is False:
        pulumi_identifier = f"{instance_name}-rds"
    if not options:
        options = ResourceOptions()

    return rds.Instance(
        pulumi_identifier,
        identifier=instance_name,
        db_name=database_name,
        allocated_storage=storage,
        engine="postgres",
        engine_version=version,
        instance_class=instance_class,
        db_subnet_group_name=config.RDS_SUBNET_GROUP_NAME,
        username=master_user,
        password=master_password,
        skip_final_snapshot=True,
        copy_tags_to_snapshot=True,
        deletion_protection=deletion_protection,
        storage_encrypted=storage_encrypted,
        enabled_cloudwatch_logs_exports=["postgresql"],
        backup_retention_period=7,
        max_allocated_storage=1000,
        vpc_security_group_ids=[config.RDS_SECURITY_GROUP],
        apply_immediately=False,
        performance_insights_enabled=performance_insights_enabled,
        monitoring_interval=monitoring_interval,
        opts=options,
    )
