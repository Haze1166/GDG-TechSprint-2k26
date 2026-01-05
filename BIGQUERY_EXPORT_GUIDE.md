# BigQuery Export & Analytics Setup Guide

This guide covers streaming FHIR observations to BigQuery and running analytics queries.

## Architecture Overview

```
Health Data (Pub/Sub) 
    ↓
Cloud Function (fhirIngestion)
    ├→ Transform to FHIR
    ├→ POST to Healthcare API FHIR Store
    └→ Stream to BigQuery
```

## Prerequisites

- Completed Phase 2 setup (service account, APIs enabled)
- BigQuery dataset created (`health_analytics` or custom)
- Cloud Function deployed (see Phase 2 Deploy guide)

## Step 1: Create BigQuery Dataset & Tables

Run these commands to set up BigQuery:

```bash
export PROJECT_ID=$(gcloud config get-value project)
export BQ_DATASET="health_analytics"
export BQ_REGION="US"

# Create BigQuery dataset
bq mk --dataset \
  --location=$BQ_REGION \
  --description="Health analytics and FHIR data exports" \
  $BQ_DATASET

# Create observations table
bq mk --table \
  $BQ_DATASET.observations \
  backend/schemas/observations_schema.json

# Create patients table
bq mk --table \
  $BQ_DATASET.patients \
  backend/schemas/patients_schema.json

echo "✓ BigQuery tables created"
```

## Step 2: Configure Cloud Function Environment Variables

Create `.env.yaml` for Cloud Function deployment:

```yaml
# functions/.env.yaml
GCP_PROJECT_ID: "your-project-id"
GCP_REGION: "us-central1"
GCP_FHIR_DATASET: "fhir_data"
GCP_FHIR_STORE: "silent_disease_fhir"
GCP_BQ_DATASET: "health_analytics"
```

Deploy with environment variables:

```bash
gcloud functions deploy fhirIngestion \
  --region=us-central1 \
  --runtime=nodejs22 \
  --trigger-topic=health-data-ingestion \
  --env-vars-file=functions/.env.yaml \
  --service-account=silent-disease-sa@PROJECT_ID.iam.gserviceaccount.com
```

## Step 3: Test Data Flow

### Publish a test health data event:

```bash
gcloud pubsub topics publish health-data-ingestion \
  --message '{
    "userId": "patient-123",
    "metric": "8867-4",
    "value": 72,
    "unit": "beats/min",
    "timestamp": "2026-01-05T12:00:00Z"
  }'
```

### Check Cloud Function logs:

```bash
gcloud functions logs read fhirIngestion --region=us-central1 --limit=50
```

### Query BigQuery to verify data arrived:

```bash
bq query --use_legacy_sql=false '
  SELECT *
  FROM `'$PROJECT_ID'.'$BQ_DATASET'.observations`
  WHERE patient_id = "patient-123"
  LIMIT 10
'
```

## Analytics Queries

### 1. Average Vital Signs per Patient

```sql
SELECT
  patient_id,
  observation_display,
  COUNT(*) as measurement_count,
  AVG(value) as avg_value,
  MIN(value) as min_value,
  MAX(value) as max_value,
  STDDEV(value) as stddev_value,
  MAX(ingested_time) as last_measurement
FROM `PROJECT_ID.health_analytics.observations`
WHERE observation_type = '8867-4' -- Heart rate LOINC code
  AND ingested_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY patient_id, observation_display
ORDER BY avg_value DESC;
```

### 2. Risk Indicators (High BP + High HR)

```sql
SELECT
  hr.patient_id,
  hr.avg_hr,
  bp.avg_sbp,
  bp.avg_dbp,
  CASE
    WHEN hr.avg_hr > 100 AND bp.avg_sbp > 140 THEN 'HIGH_RISK'
    WHEN hr.avg_hr > 90 AND bp.avg_sbp > 130 THEN 'MODERATE_RISK'
    ELSE 'LOW_RISK'
  END as risk_level,
  hr.last_measurement
FROM (
  SELECT
    patient_id,
    AVG(value) as avg_hr,
    MAX(ingested_time) as last_measurement
  FROM `PROJECT_ID.health_analytics.observations`
  WHERE observation_type = '8867-4'
    AND ingested_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  GROUP BY patient_id
) as hr
JOIN (
  SELECT
    patient_id,
    AVG(CASE WHEN observation_type = '8480-6' THEN value END) as avg_sbp,
    AVG(CASE WHEN observation_type = '8462-4' THEN value END) as avg_dbp
  FROM `PROJECT_ID.health_analytics.observations`
  WHERE observation_type IN ('8480-6', '8462-4')
    AND ingested_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  GROUP BY patient_id
) as bp
ON hr.patient_id = bp.patient_id
ORDER BY risk_level DESC, avg_hr DESC;
```

