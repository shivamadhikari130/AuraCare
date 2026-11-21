# AI Elderly Care System - Master Project Blueprint
**Target Platform:** Google Antigravity (AI Coding Agent)
**Project Type:** Pure Web Application (Zero Hardware/IoT)
**Tech Stack:** 
- Frontend: HTML5, CSS3, Vanilla JavaScript
- Backend: Python (Flask)
- Database: Firebase (Firestore)
- External APIs: Google Gemini API (Sentiment/Text Analysis), Twilio API (SMS Alerts), Web Speech API (Browser Native)

---

## 1. Project Context & Objectives
**Agent Directive:** You are acting as the Lead Architect and Full-Stack Developer to build a complete, dual-interface web application. This system relies purely on software logic, time-based triggers, and user interaction patterns to simulate health and safety monitoring for senior citizens.

There are two primary users and interfaces:
1. **The Elderly Kiosk:** A permanently open web view on a tablet for the senior citizen.
2. **The Caregiver Dashboard:** A responsive web portal for the family member to monitor status and schedule alerts.

---

## 2. UI/UX Specifications

### A. The Elderly Kiosk (Frontend)
*   **Design Philosophy:** Maximum accessibility, zero learning curve.
*   **Visual Rules:** 
    *   Extra-large typography (minimum `24px` for body text, `48px` for headings).
    *   High contrast colors (e.g., Deep navy blue background `#0a192f` with bright yellow `#ffb703` or white text).
    *   No complex navigation, scrolling, or dropdowns. Single-screen operation.
*   **Core UI Elements:**
    *   **Time/Date Display:** Huge digital clock at the top.
    *   **Dynamic Central Action Area:** Remains blank until a trigger occurs (e.g., Medicine time, Check-in time).
    *   **Action Buttons:** Massive, touch-friendly buttons (e.g., "I AM OK" or "MEDICINE TAKEN").
    *   **Persistent SOS Button:** A 100% width, bright red `bottom-fixed` button that says "EMERGENCY SOS".
    *   **Voice Indicator:** A large microphone icon showing when the app is listening/speaking.

### B. The Caregiver Dashboard (Frontend)
*   **Design Philosophy:** Modern, data-dense, clean admin panel.
*   **Visual Rules:** 
    *   Clean white/grey background with modern card-based layout.
    *   Responsive design (must work perfectly on desktop and mobile).
*   **Core UI Elements:**
    *   **Live Status Header:** A prominent badge showing current status (e.g., `🟢 Active & Safe`, `🟡 Missed Medicine`, `🔴 Unresponsive`).
    *   **Medication Scheduler:** A form to input `Medicine Name`, `Dosage`, and `Time`.
    *   **Activity Log Board:** A scrolling feed of recent events (e.g., "9:00 AM - Amlodipine Taken", "11:30 AM - Ping Acknowledged").
    *   **AI Weekly Summary Card:** A text box where the backend pushes the Gemini AI-generated weekly health and mood summary.

---

## 3. Core Features & "Sensorless" Logic (Backend/JS Integration)

### Feature 1: The Digital Heartbeat (Inactivity Monitor)
*   **Logic:** Caregiver schedules 3 random check-in times (e.g., 10 AM, 2 PM, 6 PM).
*   **Execution:** At the scheduled time, the Kiosk UI flashes, plays an alarm tone, and shows a massive "I AM OK" button.
*   **Escalation:** 
    *   `T = 0 mins`: Gentle visual/audio prompt.
    *   `T = 15 mins` (No response): Louder audio prompt.
    *   `T = 30 mins` (No response): Backend triggers Twilio API to send SMS to Caregiver: *"Alert: No activity detected for 30 minutes."*

### Feature 2: Smart Medication Tracker
*   **Logic:** Backend checks current time against Firestore medication schedule.
*   **Execution:** Triggers full-screen alert and Web Speech API reads: *"Time to take [Medicine Name]"*.
*   **Escalation:** If the "TAKEN" button is not pressed within 30 minutes, log as "Missed" and update Caregiver Dashboard instantly.

### Feature 3: Voice-Based Sentiment Check-in
*   **Logic:** Once a day, the Kiosk asks, *"How are you feeling today?"*
*   **Execution:** JS Web Speech API captures the audio, converts to text, and sends to Flask backend.
*   **AI Processing:** Flask sends the text to Google Gemini API with a system prompt to analyze distress/mood. Returns a JSON like `{"mood": "positive", "distress": false}`. Saves to Firestore.

---

## 4. Step-by-Step Implementation Plan for Antigravity

**Agent Directive:** Execute these phases sequentially. Present diffs/code for review at the end of each phase before moving to the next.

### Phase 1: Boilerplate & Firebase Setup
1.  Initialize a Python Flask project structure.
2.  Set up Firebase Admin SDK in Flask.
3.  Define Firestore database schemas (Collections: `users`, `medications`, `event_logs`).
4.  Serve basic `kiosk.html` and `dashboard.html` templates.

### Phase 2: Caregiver Dashboard (CRUD & UI)
1.  Build the dashboard UI using modern CSS (Grid/Flexbox).
2.  Create REST endpoints in Flask to add/delete medications and fetch logs.
3.  Implement real-time Firestore listeners in JS so the dashboard updates instantly without refresh.

### Phase 3: Elderly Kiosk (UI & Web Speech API)
1.  Build the high-contrast, accessible Kiosk UI.
2.  Implement the Web Speech API (SpeechSynthesis for talking, SpeechRecognition for listening).
3.  Wire the persistent RED SOS button to a Flask `/trigger-sos` endpoint.

### Phase 4: Core Automation Logic (The Engine)
1.  Implement the backend interval checker (or JS frontend scheduler) for Medication and Digital Heartbeat triggers.
2.  Build the 30-minute escalation logic.
3.  Integrate the Twilio API on the backend to fire actual SMS messages on SOS or Timeout.

### Phase 5: Gemini AI Integration
1.  Integrate Google Gemini API in Flask.
2.  Create an endpoint `/analyze-sentiment` that accepts text from the Kiosk check-in.
3.  Generate the "Weekly Summary" logic that pulls the last 7 days of logs and asks Gemini to summarize them for the dashboard.

---

## 5. Automated Testing Directives (Browser Subagent)
Once code is written, use the Browser Subagent to perform the following end-to-end tests:
1.  **Test 1 (SOS):** Open `kiosk.html`, click the Red SOS button. Verify the Flask console logs the Twilio trigger, and verify `dashboard.html` status changes to Red/Alert.
2.  **Test 2 (Medicine):** Add a medicine in `dashboard.html` scheduled for 1 minute from now. Wait on `kiosk.html` until the prompt appears. Click "TAKEN". Verify the dashboard logs it as completed.
