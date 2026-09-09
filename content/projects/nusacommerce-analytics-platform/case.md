## The Case

NusaCommerce, the fictional marketplace in this competition module, has transaction, event,
shipment, and seller data but no infrastructure that turns it into answers. Hourly GMV, top
sellers, the conversion funnel, and regional distribution are computed by hand over days.

The module asks for a complete platform in five hours: automated ingestion, ETL, ML feature
engineering, lakehouse storage, and a REST API with a monitoring dashboard, all under the
`nusa-` prefix in `us-east-1`. The application code was supplied; the infrastructure, the
orchestration, and every integration between the pieces were the work.

## Key Findings

- **Infrastructure as a stack, updated in place.** Buckets, the DynamoDB table, the Kinesis
  stream, and the Firehose delivery stream were added to one CloudFormation template across
  successive stack updates rather than clicked together.
- **Two paths, one lake.** Batch CSVs land in S3 and become partitioned Parquet through Glue;
  streamed events go through Kinesis into DynamoDB for the last 48 hours and into S3 through
  Firehose for history. Redshift Spectrum and Athena read the same lake.
- **Orchestration is where the bugs were.** The Step Functions definition arrived with five
  intentional faults: wrong transitions, wrong resource names, missing S3 path segments, and
  incomplete error handling. Some failed at creation, some only when a state ran.
- **Protect the API in layers.** API keys and a usage plan first, then a WAF Web ACL with a
  rate-based block, SQL-injection managed rules, and the common rule set in count mode so that
  legitimate traffic is logged rather than blocked.
- **ML as features, not claims.** Seller scores and RFM segments are computed by PySpark on EMR,
  written as Parquet, and loaded into Redshift. No accuracy figure is reported because none was
  measured.

## Infrastructure

`nusa-foundation-stack` defines the raw, processed, and curated buckets (SSE-S3, Block Public
Access, lifecycle to Glacier after 30 days and expiry after 120), the `nusa-realtime-metrics`
DynamoDB table (PAY_PER_REQUEST, composite key, 48-hour TTL, `MetricTypeIndex`, streams), the
`nusa-events-stream` Kinesis stream, and the `nusa-firehose-delivery` stream. An EMR 7.x cluster
with one master and two core `m5.xlarge` nodes runs the Spark steps.

## Data

Glue database `nusa-database` with tables for transactions, user events, shipments, and
sellers; crawler `nusa-crawler-raw` over the processed prefixes and `nusa-crawler-curated`
on demand. Three Glue ETL jobs validate rows (null keys, non-positive amounts), deduplicate,
standardise strings, and write year/month/day-partitioned Parquet. Athena workgroup
`nusa-workgroup` holds five named queries. Redshift `nusa-warehouse` has `staging`,
`analytics`, and `reporting` schemas; COPY loads Parquet from S3 and
`reporting.mv_daily_summary` joins transactions and shipments per province.

Seller scoring weights four dimensions (90-day GMV 40%, completion rate 30%, average rating
20%, month-over-month growth 10%) after min-max scaling. User segmentation builds RFM features
(days since last purchase, completed transactions in 90 days, spend in 90 days), standardises
them, splits into quartiles, and labels CHAMPION, LOYAL, AT_RISK, and DORMANT.

## Application

Six Lambda functions on Python 3.12: `nusa-stream-processor` (Kinesis batches to DynamoDB with
atomic ADD), `nusa-api-handler` (routes `/metrics/realtime` to DynamoDB, `/analytics/sales` to
Redshift, `/analytics/funnel` to an Athena named query, `/analytics/recommendations` to the
analytics schema), and the pipeline utilities `nusa-redshift-loader`, `nusa-view-refresher`,
`nusa-validate-input`, and `nusa-ml-loader`. The handlers were provided; deployment,
environment, event source mappings, DLQs, and the runtime switch to Secrets Manager were
configured here.

## Deployment

EventBridge rule `nusa-s3-trigger` matches `Object Created` events on the raw bucket's
transactions, shipments, and sellers prefixes and starts `nusa-pipeline-orchestrator` with a
transformed input. The state machine runs the three Glue jobs in parallel, the crawler, then
two parallel branches (Redshift load and view refresh; seller scoring then user segmentation on
EMR), loads the ML features, and publishes success or failure to SNS. The dashboard is a static
page deployed to Amplify by manual deployment and configured with the API base URL and key.

## Security

API keys with usage plan `nusa-usage-plan`; WAF Web ACL `nusa-api-waf` with `NusaRateLimitRule`
(block above 100 requests per five minutes with a JSON 429 body), `NusaSQLInjectionRule`
(managed SQLi set, block), and `NusaCommonRule` (managed common set, count). Redshift
credentials live in `nusa/redshift/credentials` with a resource policy limited to LabRole and
are fetched at runtime by the four Redshift-facing functions. Dead-letter queues for the API
handler and the stream processor receive events after three failed attempts.

## Observability

CloudWatch dashboard `nusa-pipeline-dashboard` with Lambda invocations and errors, Kinesis
incoming records, Step Functions executions succeeded and failed, DynamoDB consumed capacity,
and Glue job elapsed time. Alarms on each DLQ notify `nusa-alerts` when a message stays visible
for two consecutive five-minute periods.

## Result

The foundation and core stacks exist as CloudFormation templates in the practice repository,
and the module's verification steps (row counts in Athena and Redshift, a Step Functions
execution to SUCCEEDED, a Kinesis test event loop, the five endpoints with and without an API
key, a WAF rate-limit test) define what "done" meant. Logs from the lab session were not
retained, so results are documented by the module rather than by kept evidence.
