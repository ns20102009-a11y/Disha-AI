import asyncio
import json
import random
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

router = APIRouter(prefix="/api/iot", tags=["IoT Scale Telemetry"])

# Global state for simulated hardware scale
class VirtualScaleState:
    def __init__(self):
        self.target_weight = 5.000  # Default 5 kg standard weight test
        self.unit = "kg"
        self.is_stable = True
        self.tare = 0.0
        self.device_id = "VIRTUAL-RS232-SCALE-01"

virtual_scale = VirtualScaleState()

class WeightSetRequest(BaseModel):
    weight: float
    is_stable: bool = True

@router.post("/set-simulated-weight")
def set_simulated_weight(req: WeightSetRequest):
    virtual_scale.target_weight = req.weight
    virtual_scale.is_stable = req.is_stable
    return {"message": "Simulated weight updated", "current_target": virtual_scale.target_weight}

@router.get("/current-reading")
def get_current_reading():
    # Add minor sensor micro-fluctuation (+/- 1-2 grams)
    jitter = random.uniform(-0.002, 0.002) if virtual_scale.is_stable else random.uniform(-0.05, 0.05)
    live_weight = round(virtual_scale.target_weight + jitter, 3)
    return {
        "device_id": virtual_scale.device_id,
        "weight": live_weight,
        "unit": virtual_scale.unit,
        "is_stable": virtual_scale.is_stable,
        "timestamp": time.time()
    }

@router.websocket("/ws/scale-telemetry")
async def websocket_scale_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            jitter = random.uniform(-0.002, 0.002) if virtual_scale.is_stable else random.uniform(-0.05, 0.05)
            live_weight = round(virtual_scale.target_weight + jitter, 3)
            packet = {
                "device_id": virtual_scale.device_id,
                "weight": live_weight,
                "unit": virtual_scale.unit,
                "is_stable": virtual_scale.is_stable,
                "timestamp": round(time.time(), 2)
            }
            await websocket.send_text(json.dumps(packet))
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
