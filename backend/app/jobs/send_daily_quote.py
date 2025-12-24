"""
Job: Envio diário da frase do dia por email
"""

from services.daily_quote_email import send_daily_quote_emails


def main():
    send_daily_quote_emails()


if __name__ == "__main__":
    main()
