import pathlib
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By

PAGE = (pathlib.Path(__file__).parent / "days.html").resolve().as_uri()


class DaysPageTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        self.driver.get(PAGE)

    def click(self, button_id, times=1):
        button = self.driver.find_element(By.ID, button_id)
        for i in range(times):
            button.click()

    def days(self):
        return self.driver.find_element(By.TAG_NAME, "h1").text

    def test_title(self):
        self.assertEqual(self.driver.title, "Borrow Days")

    def test_increase(self):
        self.click("increase")
        self.assertEqual(self.days(), "2")

    def test_decrease(self):
        self.click("increase", 2)
        self.click("decrease")
        self.assertEqual(self.days(), "2")

    def test_not_below_1(self):
        self.click("decrease")
        self.assertEqual(self.days(), "1")

    def test_not_above_7(self):
        self.click("increase", 10)
        self.assertEqual(self.days(), "7")


if __name__ == "__main__":
    unittest.main()
