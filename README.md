# ระบบยืมหนังสือห้องสมุด (CS50 Web Week 7: Testing, CI/CD)

เว็บ Django เล็กๆ ดูรายการหนังสือและให้สมาชิกยืม กฎคือ **ยืมได้คนละไม่เกิน 3 เล่ม** และ **ยืมไม่ได้ถ้าหนังสือหมด**

| ขั้น | หัวข้อในวิดีโอ | ไฟล์ |
|---|---|---|
| 3 | `assert`, ฟังก์ชันทดสอบ, shell script, `unittest` | `books/rules.py`, `assert_demo.py`, `tests0.py`, `tests0.sh`, `tests1.py` |
| 4–5 | Django และ Django testing | `books/` |
| 6 | Selenium | `selenium_tests/` |
| 7 | CI/CD, GitHub Actions | `.github/workflows/ci.yml` |
| 8 | Docker, Docker Compose | `Dockerfile`, `docker-compose.yml` |

คำสั่งทั้งหมดพิมพ์ใน Terminal ที่โฟลเดอร์ `library-app` และเปิด venv ไว้

---

## ขั้นที่ 1: ติดตั้งโปรแกรม

- Python 3.13 (Windows: ติ๊ก **Add Python to PATH** ตอนติดตั้ง)
- VS Code
- Git และบัญชี GitHub
- Google Chrome (ใช้ในขั้นที่ 6)
- Docker Desktop (ใช้ในขั้นที่ 8)

## ขั้นที่ 2: สร้างโปรเจกต์

สร้างโฟลเดอร์ `library-app` เปิดใน VS Code แล้วเปิด Terminal

**สร้างและเปิด venv**

```bash
# Windows (PowerShell)
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

ถ้า PowerShell ไม่ยอมให้เปิด ให้รัน `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` แล้วลองใหม่

**สร้างไฟล์ `requirements.txt`**

```text
Django>=5.2,<6
psycopg[binary]>=3.2
selenium>=4.20
```

**ติดตั้งและสร้างโครง Django** (อย่าลืมจุด `.` ท้ายคำสั่ง)

```bash
pip install -r requirements.txt
django-admin startproject library .
python manage.py startapp books
```

---

## ขั้นที่ 3: ทดสอบฟังก์ชันพื้นฐาน

### 3.1 เขียนกฎการยืม: `books/rules.py`

```python
MAX_BOOKS = 3


def can_borrow(count):
    """ยืมเพิ่มได้ไหม เมื่อตอนนี้ยืมอยู่ count เล่ม"""
    return 0 <= count < MAX_BOOKS
```

### 3.2 `assert`: `assert_demo.py`

`assert` จะเงียบถ้าเงื่อนไขจริง และ error ถ้าเป็นเท็จ

```python
from books.rules import can_borrow

assert can_borrow(0)
assert not can_borrow(3)

print("assert ผ่านทั้งหมด")
```

```bash
python assert_demo.py
```

### 3.3 ฟังก์ชันทดสอบและ shell script

`tests0.py`

```python
from books.rules import can_borrow


def test_borrow(count, expected):
    if can_borrow(count) != expected:
        print(f"ERROR on can_borrow({count}), expected {expected}")
