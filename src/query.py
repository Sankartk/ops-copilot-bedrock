from bedrock_client import invoke_titan_embedding

query = "How to fix ALB 5xx errors?"

embedding = invoke_titan_embedding(query)

print(f"Vector length: {len(embedding)}")
print("Sample vector:", embedding[:5])
