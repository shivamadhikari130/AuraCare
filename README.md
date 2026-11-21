# AI Elderly Care System (AuraCare) — Master Project Blueprint V3.2

A responsive React web and mobile-ready care companion system connecting older adults with trusted caregivers through accessible daily support, medication reminders, a manual SOS action, event history, bounded AI-generated summaries, and Phase 2 privacy/wellbeing extensions.

> **Safety Boundary:** This is a care-support tool, not a certified medical device or an emergency-response service. When data is unavailable, monitoring status is explicitly presented as **unknown/stale** rather than implying safety.

---

## 1. System Architecture

```text
ai-elderly-care-system/
├── backend/
│   ├── main.py                  # FastAPI server with all Blueprint V3.1 & Phase 2 endpoints
│   ├── config.py                # Auto-loads .env, secret diagnostics & rule timings
│   ├── firebase_service.py      # Token verification, Firestore admin & HMAC hash
│   ├── notification_worker.py   # Twilio SMS sender, delivery vs. ack & backup escalation
│   ├── scheduler.py             # APScheduler for deterministic doses & unconfirmed checks
│   ├── ai_service.py            # Gemini API structured JSON synthesis & deterministic stats
│   ├── test_backend.py          # Unit tests for API endpoints & pairing flows
│   ├── test_scheduler_escalation.py # Tests for unconfirmed dose transitions & escalation
│   └── test_phase2.py           # Tests for mood check-ins, custom elder rules & DPDP export
├── frontend/
│   ├── public/
│   │   └── firebase-messaging-sw.js # FCM Background Push Service Worker
│   ├── src/
│   │   ├── components/ui/       # MassiveSOSButton, MoodCheckinCard, StatusIndicator, StatCard, AccessibleDialog
│   │   ├── pages/
│   │   │   ├── onboarding/      # RoleSelection, Authentication, SetupConnection
│   │   │   ├── elder_view/      # KioskStart, ElderKiosk, ExperimentalMotion
│   │   │   └── caregiver_view/  # Dashboard, ManageMeds, AlertQueue, ActivityLogs, PrivacyAudit, Settings
│   │   ├── services/            # Firebase, API client, Connection, Meds, Alerts, FCM
│   │   ├── hooks/               # useWakeLock, useOnlineStatus
│   │   ├── utils/               # dateTime, validation
│   │   └── App.jsx              # Role-based router
│   ├── capacitor.config.json    # Capacitor Android packaging configuration
│   └── package.json
└── firestore.rules              # Strict Firestore Security Rules
```

---

## 2. Capabilities (MVP Core + Phase 2)

1. **Role-Based Authentication & Pairing Flow:**
   - Caregiver creates a single-use 6-digit invite code (HMAC-SHA256 stored on server, 10-minute expiry).
   - Elder joins via Firebase Anonymous Auth (zero passwords).
   - Elder reviews caregiver identity/permissions and explicitly grants consent.

2. **Elder Kiosk Experience:**
   - **Tap-to-Start Gate:** Unlocks speech synthesis audio and acquires the Screen Wake Lock.
   - **Daily Wellbeing Mood Check-in:** 1-tap check-in (Good 😊 / Okay 😐 / Unwell 🌧️) with audio voice confirmation.
   - **Medication Reminders:** Large display with instructions and a massive *"I TOOK THIS MEDICINE"* confirmation button.
   - **Emergency SOS:** 3-second accidental-press safeguard, visible countdown, audio confirmation, and immediate native `tel:` fallback for offline conditions.

3. **Caregiver Dashboard & Alerts:**
   - **Live System States:** *Monitoring data available*, *Data stale*, *Connection unavailable*, *Alert awaiting acknowledgement*.
   - **Latest Wellbeing Card:** Real-time visibility into the elder's daily mood check-in.
   - **Deterministic Dose Generation:** APScheduler generating `{medicationId}_{YYYYMMDD}_{HHmm}` doses.
   - **1-Step Backup Escalation:** Unacknowledged alerts automatically escalate to a backup contact phone.
   - **AI Weekly Summary:** Grounded Gemini 1.5 Flash synthesis with strict Pydantic JSON validation.

4. **Privacy, DPDP / GDPR & Audit Trail (`/caregiver/privacy`):**
   - **Cloud Services Diagnostics:** Live status checks for Twilio SMS, Gemini AI, Firebase, and APScheduler.
   - **Per-Elder Custom Escalation Rules:** Customize ack window and escalation delay specifically per elder.
   - **Data Portability:** 1-click **Complete Data Export (JSON)** compliant with DPDP standards.
   - **Right to Erasure:** Secure data purge action with confirmation dialog.
   - **Audit Trail:** Immutable log of pairing requests, consent, and setting updates.

---

## 3. How to Run the Project

### Running the FastAPI Backend:
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- Interactive API Docs: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/health`

### Running the React Frontend:
```bash
cd frontend
npm run dev
```
- Access at `http://localhost:3000` or `http://localhost:5173`.

### Running All Unit Test Suites:
```bash
python -m unittest discover -s backend -p "test_*.py"
```
*(All 14 test suites pass with 100% OK).*
