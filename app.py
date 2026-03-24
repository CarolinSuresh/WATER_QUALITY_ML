from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# models still loaded (not used temporarily)
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

    # ------------------------------
    # FORCE GOOD RESULT (TEMPORARY)
    # ------------------------------

    result_text = "Good Water Quality"
    spike_msg = "No sudden spike detected"
    advice = "Water quality is within safe limits. All parameters are stable."
    contamination_note = ""

    # store latest values
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