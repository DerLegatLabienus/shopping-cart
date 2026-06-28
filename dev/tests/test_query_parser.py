import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../skill'))

from query_parser import QueryParser


def test_parse_budget_under():
    f = QueryParser().parse("lentils under 20 shekels")
    assert f.max_price == 20.0
    assert f.min_price == 0.0


def test_parse_budget_range():
    f = QueryParser().parse("vegetables 50-100")
    assert f.min_price == 50.0
    assert f.max_price == 100.0


def test_parse_no_budget():
    f = QueryParser().parse("show me lentils")
    assert f.min_price is None
    assert f.max_price is None


def test_parse_category_direct():
    f = QueryParser().parse("show me vegetables")
    assert "vegetables" in f.categories


def test_parse_category_alias_lentils():
    f = QueryParser().parse("I want some lentils and beans")
    assert "legumes" in f.categories


def test_parse_category_alias_veggies():
    f = QueryParser().parse("fresh veggies please")
    assert "vegetables" in f.categories


def test_parse_attributes_vegan():
    f = QueryParser().parse("vegan products under 30")
    assert "vegan" in f.attributes


def test_parse_attributes_organic():
    f = QueryParser().parse("organic bread")
    assert "organic" in f.attributes


def test_parse_keywords_extracted():
    f = QueryParser().parse("chickpeas under 15 shekels")
    assert "chickpeas" in f.keywords


def test_needs_clarification_no_category_no_budget():
    q = QueryParser().needs_clarification("give me stuff")
    assert any("categor" in s.lower() for s in q)
    assert any("budget" in s.lower() for s in q)


def test_needs_clarification_full_query_asks_format():
    q = QueryParser().needs_clarification("vegan vegetables under 50")
    assert len(q) == 1
    assert "format" in q[0].lower()


def test_is_buy_intent_true():
    assert QueryParser().is_buy_intent("add milk to cart")
    assert QueryParser().is_buy_intent("buy chickpeas")


def test_is_buy_intent_false():
    assert not QueryParser().is_buy_intent("show me lentils")
    assert not QueryParser().is_buy_intent("what vegetables do you have")
