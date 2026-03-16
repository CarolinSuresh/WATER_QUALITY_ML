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

        if "MLDATA:" in line:

            data = line.split("MLDATA:")[1].strip()
            values = data.split(",")

            if len(values) >= 6:

                ph = float(values[0])
                turb = float(values[1])
                temp = float(values[2])

                # -------- AMMONIA CALIBRATION --------
                raw_ammonia = float(values[3])

                # 60-70 ppm considered baseline
                ammonia = max(0, raw_ammonia - 65)

                tds = float(values[4])
                waterlevel = float(values[5])

                # -------- DERIVED ML FEATURES --------

                # approximate dissolved oxygen from temperature
                do = max(0, 14.6 - 0.4 * temp)

                # approximate BOD from pollution indicators
                bod = (ammonia / 20) + (turb / 10) + (tds / 200)

                payload = {
                    "pH": ph,
                    "Turbidity (NTU)": turb,
                    "Temperature (°C)": temp,
                    "DO (mg/L)": do,
                    "BOD (mg/L)": bod,
                    "WaterLevel": waterlevel
                }

                print("Sending to ML:", payload)

                res = requests.post(
                    "http://127.0.0.1:5000/predict",
                    json=payload
                )

                print("ML RESULT:", res.json())
                print("---------------------------")

            else:
                print("⚠ Incomplete MLDATA:", values)

    except Exception as e:
        print("Error:", e)