## The Case

A SaaS platform has to serve several tenants from one Kubernetes cluster while keeping their
workloads apart, keep its data tier away from its compute tier, survive a regional failure,
and ship new versions without downtime. This module hands over a repository where every layer,
from Terraform modules to Helm values to Lambda code, contains deliberate faults or missing
pieces, and asks for a working platform built only with `aws`, `terraform`, `helm`, and
`kubectl`. Anything created by hand in the console loses points.

## Key Findings

- **Isolation is layered.** Two VPCs separate compute from data; VPC peering with explicit
  routes is the only path between them. Inside the cluster, each tenant namespace carries a
  restricted Pod Security Standard, a ResourceQuota, and a NetworkPolicy that allows ingress
  only from its own namespace and `kube-system` and egress only to DNS, the data VPC, and
  HTTPS.
- **Fix the module, not the plan.** All Terraform corrections live under `modules/`; `main.tf`
  stays untouched. State sits in a versioned S3 bucket so a bad apply can be rolled back.
- **Events are the audit log.** Every user create, update, or delete is published to Kinesis by
  the API, forwarded by a Lambda to a custom EventBridge bus, and fanned out to SNS, an SQS
  queue with a dead-letter queue, and a DynamoDB table with TTL.
- **Disaster recovery is automated, not a runbook.** A CloudWatch alarm on primary health
  drives an EventBridge rule and a Lambda that initiates the Aurora Global Database failover
  and notifies through SNS. The targets set by the module are an RTO of 15 minutes and an RPO
  of 1 minute.

## Networking

Application VPC 10.10.0.0/16 with public subnets (10.10.1.0/24, 10.10.2.0/24) for the ALB and
private subnets (10.10.10.0/24, 10.10.11.0/24) for EKS nodes and Grafana. Data VPC 10.20.0.0/16
with isolated subnets for Aurora and Redis plus private subnets. DR VPC 10.30.0.0/16 in
us-west-2. Peering `cloudtech-peering-app-data` with DNS resolution; Transit Gateways
`cloudtech-tgw-2026` and `cloudtech-tgw-secondary` peered across regions with routes in both
directions. Security groups: ALB open on 80 and 443, EKS pods reachable only from the ALB group
on 8080 and 3000, Aurora on 5432 and Redis on 6379 only from 10.10.0.0/16.

## Infrastructure

EKS 1.31 cluster `cloudtech-eks-cluster` created by Terraform with two or more nodes, the AWS
Load Balancer Controller so the ALB can target pods, three ECR repositories (`cloudtech-api-app`
on 8080 with Prometheus metrics on 9100, `cloudtech-fe-app` on 3000, `cloudtech-monitoring`
reserved for DR), and Grafana OSS as an ECS Fargate service (512 CPU, 1024 MB) with no public
IP and its image pulled through the NAT Gateway.

## Application

Two Flask 3.1 services on Python 3.13 deployed with Helm into both tenant namespaces:
`cloudtech-api` (2 replicas, 256m CPU, 512Mi) and `cloudtech-fe` (1 replica, 128m CPU, 256Mi).
Database credentials come from the Kubernetes Secret `cloudtech-db-secret` through
`secretKeyRef`; the ConfigMap `cloudtech-config` carries the Redis host and Grafana URL; the
API has CORS enabled and publishes to the `KINESIS_STREAM` named in its environment.

## Deployment

CodeDeploy application `cloudtech-eks-app` with a canary strategy: 10% of traffic to the new
version for five minutes, then 100% if no errors, with automatic rollback when the ALB health
check fails. Deployments are triggered from the CLI.

## Security

Kubernetes Secrets rather than plaintext values, restricted Pod Security Standards, no security
group open to 0.0.0.0/0 except the ALB on 80 and 443, Block Public Access on every S3 bucket,
and `publicly_accessible = false` on Aurora. The module closes with a security audit against
that checklist.

## Observability

Grafana OSS on ECS Fargate as an internal service, CloudWatch alarm `cloudtech-api-error-rate`
on 5xx responses, log group `/cloudtech/ecs/grafana`, and the frontend dashboard that reports
API, Aurora, Redis, Kinesis, EKS, Grafana, Transit Gateway, and peering status.

## Result

The module's end-to-end verification requires a CRUD lifecycle in both tenants (create with an
event to Kinesis, read from Aurora across the peering, update with an audit record in DynamoDB,
delete), every dashboard indicator green, and the security checklist satisfied. The RTO and RPO
figures are the module's targets, not measured values. Evidence from the lab session was not
retained.