```

`tests0.sh`

```bash
python -c "from tests0 import test_borrow; test_borrow(-1, False)"
python -c "from tests0 import test_borrow; test_borrow(0, True)"
python -c "from tests0 import test_borrow; test_borrow(2, True)"
python -c "from tests0 import test_borrow; test_borrow(3, False)"
python -c "from tests0 import test_borrow; test_borrow(10, False)"
```

```bash
bash tests0.sh
```

ไม่มีข้อความขึ้น = ผ่าน (Windows: รันใน **Git Bash** โดยเปิด venv ด้วย `source venv/Scripts/activate` ก่อน)

### 3.4 `unittest`: `tests1.py`

ข้อความใน `"""..."""` จะแสดงเมื่อเทสต์ข้อนั้นไม่ผ่าน

```python
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
```

```bash
python tests1.py
```

ต้องได้ `Ran 4 tests` และ `OK`

### 3.5 ลองใส่บั๊ก (บั๊ก → ไม่ผ่าน → แก้ → ผ่าน)

1. ใน `books/rules.py` เปลี่ยน `count < MAX_BOOKS` เป็น `count <= MAX_BOOKS`
2. รัน `python tests1.py` จะได้ `FAIL: test_3` และ `True is not false`
3. แก้กลับเป็น `<` แล้วรันใหม่ ต้องได้ `OK`

---

## ขั้นที่ 4: สร้างเว็บ Django

สร้างและแก้ไฟล์ให้ครบทุกข้อก่อน แล้วค่อยรันคำสั่งในข้อ 4.6

### 4.1 แก้ `library/settings.py` (4 จุด)

จุดที่ 1: บนสุดของส่วน import เพิ่ม `import os`

```python
import os
from pathlib import Path
```

จุดที่ 2: แก้ `ALLOWED_HOSTS`

```python
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]
```

จุดที่ 3: เพิ่ม `'books',` เป็นบรรทัดแรกใน `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    'books',
    # ...ของเดิม ไม่ต้องลบ
]
```

จุดที่ 4: ลบ `DATABASES = {...}` เดิมทั้งก้อน แล้ววางอันนี้แทน

```python
if os.environ.get("POSTGRES_HOST"):
    # รันใน Docker: ใช้ PostgreSQL
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "postgres",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "HOST": os.environ["POSTGRES_HOST"],
            "PORT": 5432,
        }
    }
else:
    # รันบนเครื่องและ GitHub Actions: ใช้ SQLite
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
```

### 4.2 Model: `books/models.py`

```python
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
```

### 4.3 Admin: `books/admin.py`

```python
from django.contrib import admin

from .models import Book, Member

admin.site.register(Book)
admin.site.register(Member)
```

### 4.4 Views และ URLs

`books/views.py`

```python
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Book, Member
from .rules import can_borrow


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
```

สร้างไฟล์ใหม่ `books/urls.py`

```python
from django.urls import path

from . import views

app_name = "books"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:book_id>", views.book, name="book"),
    path("<int:book_id>/borrow", views.borrow, name="borrow")
]
```

แก้ `library/urls.py` ให้เป็นแบบนี้

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("books/", include("books.urls"))
]
```

### 4.5 หน้าเว็บ

สร้างโฟลเดอร์ `books/templates/books/` แล้วสร้าง 3 ไฟล์

`layout.html`

```html
<!DOCTYPE html>
<html lang="th">
    <head>
        <meta charset="utf-8">
        <title>ห้องสมุด</title>
    </head>
    <body>
        {% block body %}
        {% endblock %}
    </body>
</html>
```

`index.html`

```html
{% extends "books/layout.html" %}

{% block body %}
    <h1>รายการหนังสือ</h1>
    <ul>
        {% for book in books %}
            <li>
                <a href="{% url 'books:book' book.id %}">{{ book.title }}</a>
                (เหลือ {{ book.available }} เล่ม)
            </li>
        {% empty %}
            <li>ยังไม่มีหนังสือ</li>
        {% endfor %}
    </ul>
{% endblock %}
```

`book.html`

```html
{% extends "books/layout.html" %}

{% block body %}
    <h1>{{ book.title }}</h1>
    <p>เหลือ {{ book.available }} จาก {{ book.copies }} เล่ม</p>

    <h2>คนที่ยืมอยู่</h2>
    <ul>
        {% for member in borrowers %}
            <li>{{ member }}</li>
        {% empty %}
            <li>ยังไม่มีคนยืม</li>
        {% endfor %}
    </ul>

    <h2>ยืมหนังสือ</h2>
    <form action="{% url 'books:borrow' book.id %}" method="post">
        {% csrf_token %}
        <select name="member">
            {% for member in non_borrowers %}
                <option value="{{ member.id }}">{{ member }}</option>
            {% endfor %}
        </select>
        <input type="submit" value="ยืม">
    </form>

    <a href="{% url 'books:index' %}">กลับหน้ารายการ</a>
{% endblock %}
```

