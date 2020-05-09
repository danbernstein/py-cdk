from aws_cdk import (
    aws_sns as sns,
    aws_sns_subscriptions as sns_subscriptions,
    core,
)


class SnsTopicConstruct(core.Construct):
    def __init__(self, app: core.Construct, id: str, **kwargs) -> None:
        super().__init__(app, id)
        self.topic_name = kwargs.get('topic_name')
        self.email_addresses = kwargs.get('email_addresses')

        self.topic = sns.Topic(self, 'Topic', topic_name=self.topic_name, display_name=self.topic_name)

        for email_address in self.email_addresses:
            self.topic.add_subscription(sns_subscriptions.EmailSubscription(email_address=email_address, ))

