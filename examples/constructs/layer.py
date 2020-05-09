from aws_cdk import (
    aws_lambda as lambda_,
    aws_ssm as ssm,
    core,
)

from datetime import datetime
import os.path
dirname = os.path.dirname(__file__)


class LayerConstruct(core.Construct):
    def __init__(self, app: core.Construct, id: str, **kwargs) -> None:
        super().__init__(app, id)

        runtimes = [lambda_.Runtime.PYTHON_3_7]

        parameter_name = 'layer-' + os.path.basename(kwargs.get('layer_code'))

        self.layer_version = lambda_.LayerVersion(self,
                                                  'layer',
                                                  code=lambda_.Code.from_asset(kwargs.get('layer_code')),
                                                  compatible_runtimes=runtimes,
                                                  description="deployed: {}".format(datetime.now().isoformat())
                                                  )

        ssm_parameter = ssm.StringParameter(self,
                                            'VersionArn',
                                            parameter_name=parameter_name,
                                            string_value=self.layer_version.layer_version_arn
                                            )

        self.parameter_name = parameter_name
