import core.email as email_module
from core.templates import render_template
from settings import settings


class EmailService:
    @staticmethod
    def send_verification_email(email: str, verification_token: str):
        verification_link = (
            f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
        )

        html = render_template(
            "emails/verify_email.html",
            {"verification_link": verification_link},
        )

        email_module.send_html_email(
            to=email,
            subject="✅ Verifique seu e-mail",
            html=html,
        )

    @staticmethod
    def send_password_reset_email(email: str, reset_token: str):
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

        html = render_template(
            "emails/reset_password.html",
            {"reset_link": reset_link},
        )

        email_module.send_html_email(
            to=email,
            subject="🔐 Redefinição de senha",
            html=html,
        )

    @staticmethod
    def send_daily_quote(
        email: str,
        text: str,
        author: str,
        username: str | None = None,
        patrimony_total_label: str | None = None,
        patrimony_comparison_label: str | None = None,
    ):
        html = render_template(
            "emails/daily_quote.html",
            {
                "text": text,
                "author": author,
                "username": username,
                "patrimony_total_label": patrimony_total_label,
                "patrimony_comparison_label": patrimony_comparison_label,
            },
        )

        email_module.send_html_email(
            to=email,
            subject="📜 Daily Digest",
            html=html,
        )
