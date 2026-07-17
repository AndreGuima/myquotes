from models.investment import Investment


def test_investment_model_imports_cleanly():
    assert Investment.__tablename__ == "investments"
