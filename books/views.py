from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_POST

from .models import Book, Member
from .rules import can_borrow


@cache_page(30)
def index(request):
    return render(request, "books/index.html", {
        "books": Book.objects.all()
    })


def book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    return render(request, "books/book.html", {
        "book": book,
        "borrowers": book.borrowers.all(),
        "non_borrowers": Member.objects.exclude(books=book)
    })


@require_POST
def borrow(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    try:
        member = Member.objects.get(pk=int(request.POST["member"]))
    except (KeyError, ValueError, Member.DoesNotExist):
        return HttpResponseBadRequest("กรุณาเลือกสมาชิก")
    if book.available() <= 0:
        return HttpResponseBadRequest("หนังสือถูกยืมหมดแล้ว")
    if not can_borrow(member.books.count()):
        return HttpResponseBadRequest("สมาชิกยืมครบ 3 เล่มแล้ว")
    member.books.add(book)
    return HttpResponseRedirect(reverse("books:book", args=(book.id,)))