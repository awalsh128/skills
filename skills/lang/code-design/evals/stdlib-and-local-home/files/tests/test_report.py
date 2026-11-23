from sales.report import format_total


def test_format_total():
    assert format_total(3) == "3.00"
