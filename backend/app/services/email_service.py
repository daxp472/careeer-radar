import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Any, Optional
from jinja2 import Template
from app.core.config import settings
from app.core.logging import logger


class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USERNAME
        self.smtp_pass = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME
        self.use_tls = settings.SMTP_USE_TLS

    def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """
        Send an HTML email via SMTP, or log formatted email if SMTP is unconfigured (dev/mock mode).
        """
        if not self.smtp_host or not self.smtp_user:
            logger.info(f"[EmailService - MOCK/DEV] To: {to_email} | Subject: '{subject}'\n[HTML Preview Length: {len(html_content)} bytes]")
            return True

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            if text_content:
                msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=15) as server:
                if self.use_tls:
                    server.starttls()
                if self.smtp_user and self.smtp_pass:
                    server.login(self.smtp_user, self.smtp_pass)
                server.sendmail(self.from_email, [to_email], msg.as_string())

            logger.info(f"[EmailService] Email successfully sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"[EmailService] Failed to send email to {to_email}: {e}")
            return False

    def send_weekly_job_digest(
        self,
        to_email: str,
        candidate_name: str,
        target_role: str,
        location: str,
        total_new_jobs: int,
        jobs_above_threshold: int,
        min_match_score: float,
        top_jobs: List[Dict[str, Any]]
    ) -> bool:
        try:
            import os
            template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "emails", "weekly_job_digest.html")
            with open(template_path, "r", encoding="utf-8") as f:
                raw_template = f.read()
            
            template = Template(raw_template)
            html = template.render(
                candidate_name=candidate_name,
                target_role=target_role,
                location=location,
                total_new_jobs=total_new_jobs,
                jobs_above_threshold=jobs_above_threshold,
                min_match_score=min_match_score,
                top_jobs=top_jobs[:settings.MAX_WEEKLY_EMAIL_JOBS],
                frontend_url=settings.FRONTEND_URL
            )
            subject = f"🎯 CareerRadar: {total_new_jobs} New Job Matches ({jobs_above_threshold} with {round(min_match_score)}%+ match)"
            return self.send_email(to_email=to_email, subject=subject, html_content=html)
        except Exception as e:
            logger.error(f"[EmailService] Error rendering weekly job digest: {e}")
            return False

    def send_reminder(self, to_email: str, candidate_name: str, message: str) -> bool:
        try:
            import os
            template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "emails", "reminder.html")
            with open(template_path, "r", encoding="utf-8") as f:
                raw_template = f.read()

            template = Template(raw_template)
            html = template.render(
                candidate_name=candidate_name,
                message=message,
                frontend_url=settings.FRONTEND_URL
            )
            subject = "🔔 CareerRadar Market Reminder: New Opportunities Available"
            return self.send_email(to_email=to_email, subject=subject, html_content=html)
        except Exception as e:
            logger.error(f"[EmailService] Error rendering reminder: {e}")
            return False


email_service = EmailService()
