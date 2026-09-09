## The Case

TechnoDev, the fictional e-commerce company in this competition module, is moving to
microservices and needs automated delivery. The AWS Academy Learner Lab does not offer
CodePipeline or CodeBuild, so the pipeline has to be built from GitHub Actions with runners that
live inside a private AWS network and still reach GitHub, ECR, Lambda, and RDS.

The module's ten tasks cover the network, the runners, the data layer, the container registry
and Lambda functions, both API Gateways, the Amplify frontend, the CI and CD workflows, secrets
and monitoring, and an end-to-end verification.

## Key Findings

- **Private runners are the security boundary.** Both runners sit in private subnets without
  public IPs. Administration goes through Session Manager, package downloads through the NAT
  Gateway, and the runner service is registered as a system service so it survives reboots.
- **Security groups, not passwords, gate the database.** RDS accepts port 5432 only from the
  Lambda and runner security groups. It is Multi-AZ, encrypted, backed up for seven days, and
  never publicly accessible.
- **Create the dead-letter queue first.** Both application queues carry a redrive policy to it
  from the start, so a message that fails three times is isolated rather than lost.
- **Greedy proxy routes keep the API small.** Three resources with `{proxy+}` children forward
  every nested path to the right function through Lambda proxy integration. The read-only
  product catalogue is served by the order function, which already holds the database
  connection.
- **Secrets move out of environment variables.** The database password is stored once in
  Secrets Manager and read at runtime by all four functions.

## Infrastructure

VPC `devops-vpc` (210.0.0.0/16) with two public and two private subnets across `us-west-2a`
and `us-west-2b`, an Internet Gateway, one NAT Gateway with an Elastic IP, and separate public
and private route tables. Two EC2 runners (Ubuntu 24.04 LTS, t3.medium, LabRole instance
profile) with Docker Engine, AWS CLI v2, Git, and the GitHub Actions runner labelled
`self-hosted, linux, x64`.

Four ECR repositories with image scanning on push hold the container images built from the
provided Dockerfiles on the Lambda Python 3.11 base image. Four Lambda functions run from those
images inside the private subnets with the `devops-sg-lambda` security group.

## Deployment

`ci.yaml` runs on pull requests against `main`: flake8 on each handler, a Docker build per
service, an import check of every handler inside its container, and presence checks for the
frontend and SQL schema. `deploy.yaml` runs on push to `main`: it logs in to ECR, builds and
pushes the four images tagged `latest` and with the commit SHA, updates each function's image,
zips and deploys the frontend to Amplify through a manual deployment, and smoke-tests the REST
API. Both target `runs-on: self-hosted`. The workflow definitions were supplied by the module;
the work was provisioning everything they depend on and getting them green on the runners.

## Data

RDS PostgreSQL 15 (`devops-db`, db.t3.small, 20 GB gp3) initialised with the provided
`schema.sql` from a runner over the private network. SQS standard queues `devops-orders-queue`
(30 s visibility) and `devops-notifications-queue` (60 s visibility) with `devops-dlq`
(14-day retention) as the redrive target; an event source mapping feeds the notification worker
in batches of ten. SNS topics `devops-notifications` and `devops-alerts` with confirmed e-mail
subscriptions.

## Security

Four security groups by least privilege, VPC-attached Lambda functions, Secrets Manager for the
database credentials, and a Cognito user pool (e-mail as username, password policy, hosted UI)
whose JWTs are validated by an API Gateway authorizer on the REST API.

## Observability

CloudWatch dashboard `devops-dashboard` with Lambda invocations, errors, and p50/p99 duration,
RDS CPU utilisation and connections, and SQS queue depth. VPC Flow Logs capture ALL traffic to
the log group `/aws/vpc/devops-vpc/flowlogs`, so both ACCEPT and REJECT records are available
for troubleshooting.

## Result

The three workflows (runner verification, CI, CD) are in the public repository and target the
self-hosted runners. The module's acceptance test is a CRUD sequence through the REST API
(create user, create order, update status, verify the SNS notification, cascade delete) and a
WebSocket sequence (ping, get_orders, status broadcast to a second client, disconnect cleanup).
Execution logs from the lab session were not kept, so the outcome is documented by the module
requirements rather than by retained evidence.
