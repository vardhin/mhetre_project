from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import os

app = FastAPI(title="Raspberry Pi LED Controller")

# Path to the ACT LED trigger
ACT_LED_TRIGGER = "/sys/class/leds/ACT/trigger"
ACT_LED_BRIGHTNESS = "/sys/class/leds/ACT/brightness"

@app.get("/")
async def root():
    return {"message": "Raspberry Pi LED Controller API"}

@app.post("/led/toggle")
async def toggle_led():
    """Toggle the ACT LED on/off"""
    try:
        # Check if running on Raspberry Pi
        if not os.path.exists(ACT_LED_BRIGHTNESS):
            raise HTTPException(status_code=500, detail="Not running on Raspberry Pi or LED not accessible")
        
        # Set trigger to none to allow manual control
        with open(ACT_LED_TRIGGER, 'w') as f:
            f.write('none')
        
        # Read current brightness
        with open(ACT_LED_BRIGHTNESS, 'r') as f:
            current = int(f.read().strip())
        
        # Toggle (0 -> 1, 1 -> 0)
        new_value = 0 if current == 1 else 1
        
        with open(ACT_LED_BRIGHTNESS, 'w') as f:
            f.write(str(new_value))
        
        return JSONResponse(content={
            "status": "success",
            "led_state": "on" if new_value == 1 else "off"
        })
    
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied. Run with sudo or adjust permissions")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/led/status")
async def get_led_status():
    """Get current LED status"""
    try:
        with open(ACT_LED_BRIGHTNESS, 'r') as f:
            brightness = int(f.read().strip())
        
        return {
            "led_state": "on" if brightness == 1 else "off",
            "brightness": brightness
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)