import aws_cdk as core
import aws_cdk.assertions as assertions

from virbo.virbo_stack import VirboStack

# example tests. To run these tests, uncomment this file along with the example
# resource in virbo/virbo_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = VirboStack(app, "virbo")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
