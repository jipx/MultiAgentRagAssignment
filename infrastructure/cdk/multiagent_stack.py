from pathlib import Path
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_sqs as sqs,
    aws_iam as iam,
    aws_lambda_event_sources as lambda_event_sources,
    aws_dynamodb as dynamodb,
    aws_cloudwatch as cw,
    aws_logs as logs,
    Duration,
)
from constructs import Construct


class MultiAgentStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        model_name = self.node.try_get_context("model_name") or "Claude"
        model_id = self.node.try_get_context("model_id") or "anthropic.claude-v2"
        kb_id = self.node.try_get_context("kb_id") or "owasp-kb-001"
        rag_endpoint = self.node.try_get_context("rag_endpoint_url") or "https://bedrock-runtime.ap-southeast-1.amazonaws.com"

        dead_letter_queue = sqs.Queue(
            self, "RAGDLQ",
            queue_name="RAGWorkerDLQ",
            retention_period=Duration.days(14)
        )

        rag_queue = sqs.Queue(
            self, "RAGQueryQueue",
            queue_name="RAGQueryQueue",
            visibility_timeout=Duration.seconds(50),
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=3,
                queue=dead_letter_queue
            )
        )

        response_table = dynamodb.Table(
            self, "ResponseTable",
            partition_key={"name": "request_id", "type": dynamodb.AttributeType.STRING},
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        submit_lambda = _lambda.Function(
            self, "SubmitLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset(str(Path(__file__).resolve().parents[2] / "backend" / "lambda_submit")),
            environment={"QUEUE_URL": rag_queue.queue_url},
        )
        rag_queue.grant_send_messages(submit_lambda)

        worker_lambda = _lambda.Function(
            self, "WorkerLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(50),
            code=_lambda.Code.from_asset(str(Path(__file__).resolve().parents[2] / "backend" / "lambda_worker")),
            environment={
                "MODEL_NAME": model_name,
                "MODEL_ID": model_id,
                "KB_ID": kb_id,
                "RAG_ENDPOINT_URL": rag_endpoint,
                "TABLE_NAME": response_table.table_name
            }
        )
        worker_lambda.add_event_source(lambda_event_sources.SqsEventSource(rag_queue, batch_size=1))
        response_table.grant_write_data(worker_lambda)
        worker_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["bedrock:*"],
            resources=["*"]
        ))

        get_answer_lambda = _lambda.Function(
            self, "GetAnswerLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset(str(Path(__file__).resolve().parents[2] / "backend" / "lambda_get_answer")),
            environment={"TABLE_NAME": response_table.table_name}
        )
        response_table.grant_read_data(get_answer_lambda)

        get_history_lambda = _lambda.Function(
            self, "GetHistoryLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset(str(Path(__file__).resolve().parents[2] / "backend" / "lambda_get_history")),
            environment={"TABLE_NAME": response_table.table_name}
        )
        response_table.grant_read_data(get_history_lambda)

        log_group = logs.LogGroup(self, "ApiGatewayAccessLogs")
        api_role = iam.Role(
            self, "ApiGatewayCloudWatchRole",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonAPIGatewayPushToCloudWatchLogs")]
        )

        api = apigateway.RestApi(self, "RAGMultiAgentAPI",
            rest_api_name="RAG Multi-Agent API",
            cloud_watch_role=True,
            deploy_options=apigateway.StageOptions(
                logging_level=apigateway.MethodLoggingLevel.INFO,
                data_trace_enabled=True,
                access_log_destination=apigateway.LogGroupLogDestination(log_group),
                access_log_format=apigateway.AccessLogFormat.json_with_standard_fields(
                    caller=True,
                    http_method=True,
                    ip=True,
                    protocol=True,
                    request_time=True,
                    resource_path=True,
                    response_length=True,
                    status=True,
                    user=True
                ),
                throttling_rate_limit=10,
                throttling_burst_limit=5
            )
        )

        ask_resource = api.root.add_resource("ask")
        ask_resource.add_method("POST", apigateway.LambdaIntegration(submit_lambda))
        ask_resource.add_cors_preflight(
            allow_origins=apigateway.Cors.ALL_ORIGINS,
            allow_methods=["POST"]
        )

        get_answer_resource = api.root.add_resource("get-answer")
        get_answer_resource.add_method("GET", apigateway.LambdaIntegration(get_answer_lambda))
        get_answer_resource.add_cors_preflight(
            allow_origins=apigateway.Cors.ALL_ORIGINS,
            allow_methods=["GET"]
        )

        cw.Alarm(
            self, "DLQAlarm",
            metric=dead_letter_queue.metric_approximate_number_of_messages_visible(),
            threshold=1,
            evaluation_periods=1,
            alarm_description="DLQ has messages pending!",
            comparison_operator=cw.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD
        )
