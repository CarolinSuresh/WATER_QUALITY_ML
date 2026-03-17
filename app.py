from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

rf = joblib.load('rf_classifier.pkl')
iso = joblib.load('isolation_forest.pkl')
scaler = joblib.load('scaler_features.pkl')

latest_result = {}
previous_values = None   # ✅ stores previous readings

@app.route('/')
def home():
    return render_template("index.html")

# ✅ SPIKE DETECTION FUNCTION
def detect_spike(current):
    global previous_values

    thresholds = [0.5, 20, 2, 50, 5, 50]  
    # pH, turbidity, temp, MQ, water level, TDS

    if previous_values is None:
        previous_values = current
        return False

    spike = False

    for i in range(len(current)):
        if abs(current[i] - previous_values[i]) > thresholds[i]:
            spike = True
            break

    previous_values = current
    return spike


@app.route('/predict', methods=['POST'])
def predict():

    global latest_result

    data = request.json

    ph = data["pH"]
    turbidity = data["Turbidity (NTU)"]
    temperature = data["Temperature (°C)"]
    do = data["DO (mg/L)"]
    bod = data["BOD (mg/L)"]
    waterlevel = data["WaterLevel"]
    mq = data["Ammonia (MQ)"]
    tds = data["TDS (ppm)"]

    # ML input
    X = np.array([[ph, turbidity, temperature, do, bod]])
    X_scaled = scaler.transform(X)

    rf_pred = rf.predict(X_scaled)[0]
    iso_pred = iso.predict(X_scaled)[0]

    # -------- DEFAULT --------
    result_text = "Good Water Quality"
    advice = "System operating normally"
    spike_msg = "No sudden spike detected"
    contamination_note = ""

    # -------- RULE-BASED DECISION --------
    if bod > 5 or do < 4:
        result_text = "Bad Water Quality"
        advice = "High pollution detected. Check water source."

        if bod > 6 or turbidity > 100:
            contamination_note = "⚠️ High possibility of E. coli or sewage contamination due to organic pollution."

    elif 3 < bod <= 5:
        result_text = "Moderate Water Quality"
        advice = "Water quality slightly degraded."

    # -------- DROUGHT --------
    if waterlevel <= 5:
        result_text = "Drought Risk Detected"
        advice = "Water level critically low."

    # -------- SPIKE DETECTION (FINAL CORRECT) --------
    current_values = [ph, turbidity, temperature, mq, waterlevel, tds]

    if detect_spike(current_values):
        spike_msg = "Sudden spike detected!"
        advice += " Sudden parameter variation observed."

    # -------- FINAL OUTPUT --------
    latest_result = {
        "ph": ph,
        "turbidity": turbidity,
        "temperature": temperature,
        "do": round(do, 2),
        "bod": round(bod, 2),
        "waterlevel": waterlevel,
        "mq": mq,
        "tds": tds,
        "result": result_text,
        "spike": spike_msg,
        "advice": advice,
        "contamination": contamination_note
    }

    return jsonify(latest_result)


@app.route('/latest')
def latest():
    return jsonify(latest_result)


if __name__ == "__main__":
    app.run(debug=True)