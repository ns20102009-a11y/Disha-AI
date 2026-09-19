import os
import smtplib
import logging

from email.message import EmailMessage


logger = logging.getLogger(__name__)


def send_complaint_email(complaint):
    """
    Sends complaint notification to the department/admin email.
    SMTP credentials are loaded from environment variables.
    """

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")

    receiver_email = os.getenv("ADMIN_EMAIL")

    if not smtp_username or not smtp_password or not receiver_email:
        logger.warning(
            "Email not sent: SMTP_USERNAME, SMTP_PASSWORD or ADMIN_EMAIL is missing."
        )
        return False

    message = EmailMessage()

    message["Subject"] = (
        f"New DISHA AI Grievance Received - {complaint.complaint_id}"
    )

    message["From"] = smtp_username
    message["To"] = receiver_email

    if complaint.complainant_email:
        message["Reply-To"] = complaint.complainant_email

    message.set_content(
        f"""
DISHA AI - Citizen Grievance Notification

A new consumer grievance has been registered.

----------------------------------------
GRIEVANCE DETAILS
----------------------------------------

Grievance ID:
{complaint.complaint_id}

Complainant Name:
{complaint.complainant_name}

Complainant Phone:
{complaint.complainant_phone}

Complainant Email:
{complaint.complainant_email or "Not provided"}

Complaint Type:
{complaint.complaint_type}

Instrument ID:
{complaint.instrument_id or "Not linked"}

Status:
{complaint.status}

Description:
{complaint.description}

Created At:
{complaint.created_at}

----------------------------------------

Please review this complaint in the DISHA AI admin panel.

This is an automated notification from DISHA AI.
"""
    )

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)

        logger.info(
            "Complaint email sent successfully for %s",
            complaint.complaint_id
        )

        return True

    except Exception:
        logger.exception(
            "Failed to send complaint email for %s",
            complaint.complaint_id
        )

        return False