### 4.6 รันเว็บ

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

(ตอนพิมพ์รหัสผ่านจะไม่เห็นตัวอักษร เป็นเรื่องปกติ)

1. เปิด http://127.0.0.1:8000/admin/ เพิ่ม `Book` 2–3 เล่ม และ `Member` 2 คน
2. เปิด http://127.0.0.1:8000/books/ กดชื่อหนังสือ แล้วลองยืม
3. กด `Ctrl+C` เพื่อหยุดเซิร์ฟเวอร์

---

## ขั้นที่ 5: ทดสอบ Django

Django สร้างฐานข้อมูลทดสอบแยกต่างหาก ข้อมูลจริงไม่ถูกแตะ `setUp` ใส่ข้อมูลตัวอย่างก่อนเทสต์ทุกข้อ และ `self.client` จำลองการเปิดหน้าเว็บ

`books/tests.py`

```python
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
```

```bash
python manage.py test
```

ต้องได้ `Ran 14 tests` และ `OK` (10 ข้อจากไฟล์นี้ + 4 ข้อจาก `tests1.py`)

**ลองใส่บั๊ก**
1. ใน `books/models.py` ฟังก์ชัน `is_valid_book` เปลี่ยน `and` เป็น `or`
2. รันเทสต์ จะไม่ผ่าน 2 ข้อ: `test_invalid_title`, `test_invalid_copies`
3. แก้กลับเป็น `and` แล้วรันใหม่

---

## ขั้นที่ 6: Selenium (ทดสอบในเบราว์เซอร์)

สร้างโฟลเดอร์ `selenium_tests`

`selenium_tests/days.html` หน้าเลือกจำนวนวันยืม

```html
<!DOCTYPE html>
<html lang="th">
    <head>
        <meta charset="utf-8">
        <title>Borrow Days</title>
        <script>
            document.addEventListener('DOMContentLoaded', () => {

                let days = 1;

                document.querySelector('#increase').onclick = () => {
                    if (days < 7) {
                        days++;
                    }
                    document.querySelector('h1').innerHTML = days;
                };

                document.querySelector('#decrease').onclick = () => {
                    if (days > 1) {
                        days--;
                    }
                    document.querySelector('h1').innerHTML = days;
                };
            });
        </script>
    </head>
    <body>
        <p>จำนวนวันที่ยืม (1-7 วัน)</p>
        <h1>1</h1>
        <button id="increase">+</button>
        <button id="decrease">-</button>
    </body>
</html>
```

`selenium_tests/tests.py`

```python
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
```

```bash
python selenium_tests/tests.py
```

Chrome จะเปิดขึ้นและกดปุ่มเอง ต้องได้ `Ran 5 tests` และ `OK` (ครั้งแรกต้องต่ออินเทอร์เน็ต เพื่อให้ Selenium โหลด ChromeDriver)

**ลองใส่บั๊ก:** เปลี่ยน `days < 7` เป็น `days <= 7` จะได้ `'8' != '7'` แล้วแก้กลับ

---

## ขั้นที่ 7: CI/CD ด้วย GitHub Actions

- **CI (Continuous Integration):** รวมโค้ดเข้า branch หลักบ่อยๆ และรันเทสต์อัตโนมัติ
- **CD (Continuous Delivery):** ปล่อยเวอร์ชันใหม่เป็นรอบสั้นๆ ถ้า deploy อัตโนมัติด้วยเรียกว่า Continuous Deployment
- โปรเจกต์นี้ทำส่วน CI

สร้างไฟล์ `.github/workflows/ci.yml` (YAML ใช้การเว้นวรรค ห้ามใช้ Tab)

