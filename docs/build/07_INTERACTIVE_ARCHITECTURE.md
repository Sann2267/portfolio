# PHASE 07 — INTERACTIVE ARCHITECTURE

## OBJECTIVE

Create a reusable architecture visualization engine.

## DATA-DRIVEN DIAGRAM

Each project may define:

```yaml
architecture:
  groups: []
  nodes: []
  edges: []
```

Do not manually create an unrelated SVG implementation for every project.

## NODE SUPPORT

Each node should support:

- id
- label
- service
- category
- status
- group
- description
- related cases

## EDGE SUPPORT

Each edge should support:

- source
- target
- label
- direction
- protocol / transport when relevant

## INTERACTIONS

On hover:

- highlight node
- dim unrelated nodes
- show short explanation

On click:

- focus node
- show details
- highlight connections
- optionally link to related technology/project evidence

Do not require JavaScript for basic diagram readability.

The fallback must remain readable as a static representation.

## DIAGRAMS TO SUPPORT

### DevOps

Developer
→ GitHub
→ GitHub Actions
→ Self-hosted Runner
→ ECR
→ Lambda
→ API Gateway

Supporting:

RDS / SQS / SNS / CloudWatch / Secrets Manager

### Cloud AI

S3 / Kinesis
→ Glue / EMR / Step Functions / EventBridge
→ Redshift / DynamoDB / S3
→ Lambda / API Gateway
→ Dashboard

Security:

WAF / Secrets Manager / SQS DLQ

### IaaS

Application VPC
↔ VPC Peering
↔ Data VPC

Virginia
↔ Transit Gateway Peering
↔ Oregon DR

### IoT

DHT22
→ ESP32
→ Wi-Fi
→ AWS IoT Core
→ MQTT
→ Node-RED
→ Dashboard

## EXIT CRITERIA

Architecture diagrams are reusable, interactive, data-driven, responsive, and readable without interaction.
