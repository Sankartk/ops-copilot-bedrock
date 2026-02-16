# FILE: blog/linkedin-article.md

# Building an AI Ops Copilot using Amazon Bedrock Knowledge Bases

I recently built a personal project to explore how Generative AI can assist DevOps teams during production incidents.

The idea was simple:

Operational runbooks are often scattered across S3, Confluence, and internal docs. During incidents, engineers waste time searching for the right troubleshooting steps.

So I built an AI assistant that answers incident questions grounded in real runbooks.

---

## Architecture

S3 Runbooks → Bedrock Knowledge Base → Titan Embeddings → OpenSearch Vector Store → RetrieveAndGenerate → Streamlit UI

---

## Key Features

* Semantic search over runbooks
* Grounded answers with citations
* Serverless architecture
* Deployable via AWS managed services

---

## Example Queries

* How do I rollback ECS deployment?
* ALB 5xx troubleshooting steps?
* RDS CPU spike mitigation?

---

## Learnings

* Knowledge Bases simplify RAG implementation significantly
* Embeddings model selection impacts sync permissions
* Vector store cost must be managed for personal projects

---

## Next Steps

* Slack bot integration
* Auto-remediation actions
* Terraform deployment

---

Happy to connect with others exploring GenAI + DevOps on AWS.
