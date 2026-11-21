"""
AuraCare - AI Quiet Care System for Elders
Flask Server & Stakeholder Demonstration Hub
"""

import json
import time
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

from ai_engine import (
    AnomalyDetector,
    MedicationAdherencePredictor,
    CognitiveSentimentAnalyzer,
    HealthStabilityIndex
)

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Initialize AI Engines
anomaly_engine = AnomalyDetector()
adherence_engine = MedicationAdherencePredictor()
sentiment_engine = CognitiveSentimentAnalyzer()

# In-Memory State for Demonstration & Real-Time Sync
SYSTEM_STATE = {
    "elder_profile": {
        "name": "Rameshwar Sharma",
        "age": 76,
        "location": "Vasant Kunj, New Delhi",
        "primary_caregiver": "Sneha Sharma (Daughter, Bangalore)",
        "secondary_contact": "Dr. V. K. Gupta (Family Physician)",
        "chronic_conditions": ["Hypertension (Grade II)", "Type 2 Diabetes", "Mild Osteoarthritis"],
        "baseline_heartbeat_interval_hrs": 4
    },
    "current_status": "NORMAL", # NORMAL, ALERT_PENDING, WARNING_MISSED, SOS_EMERGENCY
    "status_label": "Active & Safe",
    "status_color": "green", # green, yellow, red
    "sos_active": False,
    "sos_timestamp": None,
    "last_interaction_time": datetime.now().strftime("%I:%M %p"),
    "last_interaction_type": "Morning Digital Heartbeat",
    "simulated_latency_min": 4.2,
    "kiosk_active_prompt": None, # None, "HEARTBEAT", "MEDICINE", "VOICE_CHECKIN"
    "active_medicine_id": None,
    "active_prompt_title": "",
    "active_prompt_message": "",
    "active_prompt_time": None,
    "voice_sentiment_history": [
        {
            "timestamp": "Yesterday, 07:30 PM",
            "transcript": "Had my tea and walked around the veranda. Knee feels slightly stiff, but feeling peaceful.",
            "sentiment_score": 0.45,
            "mood_label": "Positive & Cheerful",
            "loneliness_index": 18,
            "clarity_score": 92,
            "flags": ["Mild Joint Stiffness"]
        },
        {
            "timestamp": "Today, 08:30 AM",
            "transcript": "Good morning. Slept well after taking dinner on time. Looking forward to talking to Sneha.",
            "sentiment_score": 0.70,
            "mood_label": "Positive & Cheerful",
            "loneliness_index": 12,
            "clarity_score": 96,
            "flags": ["Stable Routine"]
        }
    ],
    "medications": [
        {
            "id": "med-1",
            "name": "Amlodipine Besylate",
            "dosage": "5 mg",
            "timing_label": "Morning (08:30 AM)",
            "scheduled_hour": 8,
            "scheduled_minute": 30,
            "status": "TAKEN", # TAKEN, PENDING, MISSED
            "last_taken": "Today, 08:32 AM",
            "total_daily_drugs": 4,
            "past_7_days_compliance": 7,
            "category": "Blood Pressure"
        },
        {
            "id": "med-2",
            "name": "Metformin Extended-Release",
            "dosage": "500 mg",
            "timing_label": "Afternoon (01:30 PM)",
            "scheduled_hour": 13,
            "scheduled_minute": 30,
            "status": "PENDING",
            "last_taken": "Yesterday, 01:35 PM",
            "total_daily_drugs": 4,
            "past_7_days_compliance": 6,
            "category": "Diabetes Management"
        },
        {
            "id": "med-3",
            "name": "Atorvastatin Calcium",
            "dosage": "10 mg",
            "timing_label": "Night (09:00 PM)",
            "scheduled_hour": 21,
            "scheduled_minute": 0,
            "status": "PENDING",
            "last_taken": "Yesterday, 09:12 PM",
            "total_daily_drugs": 4,
            "past_7_days_compliance": 5,
            "category": "Cardiovascular Health"
        }
    ],
    "activity_feed": [
        {
            "id": 1,
            "time": "08:00 AM",
            "type": "heartbeat",
            "title": "Digital Heartbeat Acknowledged",
            "desc": "Elder tapped 'I AM OK' within 2.8 minutes of prompt.",
            "badge": "success"
        },
        {
            "id": 2,
            "time": "08:32 AM",
            "type": "medication",
            "title": "Morning Dose Taken: Amlodipine 5mg",
            "desc": "Logged 2 mins after automated voice guidance.",
            "badge": "success"
        },
        {
            "id": 3,
            "time": "08:35 AM",
            "type": "ai_sentiment",
            "title": "AI Voice Check-in Processed",
            "desc": "Clarity 96%, Loneliness Index 12%. Vitality verified stable.",
            "badge": "info"
        }
    ],
    "escalation_events": []
}

