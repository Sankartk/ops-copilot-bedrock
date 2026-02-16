import boto3
import json

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

def invoke_titan_embedding(text):

    body = json.dumps({
        "inputText": text
    })

    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v1",
        body=body
    )

    result = json.loads(response['body'].read())

    return result['embedding']
