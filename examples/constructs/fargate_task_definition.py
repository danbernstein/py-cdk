from aws_cdk import (
    aws_ecs as ecs,
    aws_ecr_assets as ecr_assets,
    aws_ecs_patterns as ecs_patterns,
    aws_applicationautoscaling as aas,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as events_targets,
    aws_cloudwatch as cloudwatch,
    core,
)


from .iam_role import RoleConstruct
from cdk_constants import ManagedPolicies, ServicePrincipals

import os.path
dirname = os.path.dirname(__file__)


class FargateTaskDefinitionConstruct(core.Construct):
    def __init__(self, app: core.Construct, id: str, **kwargs) -> None:
        super().__init__(app, id)

        iam_role = RoleConstruct(self,
                                 'role',
                                 assumed_by=iam.ServicePrincipal(ServicePrincipals.ECS_TASKS),
                                 managed_policies=[ManagedPolicies.AMAZON_S3_FULL_ACCESS]).iam_role

        self.taskDefinition = ecs.FargateTaskDefinition(self, 'task_definition', task_role=iam_role)

        # build a new docker image and push to Elastic Container Registry
        self.docker_image_asset = ecr_assets.DockerImageAsset(self, 'image_asset', directory='../src', build_args={'SCRIPTPATH' : kwargs.get('script_path')})

        # get the image from the built docker image asset
        self.docker_image = ecs.ContainerImage.from_docker_image_asset(self.docker_image_asset)

        # add container to task definition
        self.taskDefinition.add_container('container',
                                          image=self.docker_image,
                                          logging=ecs.LogDriver.aws_logs(stream_prefix='fargatetask'),
                                          environment={'sns_topic': kwargs.get('sns_topic').topic_name}
                                          )

        kwargs.get('sns_topic').grant_publish(self.taskDefinition.task_role)

        rule = events.Rule(self,
                           "rule",
                           description="trigger for fargate task",
                           enabled=True,
                           schedule=kwargs.get('schedule'),
                           targets=[
                               events_targets.EcsTask(
                                   cluster=kwargs.get('cluster'),
                                   taskDefinition=self.taskDefinition,
                                   securityGroup=kwargs.get('ecs_security_group'),
                               )]
                           )

