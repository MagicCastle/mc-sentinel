#!/bin/bash
set -e


# Install dependencies
python3 -m venv /opt/mc-sentinel/venv
source /opt/mc-sentinel/venv/bin/activate
pip install -r /opt/mc-sentinel/requirements.txt

# Create the service file
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
ExecStart=/opt/mc-sentinel/venv/bin/flask --app /opt/mc-sentinel/mc_sentinel/main.py run --host=0.0.0.0

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
systemctl enable mc-sentinel
systemctl start mc-sentinel
