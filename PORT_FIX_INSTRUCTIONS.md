# Port 5000 Conflict - Fixed!

## 🔴 Problem Found:
**macOS AirPlay Receiver** was using port 5000, causing Flask to fail silently.

## ✅ Solution Implemented:
Changed Flask webhook port from **5000** → **5002**

---

## 📋 What to Do Now:

### Step 1: Update Your .env File

Edit `.env` and change:

```env
# OLD (don't use):
# WEBHOOK_BASE_URL=https://your-ngrok-url.ngrok-free.app
# WEBHOOK_PORT=5000

# NEW (use this):
WEBHOOK_BASE_URL=https://your-ngrok-url.ngrok-free.app
WEBHOOK_PORT=5002
WEBSOCKET_PORT=5001
```

### Step 2: Restart ngrok

```bash
# Stop current ngrok (Ctrl+C)
# Then restart with new config:
./start_ngrok.sh
```

You'll see:
```
Forwarding    https://abc123.ngrok.io -> http://localhost:5002  ← Use this URL
Forwarding    https://xyz456.ngrok.io -> http://localhost:5001
```

### Step 3: Update Twilio Voice URL

Go to: https://console.twilio.com/

1. Phone Numbers → Active Numbers → Click your number
2. Update **Voice URL** to:
   ```
   https://YOUR-NEW-NGROK-URL.ngrok.io/webhook/voice
   ```
   (Use the URL from port 5002)
3. Save

### Step 4: Update .env with New ngrok URL

```env
WEBHOOK_BASE_URL=https://abc123-new-url.ngrok.io
```

### Step 5: Restart the Agent

```bash
./start_elderly.sh
```

You should now see:
```
✓ Starting webhook server on port 5002
✓ WebSocket server running on ws://0.0.0.0:5001
✓ Elderly Care Phone Agent Ready!
```

### Step 6: Test the Call

Call your Twilio number: **+14452344131**

It should work now! 🎉

---

## 🔍 What Changed:

| Component | Old Port | New Port |
|-----------|----------|----------|
| Flask Webhooks | 5000 (blocked) | 5002 ✅ |
| WebSocket | 5001 | 5001 (unchanged) |
| ngrok tunnel 1 | 5000 | 5002 |
| ngrok tunnel 2 | 5001 | 5001 (unchanged) |

---

## 💡 Why This Happened:

macOS AirPlay Receiver uses port 5000 by default. You can:

**Option A:** Keep using port 5002 (recommended)  
**Option B:** Disable AirPlay Receiver:
- System Settings → General → AirDrop & Handoff
- Turn off "AirPlay Receiver"
- Then you can use port 5000 again

---

## ✅ Verification:

After restarting, check the logs:
- ✅ Should see: `Starting webhook server on port 5002`
- ✅ Should NOT see: "Address already in use"
- ✅ Flask thread should stay alive
- ✅ Calls should connect successfully

---

**Status:** Port conflict resolved! Flask now runs on port 5002.

