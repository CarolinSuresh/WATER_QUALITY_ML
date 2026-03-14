from flask import Flask, jsonify, render_template
from serial_reader import read_serial

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/sensor-data")
def sensor_data():
    data = read_serial()
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)