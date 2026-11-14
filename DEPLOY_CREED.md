# Deploying Always-On Service to 192.168.1.4 (Host: creed)

### Important Network Note
`192.168.1.4` is a **Local Area Network (LAN)** IP address.
- If `192.168.1.4` is a **separate dedicated device** on your local network (such as a Home Server, Raspberry Pi, or NAS), it **will** stay running when your workstation is turned off, provided that device remains powered on.
- If `192.168.1.4` is the network adapter of this current workstation, turning this machine off will power down the container as well.

---

### Step 1: Copy Project Files to the Target Server
Run this from your workstation terminal:

```powershell
scp -r C:\Users\Playbeat\.gemini\antigravity\scratch\always-on-service creed@192.168.1.4:~/always-on-service
```

---

### Step 2: Connect and Run the Deploy Script
Log into the server:

```powershell
ssh creed@192.168.1.4
```

Then execute the automated setup script:

```bash
cd ~/always-on-service
chmod +x setup-vps.sh
./setup-vps.sh
```

---

### Step 3: Verify 24/7 Status
Inside your SSH session, run:
```bash
docker compose ps
docker compose logs -f
```
Once verified, you can exit the SSH session (`exit`). The container will continue running uninterrupted in the background.
