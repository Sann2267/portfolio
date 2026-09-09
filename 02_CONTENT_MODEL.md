# PHASE 02 — CONTENT MODEL

## OBJECTIVE

Create the content system that allows the portfolio to grow without rewriting UI code.

## PRINCIPLE

CONTENT != UI

A project is content.

A project page is a renderer.

## CONTENT STORAGE

Preferred approach:

- Markdown for long-form narrative content.
- YAML or JSON for structured metadata.
- Python dataclasses / validation models for runtime representation.

Do not put large project descriptions directly inside route functions or templates.

## PROJECT SCHEMA

At minimum support:

- id
- slug
- title
- category
- type
- status
- summary
- description
- role
- technologies
- AWS services
- architecture
- highlights
- challenges
- solutions
- evidence
- timeline
- repository
- demo
- documentation
- gallery
- future work

## PROJECT CONTENT

### CASE 001 — DATA SCRAPING

Title:
Indonesia Job Data Scraping System

Focus:

- Python scraping
- HTML parsing
- data extraction
- cleaning
- normalization
- structured output
- filtering
- regional categorization

Potential stack:

Python, Requests, BeautifulSoup, Regex, Pandas, JSON, CSV.

Do not invent quantitative results.

---

### CASE 002 — JOB LISTING FULLSTACK PLATFORM

Title:
Job Listing Fullstack Dashboard + API

Narrative:

The scraping/data-processing layer produces structured job data.
The fullstack platform consumes that data and exposes it through an API and interactive dashboard.

Visualize:

SCRAPING
↓
PROCESSING
↓
API
↓
DASHBOARD
↓
USER

Focus:

- backend
- API
- dashboard
- filtering
- search
- data presentation

Do not claim technologies that are not documented in the project source.

---

### CASE 003 — DEVOPS AUTOMATION

Title:
TechnoDev DevOps CI/CD Platform

Core concepts:

- AWS VPC
- public/private subnets
- EC2
- self-hosted GitHub Actions runners
- RDS PostgreSQL
- SQS
- SNS
- ECR
- Lambda
- API Gateway REST
- API Gateway WebSocket
- Amplify
- Secrets Manager
- CloudWatch
- VPC Flow Logs
- CI/CD

Architecture:

Developer
↓
GitHub
↓
GitHub Actions
↓
Self-hosted Runner
↓
Docker / ECR
↓
Lambda
↓
API Gateway

Supporting infrastructure:

RDS
SQS
SNS
CloudWatch
Secrets Manager

Source basis: the provided DevOps module.

---

### CASE 004 — CLOUD AI / DATA ANALYTICS

Title:
NusaCommerce Analytics Platform

Core layers:

INGESTION
- S3
- Kinesis

PROCESSING
- Glue
- EMR / PySpark
- Step Functions
- EventBridge

STORAGE
- S3
- DynamoDB
- Redshift

SERVING
- Lambda
- API Gateway

SECURITY
- WAF
- Secrets Manager
- SQS DLQ
- API Key

MONITORING
- CloudWatch

FRONTEND
- Amplify

Analytics:

- realtime metrics
- sales analysis
- funnel analysis
- seller scoring
- user segmentation

ML concepts:

Seller scoring:
- GMV
- completion rate
- rating
- growth rate

User segmentation:
- Recency
- Frequency
- Monetary

Do not fabricate ML accuracy values.

---

### CASE 005 — INFRASTRUCTURE AS A SERVICE

Title:
Multi-Tenant SaaS Infrastructure

Core concepts:

- Terraform
- AWS CLI
- Amazon EKS
- Kubernetes
- Helm
- Docker
- Python / Flask
- Kinesis
- EventBridge
- Lambda
- SQS
- SNS
- Grafana
- CloudWatch
- CodeDeploy
- Aurora PostgreSQL
- ElastiCache Redis

Architecture:

Virginia / us-east-1
├── Application VPC
│   ├── EKS
│   ├── ALB
│   └── Grafana / ECS Fargate
│
└── Data VPC
    ├── Aurora PostgreSQL
    └── ElastiCache Redis

Oregon / us-west-2
└── Disaster Recovery
    ├── Aurora Global Database
    └── S3 Cross-Region Replication

Network:

Application VPC
↓
VPC Peering
↓
Data VPC

Virginia
↓
Transit Gateway Peering
↓
Oregon

Multi-tenancy:

- tenant-alpha
- tenant-beta
- Kubernetes namespaces
- NetworkPolicy
- restricted Pod Security Standards
- ResourceQuota

Deployment:

Blue / Green

Target values from source documentation:

RTO <= 15 minutes
RPO <= 1 minute

Present these as project targets unless actual verification evidence exists.

---

### CASE 006 — ESP32 AWS MONITORING

Title:
Smart IoT Environment Monitoring

Core components from the supplied visual material:

- ESP32
- DHT22
- Wi-Fi
- AWS IoT Core
- MQTT
- Node-RED
- dashboard
- temperature monitoring
- humidity monitoring

Conceptual architecture:

DHT22
↓
ESP32
↓
Wi-Fi
↓
AWS IoT Core
↓
MQTT
↓
Node-RED
↓
Dashboard

Security concept:

ESP32
↓
X.509
↓
TLS
↓
AWS IoT Core

Future work must remain explicitly marked as future/planned.

Examples:

- Telegram notifications
- historical database
- automated HVAC/control integration

Do not claim those future items were already implemented.

## EXIT CRITERIA

Every project can be rendered from structured content.
Adding a new project does not require rewriting the project renderer.
