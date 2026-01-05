# 🏥 Silent Disease - AI-Powered Health Risk Analyzer

> **"Silent diseases are the most dangerous because they whisper before they roar."**

**Silent Disease** is a modern, AI-driven web application designed to help users identify potential health risks based on their lifestyle metrics and symptoms. By leveraging the power of **Groq's Llama-3 AI**, it provides real-time risk analysis, personalized insights, and an intelligent chat companion to guide users toward better health decisions.

---

## ✨ Key Features

### 📊 **Interactive Dashboard**

- Visualize your health trends with **Recharts**.
- Track key metrics: **Heart Rate, Sleep Quality, Stress Levels, and Blood Pressure**.
- Real-time **Risk Gauge** showing your probabilistic health risk score.

### 🤖 **AI Risk Analysis**

- Uses **Groq (Llama-3.1-8b)** to analyze your specific health data.
- Detects patterns and anomalies (e.g., high stress + low sleep).
- Recognizes conversational symptoms (e.g., "I feel symptoms of Covid") and integrates them into the medical report.

### 💬 **AI Health Companion**

- Persistent Chatbot that remembers your conversation history.
- Ask questions about symptoms, precautions, and general wellness.
- **Smart Context**: The AI knows your latest health metrics and risk score.

### � **Local Analytics & DuckDB**

- View real-time analytics powered by DuckDB (zero-cost).
- Export charts to CSV for further analysis.
- Track patient observations and health trends over time.

### 📞 **Telehealth Consults**

- Free, end-to-end encrypted video calls powered by Jitsi Meet.
- No account or login required for participants.
- Screen sharing and chat included.
- Ideal for remote consultations with patients.

### �🔐 **Secure & Personalized**

- **JWT Authentication**: Secure Login and Signup.
- **Profile Management**: Update your details, change passwords, or delete your account properly.
- **Mobile Responsive**: Fully optimized layout for desktop and mobile devices.

---

## 🛠️ Tech Stack

### **Frontend**

- **Framework**: React (Vite)
- **Language**: TypeScript
- **Styling**: Tailwind CSS (Glassmorphism UI)
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Charts**: Recharts

### **Backend**

- **Runtime**: Node.js
- **Framework**: Express.js
- **Database**: MongoDB (Mongoose)
- **AI Engine**: Groq SDK (Llama-3.1-8b-instant)
- **Auth**: JSON Web Tokens (JWT) & Bcrypt

---

## 🚀 Getting Started

Follow these instructions to set up the project locally.

### Prerequisites

- **Node.js** (v16+)
- **MongoDB** (Local or Atlas URI)
- **Groq API Key** (Get one for free at [console.groq.com](https://console.groq.com))

### 1. Clone the Repository

```bash
git clone https://github.com/haze1166/gdg-techsprint-2k26.git
cd silent-disease
```

### 2. Install Dependencies

Install dependencies for both the root, backend, and frontend.

```bash
# Root (for concurrent scripts)
npm install

# Backend
cd backend
npm install

# Frontend
cd ../frontend
npm install
```

### 3. Configure Environment Variables

Create a `.env` file in the **`backend/`** directory:

```env
PORT=5000
MONGO_URI=your_mongodb_connection_string
JWT_SECRET=your_jwt_secret_key
GROQ_API_KEY=your_groq_api_key
```

### 4. Run the Application

You can run both the backend and frontend simultaneously from the root directory:

```bash
# From the root directory
npm run dev
```

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

---

## 🧪 Local Zero-Cost Development (Hackathon)

This project can run entirely locally without cloud billing by using Docker for a local FHIR store and the Firebase Emulator Suite.

Prerequisites
- Docker Desktop
- Firebase CLI (`npm install -g firebase-tools`)

Quick start (zero-cost)

1. Start HAPI-FHIR (local FHIR server):

```bash
docker compose up -d
# HAPI-FHIR will be available at http://localhost:8080/baseR4/
```

2. Start Firebase emulators (Auth, Firestore, Functions):

```bash
# Unix
./scripts/start-emulators.sh
# Windows PowerShell
./scripts/start-emulators.ps1
```

3. Start the app (backend + frontend):

```bash
npm install
npm run dev
```

Tips
- Do not commit secrets or service account JSON files. They are ignored by `.gitignore`.
- Use `npm run emulators` from the project root to launch emulators via npm.

---

## 📊 DuckDB Analytics

### Features

- **CSV Export**: Export chart data (average heart rate, recent observations) as CSV files
- **Live Backend Integration**: Charts fetch data from `/api/analytics/duckdb` endpoint
- **Local Processing**: All analytics computed locally without cloud dependencies

### Usage

1. Ingest sample FHIR observations into DuckDB:

```bash
npm run analytics:ingest
```

2. Query and view results:

```bash
npm run analytics:query
```

3. View interactive charts in the frontend **Analysis** page with export buttons

---

## 📞 Telehealth via Jitsi Meet

### Features

- **Zero-Cost Video**: Powered by Jitsi Meet (open-source, free)
- **No Login Required**: Participants can join via a simple room name
- **End-to-End Encrypted**: Secure communication out of the box
- **Rich Features**: Screen sharing, chat, raise hand, closed captions

### Usage

1. Navigate to **Telehealth** page in the app
2. Enter your name and a unique room name (e.g., "patient-john-doe-2026")
3. Share the room name with participants
4. Start the call — participants join via https://meet.jit.si/{roomName}

### Deployment Note

For production, self-host Jitsi (see [Jitsi self-hosting guide](https://jitsi.github.io/handbook/docs/devops-guide/devops-guide-docker)) or use the free public instance at `meet.jit.si`.

---

## 🚀 Phase 2: GCP Production Deployment

Ready to move to production with Google Cloud? Follow the [**GCP Phase 2 Setup Guide**](./GCP_PHASE2_SETUP.md) to:

1. **Configure Service Account & IAM Roles** — Set up GCP authentication
2. **Enable Cloud Healthcare API** — Create FHIR dataset and stores
3. **Stream to BigQuery** — Export FHIR observations for analytics
4. **Deploy Cloud Functions** — Automate data ingestion pipelines

**Quick Start (One Command)**

```bash
# macOS/Linux
./scripts/gcp/setup-service-account.sh

# Windows PowerShell
.\scripts\gcp\setup-service-account.ps1
```

This script will:
- Create a GCP project (if needed)
- Create a service account with necessary IAM roles
- Enable required APIs (Healthcare, BigQuery, Cloud Functions, etc.)
- Generate and save service account credentials

Then update your `backend/.env` with the GCP resources (see [GCP_PHASE2_SETUP.md](./GCP_PHASE2_SETUP.md) for details).

---

## Deployment Note

For production, self-host Jitsi (see [Jitsi self-hosting guide](https://jitsi.github.io/handbook/docs/devops-guide/devops-guide-docker)) or use the free public instance at `meet.jit.si`.

---
