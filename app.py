from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# ---------------------------
# Load ML models and scalers
rf = joblib.load('rf_classifier.pkl')
iso = joblib.load('isolation_forest.pkl')
lr = joblib.load('linear_regression_turbidity.pkl')
scaler = joblib.load('scaler_features.pkl')
scaler_lr = joblib.load('scaler_lr.pkl')

# ---------------------------
@app.route('/')
def home():
    return render_template('index.html')

# ---------------------------
@app.route('/predict', methods=['POST'])
def predict():
    try:

        data = request.json

        ph = data['pH']
        turbidity = data['Turbidity (NTU)']
        temperature = data['Temperature (°C)']
        do = data['DO (mg/L)']
        bod = data['BOD (mg/L)']

        # Prepare input for Random Forest & Isolation Forest
        X = np.array([[ph, turbidity, temperature, do, bod]])
        X_scaled = scaler.transform(X)

        # Random Forest prediction
        rf_pred = rf.predict(X_scaled)[0]

        # Isolation Forest (anomaly detection)
        iso_pred = iso.predict(X_scaled)[0]

        # Linear Regression (predict turbidity)
        lr_input = np.array([[ph, temperature, do, bod]])
        lr_input_scaled = scaler_lr.transform(lr_input)
        predicted_turbidity = lr.predict(lr_input_scaled)[0]

        # ---------------------------
        # Convert results to text

        result_text = "Water is Safe" if rf_pred == 0 else "Water is Unsafe"

        sudden_change = "No sudden spike detected"

        if iso_pred == -1:
            result_text = "Water is Unsafe"
            sudden_change = "Sudden spike detected!"

        result = {
            "result": result_text,
            "sudden_change": sudden_change,
            "predicted_turbidity": round(float(predicted_turbidity), 3)
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})

# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)