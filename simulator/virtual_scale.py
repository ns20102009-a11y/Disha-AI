"""
IoT Virtual Scale & Load-Cell Telemetry Simulator
Legal Metrology Online Verification Portal - Government of India

Simulates an electronic weighing scale indicator (RS-232 / Modbus / Bluetooth)
streaming continuous weight packets into the Legal Metrology Officer app.
"""

import time
import random
import sys
try:
    import urllib.request
    import json
except ImportError:
    pass

API_ENDPOINT = "http://127.0.0.1:8000/api/iot/set-simulated-weight"

def simulate_weight_cycle():
    print("==========================================================")
    print("  ⚖️  LEGAL METROLOGY IoT LOAD-CELL SIMULATOR (RS-232)")
    print("  Streaming live calibration packets to LMO Inspector app...")
    print("==========================================================\n")

    test_stages = [
        {"name": "Zero Tare Test (Empty Platform)", "weight": 0.000, "duration": 4},
        {"name": "Class M1 1kg Standard Weight Placed", "weight": 1.000, "duration": 4},
        {"name": "Class M1 5kg Standard Weight Placed", "weight": 5.000, "duration": 6},
        {"name": "Class M1 10kg Calibration Weight Placed", "weight": 10.000, "duration": 4},
        {"name": "Corner Load Eccentricity Test", "weight": 5.002, "duration": 4},
        {"name": "Scale Return to Zero", "weight": 0.000, "duration": 4},
    ]

    while True:
        for stage in test_stages:
            print(f"\n>> [SIMULATOR EVENT]: {stage['name']} -> Target: {stage['weight']} kg")
            start = time.time()
            while time.time() - start < stage["duration"]:
                # Micro-jitter of 1-2 grams to emulate real-world ADC sensor
                jitter = random.uniform(-0.002, 0.002) if stage["weight"] > 0 else 0.0
                current_weight = round(stage["weight"] + jitter, 3)

                try:
                    payload = json.dumps({"weight": current_weight, "is_stable": True}).encode("utf-8")
                    req = urllib.request.Request(
                        API_ENDPOINT,
                        data=payload,
                        headers={"Content-Type": "application/json"}
                    )
                    urllib.request.urlopen(req, timeout=1.0)
                    sys.stdout.write(f"\r   Streaming Packet: [{current_weight:.3f} kg] [STABLE: YES]   ")
                    sys.stdout.flush()
                except Exception as e:
                    sys.stdout.write(f"\r   Connecting to server... ({e})   ")
                    sys.stdout.flush()

                time.sleep(0.5)

if __name__ == "__main__":
    simulate_weight_cycle()
