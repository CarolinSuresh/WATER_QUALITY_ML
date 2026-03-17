from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

rf = joblib.load('rf_classifier.pkl')
iso = joblib.load('isolation_forest.pkl')
scaler = joblib.load('scaler_features.pkl')

latest_result = {}

@app.route('/')
def home():
    return render_template("index.html")

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

    # -------- FINAL DECISION LOGIC --------

    result_text = "Good Water Quality"
    advice = "System operating normally"
    spike = "No sudden spike detected"

    # Rule-based decision (PRIMARY)
    if bod > 5 or do < 4:
        result_text = "Bad Water Quality"
        advice = "High pollution detected. Check water source."

    elif 3 < bod <= 5:
        result_text = "Moderate Water Quality"
        advice = "Water quality slightly degraded."

    # ML anomaly (ONLY WARNING)
    if iso_pred == -1:
        spike = "Sudden spike detected!"
        advice += " Possible sensor anomaly."

    # Drought override
    if waterlevel <= 5:
        result_text = "Drought Risk Detected"
        advice = "Water level critically low."

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
        "spike": spike,
        "advice": advice
    }

    return jsonify(latest_result)

@app.route('/latest')
def latest():
    return jsonify(latest_result)

if __name__ == "__main__":
    app.run(debug=True)