def recalculate_metrics():
    """Recalculates AI scores based on current system state."""
    # Anomaly
    cur_lat = SYSTEM_STATE["simulated_latency_min"]
    anomaly_res = anomaly_engine.analyze_latency(cur_lat)
    
    # Calculate adherence average
    total_meds = len(SYSTEM_STATE["medications"])
    taken_meds = sum(1 for m in SYSTEM_STATE["medications"] if m["status"] == "TAKEN")
    adherence_pct = round((taken_meds / total_meds * 100), 1) if total_meds > 0 else 100.0

    # Sentiment average
    latest_sentiment = SYSTEM_STATE["voice_sentiment_history"][-1]["sentiment_score"] if SYSTEM_STATE["voice_sentiment_history"] else 0.5

    # Composite HSI
    hsi_score = HealthStabilityIndex.calculate(
        adherence_pct=adherence_pct,
        mean_z_score=anomaly_res["z_score"],
        sentiment_score=latest_sentiment,
        sos_active=SYSTEM_STATE["sos_active"]
    )

    # Status badge determination
    if SYSTEM_STATE["sos_active"]:
        SYSTEM_STATE["current_status"] = "SOS_EMERGENCY"
        SYSTEM_STATE["status_label"] = "EMERGENCY SOS ACTIVE"
        SYSTEM_STATE["status_color"] = "red"
    elif anomaly_res["status"] == "CRITICAL_ANOMALY":
        SYSTEM_STATE["current_status"] = "WARNING_MISSED"
        SYSTEM_STATE["status_label"] = "Critical Inactivity Detected"
        SYSTEM_STATE["status_color"] = "red"
    elif anomaly_res["status"] == "ELEVATED_RISK":
        SYSTEM_STATE["current_status"] = "ALERT_PENDING"
        SYSTEM_STATE["status_label"] = "Check-in Delayed (Elevated Risk)"
        SYSTEM_STATE["status_color"] = "yellow"
    elif any(m["status"] == "MISSED" for m in SYSTEM_STATE["medications"]):
        SYSTEM_STATE["current_status"] = "ALERT_PENDING"
        SYSTEM_STATE["status_label"] = "Missed Medication Alert"
        SYSTEM_STATE["status_color"] = "yellow"
    else:
        SYSTEM_STATE["current_status"] = "NORMAL"
        SYSTEM_STATE["status_label"] = "Active & Safe"
        SYSTEM_STATE["status_color"] = "green"

    return {
        "anomaly": anomaly_res,
        "health_stability_index": hsi_score,
        "adherence_rate": adherence_pct
    }

# ----------------- ROUTES ----------------- #

@app.route("/")
def index():
    """Main Stakeholder Portal with Interactive Dual View & Executive Command Deck."""
    return render_template("index.html")

@app.route("/dashboard")
def caregiver_dashboard():
    """Dedicated Fullscreen Caregiver Command Dashboard."""
    return render_template("dashboard.html")

@app.route("/kiosk")
def elderly_kiosk():
    """Dedicated Fullscreen Elderly Tablet Kiosk."""
    return render_template("kiosk.html")


# ----------------- REST APIS ----------------- #

