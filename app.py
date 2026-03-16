from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

rf = joblib.load('rf_classifier.pkl')
iso = joblib.load('isolation_forest.pkl')
lr = joblib.load('linear_regression_turbidity.pkl')
scaler = joblib.load('scaler_features.pkl')
scaler_lr = joblib.load('scaler_lr.pkl')

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

    X = np.array([[ph, turbidity, temperature, do, bod]])
    X_scaled = scaler.transform(X)

    rf_pred = rf.predict(X_scaled)[0]
    iso_pred = iso.predict(X_scaled)[0]

    lr_input = np.array([[ph, temperature, do, bod]])
    lr_scaled = scaler_lr.transform(lr_input)
    predicted_turbidity = lr.predict(lr_scaled)[0]

    result_text = "Good Water Quality"
    spike = "No sudden spike detected"
    advice = "System operating normally"

    if rf_pred == 1:
        result_text = "Bad Water Quality"
        advice = "Manual water quality inspection recommended"

    # Only treat anomaly as unsafe if values are actually abnormal
    if iso_pred == -1:

        if turbidity > 5 or ph < 6 or ph > 9 or bod > 6 or do < 3:
            spike = "Sudden spike detected!"
            result_text = "Bad Water Quality"
            advice = "Sensor anomaly detected. Manual inspection recommended."
        else:
            spike = "Minor sensor fluctuation detected"
            
    if waterlevel <= 5:
        result_text = "Drought Risk Detected"
        advice = "Water level critically low. Manual check required."

    latest_result = {
        "ph": ph,
        "turbidity": turbidity,
        "temperature": temperature,
        "do": round(do,2),
        "bod": round(bod,2),
        "waterlevel": waterlevel,
        "result": result_text,
        "spike": spike,
        "advice": advice,
        "predicted_turbidity": round(float(predicted_turbidity),3)
    }

    return jsonify(latest_result)

@app.route('/latest')
def latest():
    return jsonify(latest_result)

if __name__ == "__main__":
    app.run(debug=True)