import serial
import time

PORT = "COM5"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)

latest_data = {
    "ph": 0,
    "temperature": 0,
    "turbidity": 0,
    "tds": 0,
    "water_level": 0,
    "flow": 0
}

def read_serial():
    global latest_data

    try:
        line = ser.readline().decode('utf-8').strip()

        if line:
            print("SERIAL:", line)

            values = line.split(",")

            if len(values) == 6:
                latest_data = {
                    "ph": float(values[0]),
                    "temperature": float(values[1]),
                    "turbidity": float(values[2]),
                    "tds": float(values[3]),
                    "water_level": float(values[4]),
                    "flow": float(values[5])
                }

    except Exception as e:
        print("Serial Error:", e)

    return latest_data