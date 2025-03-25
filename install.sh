#!/bin/bash
set -e

pip install -r requirements

# Create a service file
cat >/etc/systemd/system/mc-sentinel.service <<EOF
[Unit]
Description=mc-sentinel API
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
StandardOutput=journal
StandardError=journal
SyslogIdentifier=mc-sentinel
ExecStart=/usr/bin/python3 /opt/mc-sentinel/mc-sentinel.py

[Install]
WantedBy=multi-user.target
EOF