@app.route("/api/status", methods=["GET"])
def get_status():
    """Returns real-time telemetric status, AI indices, and active prompts."""
    metrics = recalculate_metrics()
    
    # Calculate predictive adherence risks for all medications
    meds_with_predictions = []
    latest_distress = 0.2
    if SYSTEM_STATE["voice_sentiment_history"]:
        # Inverse of sentiment mapped to distress
        s_score = SYSTEM_STATE["voice_sentiment_history"][-1]["sentiment_score"]
        latest_distress = max(0.0, min(1.0, (1.0 - s_score) / 2.0))

    for med in SYSTEM_STATE["medications"]:
        pred = adherence_engine.predict_risk(
            drug_name=med["name"],
            scheduled_hour=med["scheduled_hour"],
            total_daily_drugs=med["total_daily_drugs"],
            past_7_days_taken=med["past_7_days_compliance"],
            distress_level=latest_distress
        )
        med_copy = dict(med)
        med_copy["ai_prediction"] = pred
        meds_with_predictions.append(med_copy)

    response_data = {
        "profile": SYSTEM_STATE["elder_profile"],
        "status": SYSTEM_STATE["current_status"],
        "status_label": SYSTEM_STATE["status_label"],
        "status_color": SYSTEM_STATE["status_color"],
        "sos_active": SYSTEM_STATE["sos_active"],
        "sos_timestamp": SYSTEM_STATE["sos_timestamp"],
        "last_interaction_time": SYSTEM_STATE["last_interaction_time"],
        "last_interaction_type": SYSTEM_STATE["last_interaction_type"],
        "kiosk_active_prompt": SYSTEM_STATE["kiosk_active_prompt"],
        "active_medicine_id": SYSTEM_STATE["active_medicine_id"],
        "active_prompt_title": SYSTEM_STATE["active_prompt_title"],
        "active_prompt_message": SYSTEM_STATE["active_prompt_message"],
        "simulated_latency_min": SYSTEM_STATE["simulated_latency_min"],
        "ai_metrics": metrics,
        "medications": meds_with_predictions,
        "sentiment_history": SYSTEM_STATE["voice_sentiment_history"],
        "activity_feed": SYSTEM_STATE["activity_feed"][-15:],
        "escalation_events": SYSTEM_STATE["escalation_events"]
    }
    return jsonify(response_data)


@app.route("/api/heartbeat/ack", methods=["POST"])
def ack_heartbeat():
    """Triggered when elder presses 'I AM OK' on the Kiosk."""
    now_str = datetime.now().strftime("%I:%M %p")
    SYSTEM_STATE["last_interaction_time"] = now_str
    SYSTEM_STATE["last_interaction_type"] = "Digital Heartbeat ('I AM OK')"
    SYSTEM_STATE["simulated_latency_min"] = 3.6
    SYSTEM_STATE["kiosk_active_prompt"] = None
    SYSTEM_STATE["active_prompt_title"] = ""
    SYSTEM_STATE["active_prompt_message"] = ""

    SYSTEM_STATE["activity_feed"].append({
        "id": len(SYSTEM_STATE["activity_feed"]) + 1,
        "time": now_str,
        "type": "heartbeat",
        "title": "Heartbeat Confirmed",
        "desc": f"Rameshwar ji tapped 'I AM OK'. Normal circadian activity verified.",
        "badge": "success"
    })

    return jsonify({"success": True, "message": "Heartbeat acknowledged"})


@app.route("/api/heartbeat/trigger", methods=["POST"])
def trigger_heartbeat_prompt():
    """Caregiver or schedule triggers a digital heartbeat check on Kiosk."""
    data = request.get_json(silent=True) or {}
    SYSTEM_STATE["kiosk_active_prompt"] = "HEARTBEAT"
    SYSTEM_STATE["active_prompt_title"] = "Namaste Rameshwar ji!"
    SYSTEM_STATE["active_prompt_message"] = "Just checking in on you. Please tap the button below."
    SYSTEM_STATE["active_prompt_time"] = datetime.now().isoformat()
    
    # If latency parameter passed
    if "latency" in data:
        SYSTEM_STATE["simulated_latency_min"] = float(data["latency"])
    else:
        SYSTEM_STATE["simulated_latency_min"] = 4.0

    return jsonify({"success": True, "message": "Heartbeat prompt sent to kiosk"})


@app.route("/api/medications/<med_id>/take", methods=["POST"])
def take_medication(med_id):
    """Marks medication as taken."""
    now_str = datetime.now().strftime("%I:%M %p")
    found = False
    med_name = ""
    for med in SYSTEM_STATE["medications"]:
        if med["id"] == med_id:
            med["status"] = "TAKEN"
            med["last_taken"] = f"Today, {now_str}"
            med_name = med["name"]
            found = True
            break
            
    if found:
        SYSTEM_STATE["last_interaction_time"] = now_str
        SYSTEM_STATE["last_interaction_type"] = f"Medication Taken ({med_name})"
        if SYSTEM_STATE["kiosk_active_prompt"] == "MEDICINE" and SYSTEM_STATE["active_medicine_id"] == med_id:
            SYSTEM_STATE["kiosk_active_prompt"] = None
            SYSTEM_STATE["active_medicine_id"] = None

        SYSTEM_STATE["activity_feed"].append({
            "id": len(SYSTEM_STATE["activity_feed"]) + 1,
            "time": now_str,
            "type": "medication",
            "title": f"Medication Taken: {med_name}",
            "desc": f"Logged on Kiosk with speech confirmation.",
            "badge": "success"
        })
        return jsonify({"success": True, "message": f"{med_name} marked as taken"})
    
    return jsonify({"success": False, "error": "Medication not found"}), 404


