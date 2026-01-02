# ngrok Setup for Phone Call Agent

## Problem
Free ngrok accounts only allow **1 simultaneous tunnel**, but we need **2 tunnels**:
- Port 5000 - Flask webhooks
- Port 5001 - WebSocket for Media Streams

## Solution
Use ngrok's configuration file to run multiple tunnels from a **single ngrok session**.

---

## Quick Setup (3 steps)

### Step 1: Get Your ngrok Authtoken

1. Go to: https://dashboard.ngrok.com/get-started/your-authtoken
2. Copy your authtoken (looks like: `2abc...xyz`)

### Step 2: Update ngrok.yml

Open `ngrok.yml` in this directory and replace:
```yaml
authtoken: YOUR_NGROK_AUTHTOKEN_HERE
```

With your actual token:
```yaml
authtoken: 2abc...xyz  # Your actual token
```

### Step 3: Start ngrok

```bash
./start_ngrok.sh
```

That's it! Both tunnels will start from one ngrok session.

---

## What You'll See

```
ngrok                                                                         

Session Status                online                                          
Account                       Your Name (Plan: Free)                         
Version                       3.x.x                                          

Forwarding                    https://abc123.ngrok.io -> http://localhost:5000
Forwarding                    https://xyz456.ngrok.io -> http://localhost:5001

Web Interface                 http://127.0.0.1:4040                          
```

### Important: Update Your .env

Copy the **first HTTPS URL** (the one pointing to port 5000) to your `.env`:

```env
WEBHOOK_BASE_URL=https://abc123.ngrok.io
```

---

## Alternative: Manual Setup

If you prefer not to use the script:

```bash
ngrok start --all --config ngrok.yml
```

---

## Troubleshooting

### "authtoken not found"
- Make sure you replaced `YOUR_NGROK_AUTHTOKEN_HERE` in `ngrok.yml`
- Get token from: https://dashboard.ngrok.com/get-started/your-authtoken

### "ERR_NGROK_108"
- This means you're trying to run multiple ngrok instances
- Kill all ngrok processes: `pkill ngrok`
- Then run: `./start_ngrok.sh`

### "tunnel not found"
- Check that `ngrok.yml` is in the same directory
- Verify the YAML syntax is correct (no tabs, proper spacing)

---

## ngrok.yml Explained

```yaml
version: "2"
authtoken: YOUR_TOKEN_HERE  # Your auth token

tunnels:
  web:                      # Name for this tunnel
    proto: http             # Protocol
    addr: 5000              # Local port
  
  websocket:                # Name for second tunnel
    proto: http             # Protocol (WebSocket runs over HTTP)
    addr: 5001              # Local port
```

---

## Full Workflow

1. **Terminal 1** - Start ngrok:
   ```bash
   ./start_ngrok.sh
   ```

2. **Copy the HTTPS URL** for port 5000 to `.env`:
   ```env
   WEBHOOK_BASE_URL=https://your-url.ngrok.io
   ```

3. **Terminal 2** - Start the agent:
   ```bash
   ./start_elderly.sh
   ```

---

## Free vs Paid ngrok

**Free Plan:**
- ✅ Multiple tunnels from single session (this solution)
- ❌ URLs change on restart
- ✅ Good for development

**Paid Plan:**
- ✅ Multiple simultaneous sessions
- ✅ Static URLs (don't change)
- ✅ Custom domains
- Better for production

For development, the free plan with config file works great!

---

## Need Help?

- ngrok documentation: https://ngrok.com/docs
- Configuration file docs: https://ngrok.com/docs/agent/config/
- Dashboard: https://dashboard.ngrok.com

---

**Once setup, you only need to run `./start_ngrok.sh` - it's that simple!** 🚀

