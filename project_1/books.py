from typing import Any
from fastapi import Body, FastAPI

app = FastAPI()

books: list[dict[str, str]] = [
    {"title": "Title One", "author": "Author One", "category": "science"},
    {"title": "Title Two", "author": "Author Two", "category": "science"},
    {"title": "Title Three", "author": "Author Three", "category": "history"},
    {"title": "Title Four", "author": "Author Four", "category": "math"},
    {"title": "Title Five", "author": "Author Five", "category": "math"},
    {"title": "Title Six", "author": "Author Two", "category": "math"},
]


@app.get("/books")
async def read_all_books() -> list[dict[str, str]]:
    return books


@app.get("/books/{book_title}")
async def read_book(book_title: str) -> dict[str, str]:
    for book in books:
        if book.get("title", "").casefold() == book_title.casefold():
            return book
    return {"Error": f"Book '{book_title}' not found"}


@app.get("/books/")
async def read_category_by_query(category: str) -> list[dict[str, str]]:
    books_to_return = []
    for book in books:
        if book.get("category", "").casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return


@app.get("/books/{author}")
async def get_books_by_author(author: str) -> list[dict[str, str]]:
    books_to_return = []
    for book in books:
        if book.get("author", "").casefold() == author.casefold():
            books_to_return.append(book)
    return books_to_return


@app.get("/books/{book_author}/")
async def read_author_category_by_query(
    book_author: str, category: str
) -> list[dict[str, str]]:
    books_to_return = []
    for book in books:
        if not book.get("author", "").casefold() == book_author.casefold():
            continue
        if not book.get("category", "").casefold() == category.casefold():
            continue
        books_to_return.append(book)
    return books_to_return


@app.post("/books/create_book")
async def create_book(new_book: Any = Body()) -> None:
    books.append(new_book)


@app.put("/books/update_book")
async def update_book(updated_book: dict[str, str] = Body()) -> None:
    for i in range(len(books)):
        if (
            books[i].get("title", "").casefold()
            == updated_book.get("title", "").casefold()
        ):
            books[i] = updated_book


@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str) -> None:
    for i in range(len(books)):
        if books[i].get("title", "").casefold() == book_title.casefold():
            books.pop(i)
            break
