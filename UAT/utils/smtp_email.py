"""
utils/smtp_email.py
====================
SMTP email notification utility.
Sends execution reports and alerts via a configured SMTP relay.
"""

import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Iterable

from utils.paths import get_config_path


# ---------------------------------------------------------------------------
# SMTP configuration
# ---------------------------------------------------------------------------
SMTP_HOST = "smtp.its.hpecorp.net"
FROM_ADDR = "mdcp.automation@hpe.com"
FROM_NAME = "Albert Automation"


# ---------------------------------------------------------------------------
# Recipient loading
# ---------------------------------------------------------------------------

def get_email_recipients():
    """
    Read email recipients from config/email_recipients.txt.

    Format rules:
      - Lines starting with '#' are treated as comments and ignored.
      - Blank lines are ignored.
      - Lines prefixed with 'cc:' are CC addresses (case-insensitive).
      - All other non-empty lines are TO addresses.

    Returns:
        tuple[list[str], list[str]]: (to_recipients, cc_recipients)

    Raises:
        FileNotFoundError: If recipients file doesn't exist.
        ValueError:        If recipients file has no TO addresses.
    """
    file_path = get_config_path("email_recipients.txt")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Recipients file not found: {file_path}")

    to_recipients: list = []
    cc_recipients: list = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.lower().startswith("cc:"):
                cc_recipients.append(line[3:].strip())
            else:
                to_recipients.append(line)

    if not to_recipients:
        raise ValueError(
            f"Recipients file has no TO addresses: {file_path}\n"
            f"Add at least one email address on its own line."
        )

    return to_recipients, cc_recipients


# ---------------------------------------------------------------------------
# Core send function
# ---------------------------------------------------------------------------

def send_email(
    subject: str,
    body: str,
    to_recipient: Iterable,
    cc_recipient: Iterable = (),
    attachments: list = None,
    smtp_host: str = SMTP_HOST,
    from_addr: str = FROM_ADDR,
    from_name: str = FROM_NAME,
) -> None:
    """
    Send an HTML email via SMTP with optional file attachments.

    Args:
        subject      : Email subject line.
        body         : Email body text (rendered inside <pre> for formatting).
        to_recipient : TO addresses (iterable of strings).
        cc_recipient : CC addresses (optional).
        attachments  : List of absolute file paths to attach (optional).
        smtp_host    : SMTP relay hostname.
        from_addr    : Sender email address.
        from_name    : Sender display name.

    Raises:
        FileNotFoundError : If an attachment path does not exist.
        Exception         : If the SMTP send fails (with hostname in message).
    """
    to_list = list(to_recipient)
    cc_list = list(cc_recipient)

    # Build message
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"]    = f"{from_name} <{from_addr}>"
    msg["To"]      = ", ".join(to_list)
    if cc_list:
        msg["Cc"] = ", ".join(cc_list)

    # Body — wrap in <pre> so plain-text spacing and line breaks are preserved
    html_body = (
        "<html><body>"
        "<pre style='font-family:Courier New,monospace;font-size:13px'>"
        f"{body}"
        "</pre></body></html>"
    )
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    # Attachments
    if attachments:
        for file_path in attachments:
            file_path = os.path.abspath(file_path)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Attachment not found: {file_path}")

            filename = os.path.basename(file_path)
            with open(file_path, "rb") as fh:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(fh.read())

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                "attachment",
                filename=filename,
            )
            msg.attach(part)

    # Send
    all_recipients = to_list + cc_list
    try:
        with smtplib.SMTP(smtp_host) as smtp:
            smtp.sendmail(from_addr, all_recipients, msg.as_string())
    except Exception as exc:
        raise Exception(
            f"Failed to send email via SMTP: {exc}\n"
            f"Ensure SMTP host '{smtp_host}' is reachable from this machine."
        )