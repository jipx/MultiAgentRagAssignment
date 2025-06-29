import aws_cdk as cdk
from multiagent_stack import MultiAgentStack
from monitoring_dashboard_stack import MonitoringDashboardStack

env = cdk.Environment(account="628902727523", region="ap-northeast-1")

app = cdk.App()

core_stack = MultiAgentStack(app, "MultiAgentStack")

MonitoringDashboardStack(
    app, "MonitoringDashboardStack",
    worker_lambda=core_stack.worker_lambda,
    submit_lambda=core_stack.submit_lambda,
    rag_queue=core_stack.rag_queue,
    dlq=core_stack.dead_letter_queue,
    api=core_stack.api
)
app.synth()
