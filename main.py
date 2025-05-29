from fastapi import FastAPI, Query, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Annotated, Union
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, HTTPException

from sqlalchemy.orm import Session
from db import crud, models, schemas
from db.database import SessionLocal, engine
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

SECRET_KEY = "19109197bd5e7c289b92b2b355083ea26c71dee2085ceccc19308a7291b2ea06"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Book(BaseModel):
    
    title: str = Field(..., min_length=3, max_length=100)
    pages: int = Field(..., ge=10)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def token_create(data: dict):
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

@app.post("/token")
async def token_get(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)): 
    user_db = db.query(models.User).filter(models.User.login == form_data.username, models.User.password==form_data.password).first()
    if not user.db:
        raise HTTPException(status_code=400, detail="---")


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
def get_books(author: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    if author in all_books:
        books = db.query(models.Book).filter(models.Author.name == author).all()
    
    if books:
        return books
    raise HTTPException(status_code=404, detail="автора незнайдено")
    

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

    