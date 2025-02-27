from src.sales import add_item_to_sale

def test_add_item_success():
    result = add_item_to_sale("123", 2)
    assert result["name"] == "Hammer"
    assert result["total"] == 19.98

def test_add_item_not_found():
    result = add_item_to_sale("999", 1)
    assert "error" in result