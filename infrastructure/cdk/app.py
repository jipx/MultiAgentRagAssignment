import aws_cdk as cdk
from multiagent_stack import MultiAgentStack

env = cdk.Environment(account="628902727523", region="ap-northeast-1")

app = cdk.App()
MultiAgentStack(app, "MultiAgentStack", env=env)
app.synth()
