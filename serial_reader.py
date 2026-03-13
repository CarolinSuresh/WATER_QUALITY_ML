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

        # Parse TX format: Sent: x,x,x,x,x,x
        if "Sent:" in line:

            data = line.split("Sent:")[1].strip()
            values = data.split(",")

            if len(values) >= 5:

                ph = float(values[0])
                turb = float(values[2])
                temp = float(values[4])
                do = float(values[3])
                bod = float(values[1])

                payload = {
                    "pH": ph,
                    "Turbidity (NTU)": turb,
                    "Temperature (°C)": temp,
                    "DO (mg/L)": do,
                    "BOD (mg/L)": bod
                }

                res = requests.post(
                    "http://127.0.0.1:5000/predict",
                    json=payload
                )

                print("ML RESULT:", res.json())
                print("---------------------------")

    except Exception as e:
        print("Error:", e)