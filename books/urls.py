from django.urls import path

from . import views

app_name = "books"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:book_id>", views.book, name="book"),
    path("<int:book_id>/borrow", views.borrow, name="borrow")
]
