#!/usr/bin/env bash
set -e

echo "=== Initializing 24/7 VPS Setup ==="

# Update package indices
sudo apt-get update -y
sudo apt-get install -y curl ca-certificates gnupg git

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
fi

# Ensure Docker starts on VPS boot
sudo systemctl enable docker
sudo systemctl start docker

# Build and start container in detached mode
echo "Launching 24/7 container..."
docker compose up -d --build

echo "=== Service is live and running 24/7! ==="
docker compose ps
