from aws_cdk import (
    aws_events as events,
    aws_lambda as lambda_,
    aws_events_targets as targets,
    aws_sns as sns,
    aws_ssm as ssm,
    aws_lambda_destinations as destinations,
    core,
)

from datetime import datetime

import os.path
dirname = os.path.dirname(__file__)


class LambdaConstruct(core.Construct):
    def __init__(self, app: core.Construct, id: str, **kwargs) -> None:
        super().__init__(app, id)

        environmental_variables = {'PYTHONPATH': '/opt'} # access layers

        layer_list = []
        for layer_parameter_name in kwargs.get('layers'):
            baseLayerArn = ssm.StringParameter.value_for_string_parameter(self, layer_parameter_name)
            layer = lambda_.LayerVersion.from_layer_version_arn(self, layer_parameter_name, baseLayerArn)
            layer_list.append(layer)

        if 'environmental_variables' in kwargs:
            environmental_variables.update(kwargs.get('environmental_variables'))

        self.lambdaFn = lambda_.Function(
            self,
            "Singleton",
            code=lambda_.Code.asset(os.path.join(dirname, kwargs.get('handler_code'))),
            handler="lambda_function.lambda_handler",
            timeout=core.Duration.seconds(300),
            runtime=lambda_.Runtime.PYTHON_3_7,
            environment=environmental_variables,
            role=kwargs.get('iam_role'),
            layers=layer_list,
            on_failure=destinations.SnsDestination(kwargs.get('sns_topic_error')),
        )

        rule = events.Rule(
            self,
            "Rule",
            schedule=events.Schedule.expression(kwargs.get('cron_expression'))
        )

        rule.add_target(targets.LambdaFunction(self.lambdaFn))
