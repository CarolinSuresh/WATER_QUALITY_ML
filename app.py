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

    # SENSOR VALUES
    ph = data.get("pH",0)
    turbidity = data.get("Turbidity (NTU)",0)
    temperature = data.get("Temperature (°C)",0)
    do = data.get("DO (mg/L)",0)
    bod = data.get("BOD (mg/L)",0)

    # WATER LEVEL FIX
    waterlevel = data.get("WaterLevel", data.get("waterlevel", data.get("water_level",0)))

    # -----------------------
    # ML FEATURES
    # -----------------------

    X = np.array([[ph, turbidity, temperature, do, bod]])
    X_scaled = scaler.transform(X)

    rf_pred = rf.predict(X_scaled)[0]
    iso_pred = iso.predict(X_scaled)[0]

    lr_input = np.array([[ph, temperature, do, bod]])
    lr_scaled = scaler_lr.transform(lr_input)
    predicted_turbidity = lr.predict(lr_scaled)[0]

    # -----------------------
    # NORMAL ML RESULT
    # -----------------------

    result_text = "Water is Safe" if rf_pred == 0 else "Water is Unsafe"
    spike = "No sudden spike detected"

    if iso_pred == -1:
        result_text = "Water is Unsafe"
        spike = "Sudden spike detected!"

    # -----------------------
    # DROUGHT CONDITION
    # -----------------------

    if waterlevel <= 0:
        result_text = "Drought Predicted"

    latest_result = {
        "ph": ph,
        "turbidity": turbidity,
        "temperature": temperature,
        "do": do,
        "bod": bod,
        "waterlevel": waterlevel,
        "result": result_text,
        "spike": spike,
        "predicted_turbidity": round(float(predicted_turbidity),3)
    }

    return jsonify(latest_result)


@app.route('/latest')
def latest():
    return jsonify(latest_result)


if __name__ == "__main__":
    app.run(debug=True)