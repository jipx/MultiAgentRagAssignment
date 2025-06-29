from aws_cdk import Stack, aws_cloudwatch as cw
from constructs import Construct

class MonitoringDashboardStack(Stack):
    def __init__(self, scope: Construct, id: str, *, worker_lambda, submit_lambda, rag_queue, dlq, api, **kwargs):
        super().__init__(scope, id, **kwargs)

        dashboard = cw.Dashboard(self, "Dashboard", dashboard_name="RAGMonitoringDashboard")

        dashboard.add_widgets(
            cw.GraphWidget(
                title="Worker Lambda Duration",
                left=[worker_lambda.metric_duration()]
            ),
            cw.GraphWidget(
                title="Submit Lambda Invocations",
                left=[submit_lambda.metric_invocations()]
            ),
            cw.GraphWidget(
                title="RAG Queue Length",
                left=[rag_queue.metric_approximate_number_of_messages_visible()]
            ),
            cw.GraphWidget(
                title="DLQ Messages",
                left=[dlq.metric_approximate_number_of_messages_visible()]
            ),
            cw.GraphWidget(
                title="API Latency",
                left=[api.metric_latency()]
            )
        )

        cw.Alarm(self, "DLQAlarm",
            metric=dlq.metric_approximate_number_of_messages_visible(),
            threshold=1,
            evaluation_periods=1,
            alarm_description="Messages stuck in DLQ!",
            comparison_operator=cw.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD
        )
