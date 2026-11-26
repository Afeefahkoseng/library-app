MAX_BOOKS = 3


def can_borrow(count):
    """ยืมเพิ่มได้ไหม เมื่อตอนนี้ยืมอยู่ count เล่ม"""
    return 0 <= count < MAX_BOOKS
