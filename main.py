from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from db import crud, models, schemas
from db.database import SessionLocal, engine
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class Book(BaseModel):
    
    title: str = Field(..., min_length=3, max_length=100)
    pages: int = Field(..., ge=10)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    return {"message": "Привіт, FastAPI!"}


all_books = {
    "Джордж Оруелл": [
        {"title": "1984", "pages": 328},
        {"title": "Колгосп тварин", "pages": 112}
    ],
    "Стівен Кінг": [
        {"title": "Воно", "pages": 1138},
        {"title": "Сяйво", "pages": 447}
    ],
    "Артур Конан Дойл": [
        {"title": "Пригоди Шерлока Холмса", "pages": 307},
        {"title": "Собака Баскервілів", "pages": 256}
    ],
    "Джоан Роулінг": [
        {"title": "Гаррі Поттер і філософський камінь", "pages": 223},
        {"title": "Гаррі Поттер і таємна кімната", "pages": 251}
    ]
}

@app.get("/books/{author}", response_model=list[schemas.BookDB])
def get_books(author: str, db: Session = Depends(get_db)):
    if author in all_books:
        books = db.query(models.Book).filter(models.Author.name == author).all()
        return all_books[author]
    
    else:
        return {"massage": "книг такого автора незнайдено"}
    

@app.post("/books/")
def add_book(new_book: Book):
    if new_book.author not in all_books:
        all_books[new_book.author] = []

    all_books[new_book.author].append(new_book)
    return {"message": "книга додана"}


@app.delete("/books/")
def delete_book(title: str = Query(min_length=3, max_length=100), 
                author: str = Query(min_length=3, max_length=100)):
    
    if author in all_books:
        for book in all_books[author]:
            if book.title == title:
                all_books.remove(book)
                return {"message": "книгу видалено"}

    return{"message": "книгу не знайдено"}

    