@app.route("/api/medications/trigger", methods=["POST"])
def trigger_medication_alert():
    """Triggers medicine prompt on the kiosk."""
    data = request.get_json(silent=True) or {}
    med_id = data.get("med_id", "med-2")
    target_med = next((m for m in SYSTEM_STATE["medications"] if m["id"] == med_id), SYSTEM_STATE["medications"][0])

    SYSTEM_STATE["kiosk_active_prompt"] = "MEDICINE"
    SYSTEM_STATE["active_medicine_id"] = target_med["id"]
    SYSTEM_STATE["active_prompt_title"] = f"Medicine Time: {target_med['name']}"
    SYSTEM_STATE["active_prompt_message"] = f"Please take {target_med['dosage']} with water, then press TAKEN."
    SYSTEM_STATE["active_prompt_time"] = datetime.now().isoformat()

    return jsonify({"success": True, "medication": target_med})


@app.route("/api/trigger-sos", methods=["POST"])
def trigger_sos():
    """Triggered by senior tapping RED SOS button."""
    now_str = datetime.now().strftime("%I:%M:%S %p")
    SYSTEM_STATE["sos_active"] = True
    SYSTEM_STATE["sos_timestamp"] = now_str
    SYSTEM_STATE["current_status"] = "SOS_EMERGENCY"
    SYSTEM_STATE["status_label"] = "EMERGENCY SOS ACTIVE"
    SYSTEM_STATE["status_color"] = "red"

    # Multi-Tier Escalation Dispatch Simulation (Twilio SMS / Push / EMS)
    escalation_log = [
        {"tier": "Tier 1", "action": "Automated Twilio SMS sent to Sneha Sharma (+91 98765 43210)", "status": "DELIVERED", "time": now_str},
        {"tier": "Tier 2", "action": "Twilio SMS dispatched to Dr. V. K. Gupta & Neighborhood Contact", "status": "DELIVERED", "time": now_str},
        {"tier": "Tier 3", "action": "High-priority push alarm triggered on Caregiver mobile app", "status": "RINGING", "time": now_str},
        {"tier": "Tier 4", "action": "Nearest Hospital Emergency Dispatch geolocated (Fortis Vasant Kunj - 2.4 km)", "status": "STANDBY", "time": now_str}
    ]
    SYSTEM_STATE["escalation_events"] = escalation_log

    SYSTEM_STATE["activity_feed"].append({
        "id": len(SYSTEM_STATE["activity_feed"]) + 1,
        "time": now_str,
        "type": "sos",
        "title": "🚨 EMERGENCY SOS TRIGGERED",
        "desc": "Senior pressed red physical emergency button on Kiosk. Autonomous escalation initiated.",
        "badge": "danger"
    })

    return jsonify({"success": True, "escalation": escalation_log})


@app.route("/api/resolve-sos", methods=["POST"])
def resolve_sos():
    """Caregiver or Senior cancels/resolves SOS."""
    now_str = datetime.now().strftime("%I:%M %p")
    SYSTEM_STATE["sos_active"] = False
    SYSTEM_STATE["sos_timestamp"] = None
    SYSTEM_STATE["escalation_events"] = []
    
    SYSTEM_STATE["activity_feed"].append({
        "id": len(SYSTEM_STATE["activity_feed"]) + 1,
        "time": now_str,
        "type": "info",
        "title": "SOS Emergency Resolved",
        "desc": "Caregiver confirmed senior's safety. System returned to normal monitoring.",
        "badge": "info"
    })
    recalculate_metrics()
    return jsonify({"success": True, "message": "SOS emergency resolved"})


