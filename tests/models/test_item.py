from visivo.models.item import Item
from visivo.models.base_model import REF_REGEX
from pydantic import ValidationError
import pytest


def test_Target_simple_data():
    data = {"width": 2}
    item = Item(**data)
    assert item.width == 2


def test_Item_both_chart_and_markdown():
    with pytest.raises(ValidationError) as exc_info:
        Item(chart="ref(chart)", markdown="markdown")

    error = exc_info.value.errors()[0]
    assert (
        error["msg"]
        == 'only one of the "markdown", "chart", or "table" properties should be set on an item'
    )
    assert error["type"] == "value_error"


def test_Item_invalid_ref_string():
    item = Item(chart="ref(chart)")
    item.chart = "ref(chart)"
    with pytest.raises(ValidationError) as exc_info:
        Item(chart="ref(chart")

    error = exc_info.value.errors()[0]
    assert error["msg"] == f'string does not match regex "{REF_REGEX}"'
    assert error["type"] == "value_error.str.regex"