import datetime
from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status


app = FastAPI()


class BookRequest(BaseModel):
    title: str = Field(min_length=3)
    author: str = Field(min_length=2)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(
        default=datetime.datetime.now().year, le=datetime.datetime.now().year
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new Book",
                "author": "Author",
                "description": "A book about..",
                "rating": 5,
                "published_date": 2025,
            }
        }
    }


class Book(BookRequest):
    id: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "title": "A new Book",
                "author": "Author",
                "description": "A book about..",
                "rating": 5,
            }
        }
    }

    def set_id(self, books: list["Book"]) -> None:
        self.id = 1 if len(books) == 0 else books[-1].id + 1


books: list[Book] = [
    Book(
        id=1,
        title="Computer Science Pro",
        author="codingwithroby",
        description="A very nice book",
        rating=5,
        published_date=2022,
    ),
    Book(
        id=2,
        title="Be Fast with FastAPI",
        author="codingwithroby",
        description="A great book!",
        rating=5,
    ),
    Book(
        id=3,
        title="Master Endpoints",
        author="codingwithroby",
        description="A awesome book!",
        rating=5,
    ),
    Book(
        id=4,
        title="HP1",
        author="Author 1",
        description="Book Description",
        rating=2,
    ),
    Book(
        id=5,
        title="HP2",
        author="Author 2",
        description="Book Description",
        rating=3,
    ),
    Book(
        id=6,
        title="HP3",
        author="Author 3",
        description="Book Description",
        rating=1,
    ),
]


@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books() -> list[Book]:
    return books


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)) -> Book:
    for book in books:
        if book_id == book.id:
            return book
    raise HTTPException(status_code=404, detail="Item not found")


@app.get("/books/by-rating", status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating: int = Query(gt=1, lt=6)) -> list[Book]:
    books_to_return: list[Book] = []
    for book in books:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return


@app.get("/books/by-year", status_code=status.HTTP_200_OK)
async def read_book_by_year(book_published: int) -> list[Book]:
    found: list[Book] = []
    for book in books:
        if book.published_date == book_published:
            found.append(book)
    return found


@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest) -> None:
    new_book = Book(**book_request.model_dump())
    new_book.set_id(books)
    books.append(new_book)


@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book_by_id(book: Book) -> None:
    changed = False
    for i in range(len(books)):
        if books[i].id == book.id:
            books[i] = book
            changed = True
            break
    if not changed:
        raise HTTPException(status_code=404, detail="Item not found")


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book_by_id(book_id: int = Path(gt=0)) -> None:
    deleted = False
    for i in range(len(books)):
        if books[i].id == book_id:
            books.pop(i)
            deleted = True
            break
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