@app.route("/api/sentiment/checkin", methods=["POST"])
def submit_voice_checkin():
    """
    Receives voice transcript from Kiosk or Simulator,
    runs NLP Sentiment & Cognitive Vitality Analysis, and updates clinical log.
    """
    data = request.get_json(silent=True) or {}
    transcript = data.get("transcript", "I am feeling quite good today, had my breakfast.")
    
    result = sentiment_engine.analyze(transcript)
    now_str = datetime.now().strftime("Today, %I:%M %p")
    
    entry = {
        "timestamp": now_str,
        "transcript": transcript,
        "sentiment_score": result["sentiment_score"],
        "mood_label": result["mood_label"],
        "loneliness_index": result["loneliness_index"],
        "clarity_score": result["cognitive_clarity_score"],
        "flags": result["flags"],
        "summary_for_family": result["summary_for_family"],
        "engine": result.get("engine", "AuraCare NLP")
    }
    
    SYSTEM_STATE["voice_sentiment_history"].append(entry)
    SYSTEM_STATE["last_interaction_time"] = datetime.now().strftime("%I:%M %p")
    SYSTEM_STATE["last_interaction_type"] = "Voice Vitality Check-in"
    SYSTEM_STATE["kiosk_active_prompt"] = None

    SYSTEM_STATE["activity_feed"].append({
        "id": len(SYSTEM_STATE["activity_feed"]) + 1,
        "time": datetime.now().strftime("%I:%M %p"),
        "type": "ai_sentiment",
        "title": f"AI Voice Check-in: {result['mood_label']}",
        "desc": f"Cognitive Clarity: {result['cognitive_clarity_score']}%, Loneliness: {result['loneliness_index']}%.",
        "badge": "info"
    })

    return jsonify({"success": True, "analysis": entry})


@app.route("/api/simulate-latency", methods=["POST"])
def simulate_latency():
    """Adjusts latency to demonstrate Anomaly Detection Engine to stakeholders."""
    data = request.get_json(silent=True) or {}
    latency = float(data.get("latency", 4.0))
    SYSTEM_STATE["simulated_latency_min"] = latency
    
    res = recalculate_metrics()
    return jsonify({"success": True, "metrics": res})


@app.route("/api/stakeholder-summary", methods=["GET"])
def get_stakeholder_summary():
    """
    Returns executive stakeholder data:
    - UX research citations (HelpAge India, NCD burden, ADL challenge)
    - Total cost avoidance (Zero hardware vs $800 IoT sensor suite)
    - AI architecture specifications
    """
    return jsonify({
        "project_name": "AuraCare AI Quiet Care System",
        "target_demographic": "Indian Elderly Population (140M+ by 2026, 71% feature phones/tablets)",
        "clinical_foundation": {
            "ncd_burden_stat": "54% elders report 2+ chronic non-communicable diseases (HelpAge India 2024)",
            "adl_challenges_stat": "52% face difficulties with activities of daily living",
            "family_dependency_stat": "94% depend on family care with increasing geographical separation"
        },
        "solution_paradigm": "Quiet Care: Monitor quietly through software triggers, intervene meaningfully, preserve dignity with zero wearable friction.",
        "ai_innovations": [
            {
                "engine": "Circadian Anomaly Detector",
                "method": "Dynamic Z-Score & Moving Window Baseline",
                "value": "Flags silent falls or incapacitation within 15-30m without intrusive cameras."
            },
            {
                "engine": "Predictive Non-Adherence Model",
                "method": "Multivariate Behavioral Risk Scoring",
                "value": "Prevents hypertensive spikes and missed diabetic doses before they occur."
            },
            {
                "engine": "Cognitive Vitality & NLP Check-in",
                "method": "Gemini 1.5 Flash + Geriatric Sentiment Heuristics",
                "value": "Continuously tracks early cognitive decline and loneliness trajectories."
            }
        ],
        "roi_and_scalability": {
            "hardware_cost": "$0 (Runs on existing Android tablet or smartphone browser)",
            "setup_time": "< 3 minutes",
            "battery_impact": "Negligible (Browser native event loops)",
            "telecom_integration": "Twilio SMS & Automated Voice IVR fallback"
        }
    })


if __name__ == "__main__":
    print("=" * 60)
    print("  AuraCare - AI Quiet Care System for Elders")
    print("  Executive Stakeholder Demonstration Portal")
    print("  Serving at: http://localhost:5000")
    print("  Elderly Kiosk View: http://localhost:5000/kiosk")
    print("  Caregiver Dashboard: http://localhost:5000/dashboard")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=True)
