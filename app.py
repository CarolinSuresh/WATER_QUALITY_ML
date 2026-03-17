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

    # NEW PARAMETERS
    mq = data["Ammonia (MQ)"]
    tds = data["TDS (ppm)"]

    X = np.array([[ph, turbidity, temperature, do, bod]])
    X_scaled = scaler.transform(X)

    rf_pred = rf.predict(X_scaled)[0]
    iso_pred = iso.predict(X_scaled)[0]

    result_text = "Good Water Quality"
    spike = "No sudden spike detected"
    advice = "System operating normally"

    if rf_pred == 1:
        result_text = "Bad Water Quality"
        advice = "Manual water quality inspection recommended"

    if iso_pred == -1:
        spike = "Sudden spike detected!"
        result_text = "Bad Water Quality"
        advice = "Sensor anomaly detected. Manual inspection recommended."

    if waterlevel <= 5:
        result_text = "Drought Risk Detected"
        advice = "Water level critically low. Manual check required."

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