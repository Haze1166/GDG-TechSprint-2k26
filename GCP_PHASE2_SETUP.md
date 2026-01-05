# Phase 2: GCP Healthcare API Integration Setup Guide

This guide walks you through configuring Google Cloud Platform (GCP) to enable FHIR data ingestion, transformation, and streaming to BigQuery.

## Prerequisites

- A Google Cloud account (free tier available)
- `gcloud` CLI installed ([install here](https://cloud.google.com/sdk/docs/install))
- Billing enabled on your GCP project (note: Google Cloud Healthcare API has free tier limits)

## Step 1: Create a GCP Project

```bash
# Set your project name
export PROJECT_NAME="silent-disease"
export PROJECT_ID="silent-disease-$(date +%s)"

# Create the project
gcloud projects create $PROJECT_ID --name "$PROJECT_NAME"

# Set as active project
gcloud config set project $PROJECT_ID

# Enable billing (visit https://console.cloud.google.com/billing to set up)
echo "Visit https://console.cloud.google.com/billing and link a billing account"
```

## Step 2: Enable Required APIs

```bash
gcloud services enable \
  healthcareapi.googleapis.com \
  cloudresourcemanager.googleapis.com \
  iam.googleapis.com \
  cloudfunctions.googleapis.com \
  cloudbuild.googleapis.com \
  cloudscheduler.googleapis.com \
  bigquery.googleapis.com \
  pubsub.googleapis.com
```

## Step 3: Create Service Account & IAM Roles

Run the helper script:

```bash
# From repo root
./scripts/gcp/setup-service-account.sh
```

Or manually:

```bash
# Create service account
gcloud iam service-accounts create silent-disease-sa \
  --display-name="Silent Disease FHIR Service Account"

# Set PROJECT_ID
export PROJECT_ID=$(gcloud config get-value project)
export SA_EMAIL="silent-disease-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant Healthcare API admin role (for FHIR store access)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/healthcare.admin"

# Grant BigQuery admin role (for data export)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/bigquery.admin"

# Grant Cloud Functions admin role (for deployment)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/cloudfunctions.admin"

# Grant Pub/Sub editor role (for triggering functions)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/pubsub.editor"

# Create and download key
gcloud iam service-accounts keys create ./backend/gcp-service-account-key.json \
  --iam-account=$SA_EMAIL

echo "✅ Service account created: $SA_EMAIL"
echo "✅ Key saved to: ./backend/gcp-service-account-key.json"
```

## Step 4: Create FHIR Dataset & Store

```bash
export REGION="us-central1"
export DATASET_ID="fhir_data"
export FHIR_STORE_ID="silent_disease_fhir"

# Create Healthcare dataset
gcloud healthcare datasets create $DATASET_ID \
  --location=$REGION

# Create FHIR store
gcloud healthcare fhir-stores create $FHIR_STORE_ID \
  --dataset=$DATASET_ID \
  --location=$REGION

echo "✅ FHIR Store created: projects/$PROJECT_ID/locations/$REGION/datasets/$DATASET_ID/fhirStores/$FHIR_STORE_ID"
```

## Step 5: Create BigQuery Dataset for Analytics

```bash
export BQ_DATASET="health_analytics"

# Create BigQuery dataset
bq mk --dataset \
  --location=$REGION \
  --description="Health analytics and FHIR data exports" \
  $BQ_DATASET

echo "✅ BigQuery dataset created: $BQ_DATASET"
```

## Step 6: Configure Environment Variables

Update `backend/.env` with your GCP resources:

```env
# GCP Configuration
GCP_PROJECT_ID=silent-disease-xxxxx
GCP_REGION=us-central1
GCP_FHIR_DATASET=fhir_data
GCP_FHIR_STORE=silent_disease_fhir
GCP_BQ_DATASET=health_analytics
GOOGLE_APPLICATION_CREDENTIALS=./gcp-service-account-key.json
```

## Step 7: Deploy Cloud Function

The Cloud Function will be triggered by Pub/Sub when health data arrives and will:
1. Transform FHIR observations
2. POST to Cloud Healthcare API
3. Stream results to BigQuery

```bash
# Deploy function
gcloud functions deploy fhirIngestion \
  --region=$REGION \
  --runtime nodejs22 \
  --trigger-topic health-data-ingestion \
  --entry-point fhirIngestion \
  --service-account=$SA_EMAIL \
  --env-vars-file ./functions/.env.yaml \
  --source ./functions

echo "✅ Cloud Function deployed"
```

## Step 8: Test the Integration

```bash
# Publish a test health data event
gcloud pubsub topics publish health-data-ingestion \
  --message '{"userId":"test-user","heartRate":72,"bloodPressure":"120/80"}'

# Check function logs
gcloud functions logs read fhirIngestion --region=$REGION --limit=50
```

## Cost Considerations

### Free Tier

- Google Cloud Healthcare API: 1,000 API calls/month (free)
- BigQuery: 1 TB query/month (free), 10 GB storage (free)
- Cloud Functions: 2 million invocations/month (free)
- Pub/Sub: 10 GB/month (free)

### Estimated Costs (Beyond Free Tier)

- Healthcare API: $0.50/1000 calls
- BigQuery: $6.25/TB after 1 TB/month free
- Cloud Functions: $0.40/million invocations

## Cleanup

To avoid unexpected charges, delete resources when done:

```bash
# Delete Cloud Function
gcloud functions delete fhirIngestion --region=$REGION

# Delete FHIR store
gcloud healthcare fhir-stores delete $FHIR_STORE_ID \
  --dataset=$DATASET_ID \
  --location=$REGION

# Delete BigQuery dataset
bq rm -d -r -f $BQ_DATASET

# Delete dataset
gcloud healthcare datasets delete $DATASET_ID --location=$REGION

# Delete service account
gcloud iam service-accounts delete $SA_EMAIL

# Delete project (if no longer needed)
gcloud projects delete $PROJECT_ID
```

## Troubleshooting

### "Permission denied" errors
- Verify service account has necessary IAM roles (run Step 3 again)
- Check `GOOGLE_APPLICATION_CREDENTIALS` path is correct

### Cloud Function fails to deploy
- Ensure Cloud Build API is enabled: `gcloud services enable cloudbuild.googleapis.com`
- Check function syntax: `npm test` in `functions/` directory

### BigQuery export not working
- Verify FHIR store has BigQuery export enabled
- Check service account has `bigquery.dataEditor` role

## Next Steps

After Phase 2 setup:
1. Uncomment production-ready code in `functions/fhirIngestion/index.js`
2. Deploy Cloud Function to production
3. Set up Cloud Scheduler for periodic data exports
4. Configure BigQuery scheduled queries for analytics

## References

- [Google Cloud Healthcare API Docs](https://cloud.google.com/healthcare-api/docs)
- [FHIR Implementation Guide](https://www.hl7.org/fhir/overview.html)
- [BigQuery Export Guide](https://cloud.google.com/healthcare-api/docs/how-tos/fhir-bigquery)
