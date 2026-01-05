# Phase 3: AI/ML Risk Prediction System

Advanced machine learning-powered disease early detection for Silent Disease.

## Overview

Phase 3 implements intelligent risk prediction using temporal analysis, statistical anomaly detection, and Groq AI for explainable analysis:

- **Real-time Risk Scoring** — Analyzes current vital sign trends
- **30-Day Risk Projection** — Forecasts disease progression
- **Anomaly Detection** — Identifies abnormal patterns
- **Explainable AI** — Natural language analysis via Groq
- **Alert System** — Automatic notifications for high-risk conditions

## Architecture

```
Vital Signs Data (DuckDB)
        ↓
Risk Prediction Service
    ├→ Trend Analysis (heart rate, BP, RR, glucose)
    ├→ Statistical Anomaly Detection
    ├→ Temporal Risk Projection
    └→ Groq AI Explainability
        ↓
Risk Prediction Dashboard
    ├→ Current Risk Score (0-100)
    ├→ 30-Day Forecast
    ├→ Risk Factor Breakdown
    ├→ AI Explanation
    └→ Active Alerts
```

## Backend: Risk Prediction Service

### File: `backend/services/riskPredictionService.js`

**Key Methods:**

1. **`calculateTrendRisk(observations)`** — Current risk score
   - Heart Rate: >90 bpm = +15 risk, increasing trend = +10
   - Blood Pressure: >130 mmHg = +20, >160 episodes = +15
   - Respiratory Rate: >20 = +12
   - Glucose: >125 mg/dL = +18
   - Anomalies: Each = +5 points

2. **`predictRiskProgression(observations)`** — 30-day forecast
   - Uses linear regression to project trend
   - Returns trajectory: worsening/improving/stable
   - Confidence based on data points

3. **`generateRiskAnalysis(patientData)`** — Groq AI explanation
   - Why risk score is at this level
   - Most concerning factors
   - Lifestyle recommendations
   - When to consult doctor

4. **`generateAlerts(observations)`** — Rule-based alerts
   - HIGH: Risk > 70, worsening trends
   - MODERATE: Risk factors > 15 impact
   - Severity and action flags

### Risk Thresholds

| Level | Range | Color | Action |
|-------|-------|-------|--------|
| Low Risk | 0-30 | Green | Monitor regularly |
| Moderate Risk | 31-60 | Orange | Lifestyle changes |
| High Risk | 61-100 | Red | Consult provider |

## API Endpoints

### 1. Get Current Risk Score

```bash
GET /api/risk/score/:patientId
```

**Response:**
```json
{
  "score": 62,
  "category": {
    "label": "Moderate Risk",
    "color": "#f59e0b"
  },
  "factors": [
    {
      "factor": "Elevated Heart Rate",
      "value": "94 bpm",
      "impact": 15,
      "description": "Average heart rate above normal resting range"
    },
    {
      "factor": "Rising Heart Rate Trend",
      "value": "Trending up",
      "impact": 10
    }
  ],
  "confidence": 0.85
}
```

### 2. Get 30-Day Risk Projection

```bash
GET /api/risk/prediction/:patientId
```

**Response:**
```json
{
  "prediction": "Risk projected to increase over next 30 days",
  "currentRisk": 62,
  "riskIn30Days": 72,
  "trajectory": "worsening",
  "trend": 0.33,
  "confidence": 0.85
}
```

### 3. Get Explainable AI Analysis

```bash
GET /api/risk/analysis/:patientId
```

**Response:**
```json
{
  "analysis": "Your current risk score of 62 suggests Moderate Risk. Key concerns include elevated heart rate and rising blood pressure. Consider regular exercise, stress management, and maintaining a healthy diet. Please consult with your healthcare provider for a comprehensive evaluation.",
  "riskScore": 62,
  "category": { ... },
  "factors": [ ... ],
  "projection": { ... }
}
```

### 4. Get Active Alerts

```bash
GET /api/risk/alerts/:patientId
```

**Response:**
```json
{
  "alerts": [
    {
      "severity": "MODERATE",
      "message": "Risk trend is worsening. Projected risk in 30 days: 72/100",
      "timestamp": "2026-01-05T12:00:00Z",
      "actionRequired": false
    },
    {
      "severity": "MODERATE",
      "message": "Elevated Blood Pressure: Systolic BP consistently elevated",
      "timestamp": "2026-01-05T11:45:00Z",
      "actionRequired": false
    }
  ],
  "count": 2
}
```

## Frontend: Risk Prediction Dashboard

### File: `frontend/src/pages/RiskPrediction.tsx`

**Components:**

1. **Risk Score Card** — Large display of current score/100
2. **30-Day Projection** — Trend indicator (worsening/improving/stable)
3. **Active Alerts** — High-priority items
4. **Risk Factors Breakdown** — Bar chart of impact contributions
5. **AI Analysis** — Natural language explanation from Groq
6. **Recommended Actions** — Monitor, exercise, stress management, provider consult

