import os
from bedrock_client import invoke_titan_embedding

DATA_PATH = "../data"

for file in os.listdir(DATA_PATH):

    with open(f"{DATA_PATH}/{file}", "r") as f:
        content = f.read()

    vector = invoke_titan_embedding(content)

    print(f"Ingested {file} → vector size {len(vector)}")
