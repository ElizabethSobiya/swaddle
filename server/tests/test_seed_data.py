from collections import Counter
from datetime import date

from scripts.seed import CONTENT_ITEMS, PRODUCTS, months_ago


def test_demo_seed_has_requested_product_mix() -> None:
    assert len(PRODUCTS) == 15
    assert Counter(product[1] for product in PRODUCTS) == {
        "pharmacy": 5,
        "toy": 5,
        "supplies": 5,
    }


def test_demo_seed_has_requested_content_mix() -> None:
    assert len(CONTENT_ITEMS) == 15
    assert Counter(item[0] for item in CONTENT_ITEMS) == {
        "rhyme": 5,
        "video": 5,
        "sound": 3,
        "activity": 2,
    }


def test_demo_baby_dates_are_exact_month_offsets() -> None:
    today = date(2026, 7, 22)

    assert months_ago(2, today) == date(2026, 5, 22)
    assert months_ago(8, today) == date(2025, 11, 22)
    assert months_ago(18, today) == date(2025, 1, 22)
