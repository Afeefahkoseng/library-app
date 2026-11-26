import unittest

from books.rules import can_borrow


class RuleTests(unittest.TestCase):

    def test_negative(self):
        """จำนวนติดลบ ยืมไม่ได้"""
        self.assertFalse(can_borrow(-1))

    def test_0(self):
        """ยังไม่ได้ยืม ยืมได้"""
        self.assertTrue(can_borrow(0))

    def test_2(self):
        """ยืมอยู่ 2 เล่ม ยืมได้อีก"""
        self.assertTrue(can_borrow(2))

    def test_3(self):
        """ยืมครบ 3 เล่ม ยืมไม่ได้"""
        self.assertFalse(can_borrow(3))


if __name__ == "__main__":
    unittest.main()
