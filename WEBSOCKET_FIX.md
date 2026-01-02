# WebSocket URL Fix

## 🔴 New Problem Found:

The voice webhook is working, but the WebSocket connection is failing because:

1. **Flask webhooks** run on port 5002 with ngrok URL: `https://4700f0c97a14.ngrok-free.app`
2. **WebSocket** runs on port 5001 with DIFFERENT ngrok URL: `https://c...ngrok-free.app`

The code was trying to use the port 5002 URL for WebSocket → 404 error!

## ✅ Solution:

You need to tell the system about BOTH ngrok URLs.

### Step 1: Check Your ngrok URLs

From your ngrok terminal, you should see:
```
Forwarding    https://4700f0c97a14.ngrok-free.app -> http://localhost:5002  ← HTTP webhooks
Forwarding    https://cXXXXXXX.ngrok-free.app -> http://localhost:5001       ← WebSocket
```

### Step 2: Update Your .env

Add BOTH URLs:

```env
# HTTP Webhooks (port 5002)
WEBHOOK_BASE_URL=https://4700f0c97a14.ngrok-free.app
WEBHOOK_PORT=5002

# WebSocket (port 5001) - ADD THIS LINE
WEBSOCKET_URL=https://cXXXXXXX.ngrok-free.app
WEBSOCKET_PORT=5001

# Your other settings...
GEMINI_API_KEY=your_key
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+14452344131
TARGET_PHONE_NUMBER=+14049525557
```

**IMPORTANT:** Replace `cXXXXXXX` with the actual second ngrok URL from your terminal!

### Step 3: Restart the Agent

```bash
# Stop current agent (Ctrl+C)
./start_elderly.sh
```

### Step 4: Test

Call your Twilio number. It should now:
1. ✅ Answer the call
2. ✅ Say "Hello, connecting you now"
3. ✅ Connect to WebSocket successfully
4. ✅ Start conversation with Gemini!

---

## 📋 Quick Reference:

| Component | Port | ngrok URL | Config Variable |
|-----------|------|-----------|-----------------|
| Flask Webhooks | 5002 | First URL | `WEBHOOK_BASE_URL` |
| WebSocket | 5001 | Second URL | `WEBSOCKET_URL` |

---

## 🔍 What Was Happening:

**Before:**
```
Twilio → Webhook (5002) ✅
      → WebSocket tries 5002 URL ❌ (404 error)
```

**After:**
```
Twilio → Webhook (5002) ✅
      → WebSocket uses 5001 URL ✅
      → Gemini Live Audio ✅
```

---

**Status:** Need to add `WEBSOCKET_URL` to `.env` with the second ngrok URL!

