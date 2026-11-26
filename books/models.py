from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=100)
    copies = models.IntegerField()

    def __str__(self):
        return self.title

    def is_valid_book(self):
        return self.title != "" and self.copies >= 0

    def available(self):
        return self.copies - self.borrowers.count()


class Member(models.Model):
    name = models.CharField(max_length=64)
    books = models.ManyToManyField(Book, blank=True, related_name="borrowers")

    def __str__(self):
        return self.name
