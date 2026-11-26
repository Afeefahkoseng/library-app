from books.rules import can_borrow


def test_borrow(count, expected):
    if can_borrow(count) != expected:
        print(f"ERROR on can_borrow({count}), expected {expected}")
