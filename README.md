# 24/7 Always-On Service Template
A production-ready, self-healing template designed to run 24/7 on any Cloud VPS (DigitalOcean, Hetzner, AWS, GCP) independently of your local workstation.

## Included Components
- `docker-compose.yml`: Automated restart policy (`unless-stopped`), health checks, and log rotation.
- `Dockerfile`: Multi-stage, non-root, lightweight Python 3.11 image.
- `main.py`: Async web service with `/health` endpoint and background worker.
- `setup-vps.sh`: One-click setup script for any fresh Ubuntu/Debian VPS.
