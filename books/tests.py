from django.test import TestCase

from .models import Book, Member


class LibraryTestCase(TestCase):

    def setUp(self):
        Book.objects.create(title="Python", copies=1)
        Book.objects.create(title="", copies=1)
        Book.objects.create(title="Django", copies=-1)
        Member.objects.create(name="Alice")

    # ---------- ทดสอบ model ----------
    def test_valid_book(self):
        self.assertTrue(Book.objects.get(title="Python").is_valid_book())

    def test_invalid_title(self):
        self.assertFalse(Book.objects.get(title="").is_valid_book())

    def test_invalid_copies(self):
        self.assertFalse(Book.objects.get(title="Django").is_valid_book())

    def test_available(self):
        book = Book.objects.get(title="Python")
        Member.objects.get(name="Alice").books.add(book)
        self.assertEqual(book.available(), 0)

    # ---------- ทดสอบหน้าเว็บ ----------
    def test_index(self):
        response = self.client.get("/books/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["books"].count(), 3)

    def test_book_page(self):
        book = Book.objects.get(title="Python")
        response = self.client.get(f"/books/{book.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["non_borrowers"].count(), 1)

    def test_book_not_found(self):
        response = self.client.get("/books/999")
        self.assertEqual(response.status_code, 404)

    def test_borrow(self):
        book = Book.objects.get(title="Python")
        member = Member.objects.get(name="Alice")
        response = self.client.post(f"/books/{book.id}/borrow", {"member": member.id})
        self.assertEqual(response.status_code, 302)
        self.assertIn(book, member.books.all())

    def test_borrow_no_copies_left(self):
        book = Book.objects.get(title="Python")
        Member.objects.get(name="Alice").books.add(book)
        bob = Member.objects.create(name="Bob")
        response = self.client.post(f"/books/{book.id}/borrow", {"member": bob.id})
        self.assertEqual(response.status_code, 400)
        self.assertNotIn(book, bob.books.all())

    def test_borrow_over_limit(self):
        member = Member.objects.get(name="Alice")
        for i in range(3):
            member.books.add(Book.objects.create(title=f"Book {i}", copies=1))
        book = Book.objects.get(title="Python")
        response = self.client.post(f"/books/{book.id}/borrow", {"member": member.id})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(member.books.count(), 3)


class SecurityTestCase(TestCase):
    PAYLOAD = "<script>alert('hi')</script>"

    def test_book_title_is_escaped(self):
        book = Book.objects.create(title=self.PAYLOAD, copies=1)
        for url in ["/books/", f"/books/{book.id}"]:
            response = self.client.get(url)
            self.assertNotContains(response, self.PAYLOAD)
            self.assertContains(response, "&lt;script&gt;")

    def test_member_name_is_escaped(self):
        book = Book.objects.create(title="Python", copies=2)
        borrower = Member.objects.create(name=self.PAYLOAD)
        borrower.books.add(book)
        Member.objects.create(name=self.PAYLOAD)
        response = self.client.get(f"/books/{book.id}")
        self.assertNotContains(response, self.PAYLOAD)
        self.assertContains(response, "&lt;script&gt;")
