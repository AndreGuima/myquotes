from core.templates import render_template


def test_render_daily_quote_template():
    html = render_template(
        "emails/daily_quote.html",
        {
            "text": "Teste",
            "author": "Autor",
            "username": "Andre",
        },
    )

    assert "Teste" in html
    assert "Autor" in html
    assert "Andre" in html


def test_render_daily_quote_template_without_username():
    html = render_template(
        "emails/daily_quote.html",
        {
            "text": "Teste",
            "author": "Autor",
            "username": None,
        },
    )

    assert "Teste" in html
    assert "Autor" in html


def test_render_reset_password_template():
    html = render_template(
        "emails/reset_password.html",
        {"reset_link": "http://example.com/reset?token=123"},
    )

    assert "reset?token=123" in html
