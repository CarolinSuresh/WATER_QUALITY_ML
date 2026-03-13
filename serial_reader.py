import serial
import requests

PORT = "COM5"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)

print("Reading LoRa data...\n")

while True:

    try:
        line = ser.readline().decode(errors='ignore').strip()

        if line:
            print("SERIAL:", line)

        # Parse TX format: Sent: ph,tds,turb,ammonia,temp,waterlevel
        if "Sent:" in line:

            data = line.split("Sent:")[1].strip()
            values = data.split(",")

            if len(values) >= 6:

                ph = float(values[0])
                bod = float(values[1])          # using TDS as BOD input
                turb = float(values[2])
                do = float(values[3])           # ammonia used as DO input
                temp = float(values[4])
                waterlevel = float(values[5])

                payload = {
                    "pH": ph,
                    "Turbidity (NTU)": turb,
                    "Temperature (°C)": temp,
                    "DO (mg/L)": do,
                    "BOD (mg/L)": bod,
                    "WaterLevel": waterlevel
                }

                res = requests.post(
                    "http://127.0.0.1:5000/predict",
                    json=payload
                )

                print("ML RESULT:", res.json())
                print("---------------------------")

    except Exception as e:
        print("Error:", e)