### Route

```
/risk → Risk Prediction Dashboard
```

### Navigation

Added to sidebar with Brain icon (🧠)

## Testing the System

### 1. Ingest Sample Data

```bash
node scripts/analytics/ingest_fhir_to_duckdb.js
```

Creates observations with various heart rates, blood pressures, etc.

### 2. Test Risk Score Endpoint

```bash
curl "http://localhost:5000/api/risk/score/user-123"
```

### 3. Test Risk Prediction

```bash
curl "http://localhost:5000/api/risk/prediction/user-123"
```

### 4. Test AI Analysis (with Groq API)

```bash
export GROQ_API_KEY="your-key"
curl "http://localhost:5000/api/risk/analysis/user-123"
```

### 5. View Dashboard

Navigate to http://localhost:5175/risk

## How It Works

### Risk Score Calculation

```
Base Risk = 10%

+ Heart Rate Analysis
  - Mean > 90 bpm: +15
  - Increasing trend: +10
  - High variance: +8

+ Blood Pressure Analysis
  - Systolic > 130 mmHg: +20
  - Episodes > 160 mmHg: +15

+ Respiratory Rate
  - Mean > 20 breaths/min: +12

+ Glucose Levels
  - Mean > 125 mg/dL: +18

+ Anomaly Detection
  - Each out-of-range value: +5

= Total Risk Score (0-100, capped)
```

### Trend Projection

1. Extract values from observations (sorted by date)
2. Calculate trend slope: (last_value - first_value) / number_of_points
3. Project 30 days: current_risk + (slope × (30 / days_of_data))
4. Classify trajectory: worsening (slope > 0.5), stable, improving

### Confidence Scoring

- < 5 observations: 30% confidence
- 5-10 observations: 60% confidence
- \> 10 observations: 90% confidence

### Groq AI Explanation

Prompts Groq with:
- Risk factors and their descriptions
- Vital sign values
- Risk trajectory

Generates natural language explanation covering:
- Why the risk score is at this level
- Most concerning factors
- Lifestyle recommendations
- When to consult a doctor

## Configuration

### Environment Variables

```bash
GROQ_API_KEY=your-groq-api-key  # Optional (falls back to mock mode)
```

### Risk Thresholds (Customizable)

Edit in `riskPredictionService.js`:

```javascript
this.THRESHOLDS = {
  LOW: { max: 30, color: '#10b981', label: 'Low Risk' },
  MODERATE: { max: 60, color: '#f59e0b', label: 'Moderate Risk' },
  HIGH: { max: 100, color: '#ef4444', label: 'High Risk' }
};
```

### LOINC Code Mapping

Update vital signs dictionary:

```javascript
this.VITAL_SIGNS = {
  'HR': '8867-4',        // Heart rate
  'SBP': '8480-6',       // Systolic blood pressure
  'DBP': '8462-4',       // Diastolic blood pressure
  'RR': '9279-1',        // Respiratory rate
  'GLUCOSE': '2345-7',   // Glucose
  'CHOLESTEROL': '2085-9' // Cholesterol
};
```

## Features

✅ Real-time vital sign trend analysis  
✅ Statistical anomaly detection  
✅ 30-day risk projection  
✅ Explainable AI (Groq)  
✅ Automatic alert generation  
✅ Confidence scoring  
✅ Risk factor breakdown  
✅ No external ML models needed (heuristic-based)  
✅ Fully offline capable (with mock Groq)  

## Limitations & Future Enhancements

### Current (Phase 3)

- Heuristic-based risk scoring (rule engines)
- Linear regression trend projection
- LOINC-based vital signs only
- Single-patient view
- No patient-provider communication

### Phase 4 Potential

- ML model training (scikit-learn, TensorFlow)
- Advanced time-series forecasting (ARIMA, Prophet)
- Multi-modal risk factors (genetics, lifestyle, EHR)
- Population health analytics
- Provider alerts and workflow integration
- Patient goal tracking and coaching

## Troubleshooting

### Risk score is always low

1. Check DuckDB has observations: `SELECT COUNT(*) FROM observations;`
2. Ensure observations have `effective_time` and `value` fields
3. Verify patient_id matches request parameter

### Groq API errors

- Confirm API key is set: `echo $GROQ_API_KEY`
- Check rate limits (10 req/min free tier)
- Fallback to mock analysis if key missing

### No alerts generated

- Risk must be > 70 for HIGH alert
- Check observation timestamps are recent
- Verify data has at least 3 points for trend detection

## References

- [Vital Signs Normal Ranges](https://my.clevelandclinic.org/health/articles/10881-vital-signs)
- [LOINC Code Database](https://loinc.org/)
- [Groq API Documentation](https://console.groq.com/docs)
- [Risk Stratification in Healthcare](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3898268/)

---

**Phase 3 Status**: ✅ Complete  
**Testing**: Manual API + Dashboard  
**Production Ready**: Yes (local), Phase 4 = ML models
