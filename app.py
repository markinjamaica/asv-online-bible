#new change####
from os import environ

import sqlite3
import re

from flask import Flask, render_template, request, redirect


# Configure application
app = Flask(__name__)

#new change####
app.config['SQLALCHEMY_DATABASE_URL'] = environ.get(
    'DATABASE_URL') or 'asv.sqlite'


# List of Bible book abbreviations
abbreviated_books = [
    'Ge', 'Ex', 'Le', 'Nu', 'De', 'Jos', 'Jg', 'Ru', '1Sa', '2Sa', '1Ki', '2Ki', '1Ch', '2Ch', 'Ezr',
    'Neh', 'Es', 'Job', 'Ps', 'Pr', 'Ec', 'Ca', 'Isa', 'Jer', 'La', 'Eze', 'Da', 'Ho', 'Joe', 'Am', 'Ob',
    'Jo', 'Mic', 'Na', 'Hab', 'Zep', 'Hag', 'Zec', 'Mal', 'Mt', 'Mr', 'Lu', 'Joh', 'Ac', 'Ro', '1Co', '2Co',
    'Ga', 'Eph', 'Php', 'Col', '1Th', '2Th', '1Ti', '2Ti', 'Tit', 'Phm', 'Heb', 'Jas', '1Pe', '2Pe', '1Jo',
    '2Jo', '3Jo', 'Jude', 'Re'
]

# List of Bible books capitalized
book_names = [
    'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy', 'Joshua', 'Judges', 'Ruth',
    '1 Samuel', '2 Samuel', '1 Kings', '2 Kings', '1 Chronicles', '2 Chronicles', 'Ezra', 'Nehemiah',
    'Esther', 'Job', 'Psalms', 'Proverbs', 'Ecclesiastes', 'Song of Solomon', 'Isaiah', 'Jeremiah',
    'Lamentations', 'Ezekiel', 'Daniel', 'Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah', 'Micah', 'Nahum',
    'Habakkuk', 'Zephaniah', 'Haggai', 'Zechariah', 'Malachi', 'Matthew', 'Mark', 'Luke', 'John', 'Acts',
    'Romans', '1 Corinthians', '2 Corinthians', 'Galatians', 'Ephesians', 'Philippians', 'Colossians',
    '1 Thessalonians', '2 Thessalonians', '1 Timothy', '2 Timothy', 'Titus', 'Philemon', 'Hebrew', 'James',
    '1 Peter', '2 Peter', '1 John', '2 John', '3 John', 'Jude', 'Revelation'
]

# List of Bible books URL format
book_names_url = list(
    map(lambda name: re.sub(" ", "", name.lower()), book_names))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/preface")
def preface():
    return render_template("preface.html")


@app.route("/book")
def books():
    return render_template("books.html", book_names=book_names, abbreviated_books=abbreviated_books)


@app.route("/book/<book_url>")
def get_chapters(book_url):

    # Redirect if invalid input
    if book_url not in book_names_url:
        return redirect("/")

    book_number = int(book_names_url.index(book_url) + 1)

    # Book name is capitalized and matches the format in list book_names
    book = book_names[book_number - 1]

    # Define connection and cursor (cursor is used to interact with the database)
    try:
        connection = sqlite3.connect(
            "/home/markgauffin/asv-online-bible/asv.sqlite")
    except sqlite3.OperationalError:
        connection = sqlite3.connect(
            "asv.sqlite")
    cursor = connection.cursor()

    # SQL query to get number of chapters in selected book
    num_of_chapters = cursor.execute(
        "SELECT COUNT(DISTINCT(chapter)) FROM verses WHERE book=?", (book_number,))
    for row in num_of_chapters:
        num_of_chapters = row[0]

    return render_template("book.html", book_names_url=book_names_url, book_number=book_number, book=book, num_of_chapters=num_of_chapters, book_url=book_url)


@app.route("/book/<book_url>/<chapter>")
def get_chapter_text(book_url, chapter):

    # Redirect if invalid input
    if book_url not in book_names_url:
        return redirect("/")

    book_number = book_names_url.index(book_url) + 1
    book = book_names[int(book_number) - 1]

    # Define connection and cursor (cursor is used to interact with the database)
    try:
        connection = sqlite3.connect(
            "/home/markgauffin/asv-online-bible/asv.sqlite")
    except sqlite3.OperationalError:
        connection = sqlite3.connect(
            "asv.sqlite")
    cursor = connection.cursor()

    # SQL query to get number of chapters in selected book
    num_of_chapters = cursor.execute(
        "SELECT COUNT(DISTINCT(chapter)) FROM verses WHERE book=?", (book_number,))
    for row in num_of_chapters:
        num_of_chapters = row[0]

    # Check for invalid input
    try:
        chapter = int(chapter)
    except:
        return redirect("/")

    if chapter < 1 or chapter > num_of_chapters:
        return redirect("/")

    # SQL query to get number of verses in selected book
    num_of_verses = cursor.execute(
        "SELECT COUNT(DISTINCT(verse)) FROM verses WHERE book=? AND chapter=?", (book_number, chapter))
    for row in num_of_verses:
        num_of_verses = row[0]

    # SQL query to get chapter text
    text_row = cursor.execute(
        "SELECT text, verse FROM verses WHERE book=? AND chapter=?", (book_number, chapter))

    return render_template("chapter.html", book_url=book_url, book=book, text_row=text_row,
                           chapter=chapter, num_of_verses=num_of_verses, num_of_chapters=num_of_chapters)
