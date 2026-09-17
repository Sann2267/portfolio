
---

# 2. `PORTFOLIO_DATA.md`

File kedua ini saya sarankan menjadi **single source of truth untuk isi portofolio**. Ini yang membuat websitenya benar-benar “elastic”.

```md
# PORTFOLIO DATA

This file contains the factual content structure for the portfolio.

The UI must consume this content instead of hardcoding project descriptions.

---

# PROFILE

Name:
[YOUR NAME]

Role:

Cloud Infrastructure / DevOps / Backend / Data / IoT

Short Description:

A technical developer focused on building cloud infrastructure,
automation systems, backend services, data pipelines, and IoT systems.

Long Description:

I enjoy understanding how systems work from infrastructure,
application, data, and networking layers, then turning those
components into reliable and maintainable systems.

Primary Focus:

- Cloud Infrastructure
- DevOps
- Backend Development
- Data Engineering
- IoT
- Automation

---

# PROJECTS

## PROJECT 001

id: scraping-data

title:
Indonesia Job Data Scraping System

category:
Data Engineering

type:
Data Scraping

status:
completed

summary:

A Python-based data extraction system for collecting and processing
job listing information from online sources.

technologies:

- Python
- Requests
- BeautifulSoup
- Regex
- Pandas
- JSON
- CSV

capabilities:

- Data extraction
- HTML parsing
- Data cleaning
- Data normalization
- Structured extraction
- Job listing processing
- Filtering
- Region categorization

pipeline:

SOURCE
↓
SCRAPER
↓
RAW DATA
↓
PARSER
↓
CLEANING
↓
NORMALIZATION
↓
STRUCTURED DATA

---

## PROJECT 002

id: job-dashboard

title:
Job Listing Fullstack Dashboard

category:
Fullstack Development

type:
Web Platform

status:
completed

summary:

A fullstack platform for presenting and managing structured job listing
data through an interactive dashboard and API.

architecture:

SCRAPING
↓
DATA PROCESSING
↓
API
↓
FULLSTACK DASHBOARD
↓
USER

technologies:

- Frontend
- Backend
- REST API
- Database / structured data
- Search
- Filtering

focus:

- Fullstack architecture
- API design
- Data presentation
- Search
- Filtering
- Dashboard

---

## PROJECT 003

id: devops-automation

title:
TechnoDev DevOps CI/CD Platform

category:
DevOps

type:
Cloud Infrastructure

status:
completed

summary:

A production-oriented AWS DevOps platform designed around automated
CI/CD, secure networking, containerized serverless services,
observability, and event-driven communication.

services:

- Amazon VPC
- Amazon EC2
- Amazon RDS PostgreSQL
- Amazon SQS
- Amazon SNS
- Amazon ECR
- AWS Lambda
- API Gateway REST
- API Gateway WebSocket
- AWS Amplify
- AWS Secrets Manager
- Amazon CloudWatch
- VPC Flow Logs
- GitHub Actions

architecture:

Developer
↓
GitHub
↓
GitHub Actions
↓
Self-hosted Runner
↓
Docker
↓
Amazon ECR
↓
AWS Lambda
↓
API Gateway

Supporting:

RDS
SQS
SNS
CloudWatch
Secrets Manager

key_concepts:

- CI/CD
- Self-hosted runners
- Private subnets
- Event-driven architecture
- REST API
- WebSocket
- Containerized Lambda
- Observability
- Secret management
- Network monitoring

---

## PROJECT 004

id: cloud-ai-analytics

title:
NusaCommerce Analytics Platform

category:
Cloud AI / Data Analytics

type:
Data Engineering

status:
completed

summary:

An end-to-end AWS data platform for transforming raw operational data
into analytical insights and machine-learning driven segmentation.

architecture_layers:

INGESTION
- S3
- Kinesis

PROCESSING
- AWS Glue
- Amazon EMR
- PySpark
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

analytics:

- Daily GMV
- Sales analytics
- Conversion funnel
- Regional analysis
- Seller scoring
- User segmentation

ml:

Seller Scoring:
- GMV
- Completion Rate
- Rating
- Growth Rate

User Segmentation:
- Recency
- Frequency
- Monetary

architecture:

RAW DATA
↓
INGESTION
↓
ETL
↓
PROCESSED DATA
↓
WAREHOUSE
↓
ML FEATURE ENGINEERING
↓
API
↓
ANALYTICS DASHBOARD

---

## PROJECT 005

id: iaas

title:
Multi-Tenant SaaS Infrastructure

category:
Infrastructure as a Service

type:
Cloud Infrastructure

status:
completed

summary:

A multi-tenant SaaS infrastructure deployed across AWS regions
with Kubernetes orchestration, isolated workloads, event-driven
architecture, automated deployment, observability, and disaster recovery.

primary_region:
us-east-1

dr_region:
us-west-2

technology:

- Terraform
- AWS CLI
- Kubernetes
- EKS
- Helm
- Docker
- Python
- Flask
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

architecture:

AWS
|
+-- Virginia
|   |
|   +-- Application VPC
|   |   |
|   |   +-- EKS
|   |   +-- ALB
|   |   +-- Grafana
|   |
|   +-- Data VPC
|       |
|       +-- Aurora PostgreSQL
|       +-- ElastiCache Redis
|
+-- Oregon
    |
    +-- Disaster Recovery

network:

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

multi_tenancy:

tenant-alpha
tenant-beta

isolation:

- Kubernetes namespaces
- NetworkPolicy
- Pod Security Standards
- Resource Quotas

deployment:

Blue / Green deployment

disaster_recovery:

- Aurora Global Database
- S3 Cross-Region Replication
- Cross-region connectivity
- Automated failover workflow

target:

RTO <= 15 minutes
RPO <= 1 minute

---

## PROJECT 006

id: iot-esp32-aws

title:
Smart IoT Environment Monitoring

category:
IoT / Cloud

type:
IoT Monitoring

status:
completed

summary:

A smart environment monitoring system using ESP32 and DHT22 to
collect temperature and humidity data and transmit telemetry to
AWS for real-time monitoring.

hardware:

- ESP32
- DHT22

cloud:

- AWS IoT Core

communication:

- MQTT
- TLS / X.509

monitoring:

- Node-RED
- Dashboard
- Real-time sensor visualization
- Historical charts
- Alert concept

architecture:

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

security:

ESP32
↓
X.509
↓
TLS
↓
AWS IoT Core

future_development:

- Telegram notifications
- Historical database
- Automatic HVAC control

IMPORTANT:

Future development must be displayed as planned / future work,
not as an already implemented feature.