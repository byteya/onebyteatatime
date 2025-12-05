#!/usr/bin/env python3

import os
import smtplib
import sys
from datetime import datetime, timedelta
from email.mime.text import MIMEText

# ------------------------
# CONFIGURATION
# ------------------------
SCAN_DIR = "/path/to/your/backup"
EMAIL_FROM = "server@example.com"
EMAIL_TO = "you@example.com"
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
SMTP_USER = "server@example.com"
SMTP_PASS = "yourpassword"
# ------------------------

def get_changed_files(scan_dir):
    """Return a dict {directory: total_size_in_bytes} and an overall count."""
    cutoff = datetime.now() - timedelta(days=1)
    changed_per_dir = {}
    changed_file_count = 0

    for root, dirs, files in os.walk(scan_dir):
        total_size = 0
        for f in files:
            path = os.path.join(root, f)
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(path))
            except FileNotFoundError:
                continue  # Skip files that disappear mid-scan

            if mtime > cutoff:
                size = os.path.getsize(path)
                total_size += size
                changed_file_count += 1

        if total_size > 0:
            changed_per_dir[root] = total_size

    return changed_file_count, changed_per_dir


def send_email(subject, body):
    msg = MIMEText(body)
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        if SMTP_USER and SMTP_PASS:
            server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)


def main():
    count, changed_dirs = get_changed_files(SCAN_DIR)

    # Build human-friendly report
    lines = []
    lines.append(f"Backup Change Report for {datetime.now().strftime('%Y-%m-%d')}")
    lines.append(f"Directory scanned: {SCAN_DIR}")
    lines.append("")
    lines.append(f"Total files changed: {count}")
    lines.append("")

    if not changed_dirs:
        lines.append("No files changed in the last 24 hours.")
    else:
        lines.append("Changed file size by directory:")
        for d, size in sorted(changed_dirs.items()):
            mb = size / (1024 * 1024)
            lines.append(f"  {d}: {mb:.2f} MB")

    report = "\n".join(lines)
    send_email("Daily Backup Change Report", report)


if __name__ == "__main__":
    main()
