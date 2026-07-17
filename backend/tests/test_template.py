from core.templates import render_template


def test_render_daily_quote_template():
    html = render_template(
        "emails/daily_quote.html",
        {
            "text": "Teste",
            "author": "Autor",
            "username": "Andre",
            "patrimony_total_label": "R$ 500,00",
            "patrimony_comparison_label": (
                "Você tem R$ 50,00 a mais que o mês passado."
            ),
            "patrimony_semester_comparison_label": (
                "Você tem R$ 100,00 a mais em relação ao semestre passado."
            ),
            "patrimony_year_comparison_label": (
                "Você tem R$ 150,00 a mais em relação ao mesmo dia do ano passado."
            ),
        },
    )

    assert "Teste" in html
    assert "Autor" in html
    assert "Andre" in html
    assert "Montante atual" in html
    assert "R$ 500,00" in html
    assert "Você tem R$ 50,00 a mais que o mês passado." in html
    assert "Você tem R$ 100,00 a mais em relação ao semestre passado." in html
    assert "Você tem R$ 150,00 a mais em relação ao mesmo dia do ano passado." in html


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