### 3. Trend Analysis (Time Series)

```sql
SELECT
  DATE(effective_time) as date,
  patient_id,
  observation_display,
  AVG(value) as daily_avg,
  MIN(value) as daily_min,
  MAX(value) as daily_max
FROM `PROJECT_ID.health_analytics.observations`
WHERE patient_id = 'patient-123'
  AND observation_type = '8867-4'
GROUP BY date, patient_id, observation_display
ORDER BY date DESC;
```

### 4. Anomaly Detection (Values > 2 SD from mean)

```sql
WITH stats AS (
  SELECT
    observation_type,
    AVG(value) as mean_value,
    STDDEV_POP(value) as stddev_value
  FROM `PROJECT_ID.health_analytics.observations`
  WHERE ingested_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  GROUP BY observation_type
)
SELECT
  obs.patient_id,
  obs.observation_display,
  obs.value,
  stats.mean_value,
  stats.stddev_value,
  ROUND(ABS(obs.value - stats.mean_value) / stats.stddev_value, 2) as z_score,
  obs.effective_time,
  'ANOMALY' as flag
FROM `PROJECT_ID.health_analytics.observations` as obs
JOIN stats ON obs.observation_type = stats.observation_type
WHERE ABS(obs.value - stats.mean_value) > 2 * stats.stddev_value
  AND obs.ingested_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
ORDER BY z_score DESC;
```

## Scheduled Queries (Optional)

Set up automatic analytics exports using BigQuery scheduled queries:

### Create scheduled query for daily summary:

```bash
bq mk --transfer_config \
  --project_id=$PROJECT_ID \
  --data_source=scheduled_query \
  --display_name="Daily Health Summary" \
  --target_dataset=$BQ_DATASET \
  --schedule="every day 08:00" \
  --params='{
    "query":"SELECT DATE(effective_time) as date, patient_id, observation_display, COUNT(*) as count, AVG(value) as avg_value FROM `'$PROJECT_ID'.'$BQ_DATASET'.observations` WHERE effective_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY) GROUP BY date, patient_id, observation_display",
    "destination_table_name_template":"daily_summary_{run_date}",
    "write_disposition":"WRITE_TRUNCATE"
  }'
```

## Exporting Data

### Export observations to Cloud Storage (for backup/analysis):

```bash
bq extract \
  --destination_format CSV \
  $BQ_DATASET.observations \
  gs://your-bucket/health-analytics/observations_*.csv
```

### Export to BigQuery for external tools (Looker, Tableau, etc.):

1. Set up Public dataset: `bq update --set_iam_policy=iam_policy.json $BQ_DATASET`
2. Share dataset with BI tools
3. Connect external tools to BigQuery datasets

## Cost Optimization

### Free Tier (Limits)

- 1 TB query/month (free)
- 10 GB storage (free)
- Streaming inserts: $6.25 per GB/month after free tier

### Cost Reduction

```bash
# Partition observations table by date (reduces query costs)
bq update --set_table_expiration 7776000 \
  --time_partitioning_field effective_time \
  $BQ_DATASET.observations

# Set up table expiration (delete old data automatically)
bq update --expiration 2592000 $BQ_DATASET.observations  # 30 days
```

## Troubleshooting

### Cloud Function not streaming to BigQuery

1. Check Cloud Function logs: `gcloud functions logs read fhirIngestion --region=us-central1`
2. Verify service account has `bigquery.dataEditor` role
3. Confirm BigQuery dataset exists: `bq ls --project_id=$PROJECT_ID`

### BigQuery quota exceeded

- Reduce query frequency
- Use scheduled queries instead of real-time
- Partition tables by date
- Archive old data to Cloud Storage

### Slow queries

1. Add indexes on frequently queried columns
2. Use table partitioning (by date/patient_id)
3. Use clustering: `bq update --clustering_fields patient_id,observation_type $BQ_DATASET.observations`

## References

- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [FHIR LOINC Code Reference](https://loinc.org/)
- [Vital Signs LOINC Codes](https://loinc.org/system/components?parentId=LP180729-7)

---

**Common LOINC Codes**

| Code | Display | Unit |
|------|---------|------|
| 8867-4 | Heart rate | beats/min |
| 8480-6 | Systolic blood pressure | mmHg |
| 8462-4 | Diastolic blood pressure | mmHg |
| 2085-9 | Cholesterol | mg/dL |
| 2345-7 | Glucose | mg/dL |
| 3141-9 | Body weight | kg |
| 8302-2 | Body height | cm |