```yaml
name: Testing
on: push

jobs:
  test_project:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v7
    - uses: actions/setup-python@v7
      with:
        python-version: "3.13"
    - name: Install requirements
      run: pip install -r requirements.txt
    - name: Run unit tests
      run: python manage.py test
```

ความหมาย: ทุกครั้งที่ push ให้เปิดเครื่อง Ubuntu → ดึงโค้ด → ติดตั้ง Python และ packages → รันเทสต์ Django (ไม่รวม Selenium)

สร้างไฟล์ `.gitignore`

```text
venv/
__pycache__/
*.pyc
db.sqlite3
.DS_Store
```

สร้าง repository **เปล่า** ชื่อ `library-app` บน GitHub แล้วรัน (เปลี่ยน `USERNAME`)

```bash
git init
git add .
git commit -m "Library app"
git branch -M main
git remote add origin https://github.com/USERNAME/library-app.git
git push -u origin main
```

ถ้า Git ถามชื่อผู้ใช้ ให้รัน `git config --global user.name "ชื่อ"` และ `git config --global user.email "อีเมล"` แล้ว commit ใหม่

เปิดแท็บ **Actions** ใน repository ต้องเห็นเครื่องหมายถูกสีเขียว

**ตัวอย่าง CI จับบั๊ก** (ควรแคปหน้าจอไว้ส่งอาจารย์)

1. เปลี่ยน `and` เป็น `or` ใน `books/models.py`
2. `git add .` → `git commit -m "Add bug"` → `git push` จะเห็นกากบาทสีแดง
3. แก้กลับ → `git add .` → `git commit -m "Fix bug"` → `git push` จะกลับเป็นสีเขียว

---

## ขั้นที่ 8: Docker

Docker รันแอปใน container ที่ตั้งค่าเหมือนกันทุกเครื่อง และเบากว่า VM เพราะไม่ต้องมีระบบปฏิบัติการของตัวเองทั้งชุด

`Dockerfile` (สูตรสร้าง image ของเว็บ)

```dockerfile
FROM python:3.13-slim
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

`.dockerignore`

```text
venv/
__pycache__/
*.pyc
db.sqlite3
.DS_Store
```

`docker-compose.yml` (รันเว็บกับ PostgreSQL พร้อมกัน)

```yaml
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_PASSWORD: postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 3s
      retries: 10

  web:
    build: .
    command: sh -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"
    environment:
      POSTGRES_HOST: db
    volumes:
      - .:/usr/src/app
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
```

- `healthcheck` และ `depends_on` ทำให้เว็บรอจนฐานข้อมูลพร้อม
- รหัสผ่าน `postgres` ใช้สำหรับฝึกเท่านั้น

เปิด Docker Desktop หยุด `runserver` เดิม แล้วรัน

```bash
docker compose up --build
```

เปิด Terminal ที่สอง

```bash
docker compose ps
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py test
```

เปิด http://localhost:8000/admin/ เพิ่มข้อมูล (เป็นฐานข้อมูลใหม่ แยกจาก SQLite) แล้วดูที่ http://localhost:8000/books/

เลิกใช้: `docker compose down` (ข้อมูลใน PostgreSQL ชุดนี้จะไม่กลับมา)

---

## ปัญหาที่พบบ่อย

| อาการ | วิธีแก้ |
|---|---|
| `No module named django` | ยังไม่เปิด venv หรือยังไม่ `pip install -r requirements.txt` |
| `no such table: books_book` | รัน `makemigrations` และ `migrate` |
| `TemplateDoesNotExist` | เช็กว่าไฟล์อยู่ใน `books/templates/books/` |
| `port is already allocated` | หยุด `runserver` หรือโปรแกรมอื่นที่ใช้พอร์ต 8000 |
| Actions ไม่ทำงาน | เช็กว่าไฟล์อยู่ที่ `.github/workflows/ci.yml` |
