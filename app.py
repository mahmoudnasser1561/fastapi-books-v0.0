from typing import Optional
from fastapi import FastAPI, Path, Query, HTTPException, Depends
from pydantic import BaseModel, Field
from starlette import status
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import Column, Integer, String, select, update, delete, func
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()

# Database setup - Use asyncpg driver
DATABASE_URL = f"postgresql+asyncpg://{os.getenv('POSTGRES_USER', 'postgres')}:{os.getenv('POSTGRES_PASSWORD', 'password')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'books')}"
engine = create_async_engine(DATABASE_URL, echo=False)  
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

app = FastAPI()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    description = Column(String)
    rating = Column(Integer)
    published_date = Column(Integer)


class BookRequest(BaseModel):
    id: Optional[int] = Field(description='ID is not needed on create', default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1999, lt=2031)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "codingwithroby",
                "description": "A new description of a book",
                "rating": 5,
                'published_date': 2029
            }
        }
    }


@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book))
    return result.scalars().all()

@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if book is None:
        raise HTTPException(status_code=404, detail='Item not found')
    return book

@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating: int = Query(gt=0, lt=6), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).where(Book.rating == book_rating))
    return result.scalars().all()

@app.get("/books/publish/", status_code=status.HTTP_200_OK)
async def read_books_by_publish_date(published_date: int = Query(gt=1999, lt=2031), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).where(Book.published_date == published_date))
    return result.scalars().all()

@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest, db: AsyncSession = Depends(get_db)):
    new_book = Book(**book_request.model_dump(exclude={'id'})) 
    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)
    return new_book

@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest, db: AsyncSession = Depends(get_db)):
    if book.id is None:
        raise HTTPException(status_code=400, detail='ID is required for update')
    result = await db.execute(select(Book).where(Book.id == book.id))
    db_book = result.scalar_one_or_none()
    if db_book is None:
        raise HTTPException(status_code=404, detail='Item not found')
    await db.execute(
        update(Book).where(Book.id == book.id).values(**book.model_dump(exclude_unset=True))
    )
    await db.commit()

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).where(Book.id == book_id))
    db_book = result.scalar_one_or_none()
    if db_book is None:
        raise HTTPException(status_code=404, detail='Item not found')
    await db.execute(delete(Book).where(Book.id == book_id))
    await db.commit()

async def seed_data(db: AsyncSession):
    result = await db.execute(select(func.count()).select_from(Book))
    count = result.scalar()
    if count == 0:
        initial_books = [
            Book(id=1, title='Computer Science Pro', author='codingwithroby', description='A very nice book!', rating=5, published_date=2030),
            Book(id=2, title='Be Fast with FastAPI', author='codingwithroby', description='A great book!', rating=5, published_date=2030),
            Book(id=3, title='Master Endpoints', author='codingwithroby', description='A awesome book!', rating=5, published_date=2029),
            Book(id=4, title='HP1', author='Author 1', description='Book Description', rating=2, published_date=2028),
            Book(id=5, title='HP2', author='Author 2', description='Book Description', rating=3, published_date=2027),
            Book(id=6, title='HP3', author='Author 3', description='Book Description', rating=1, published_date=2026)
        ]
        db.add_all(initial_books)
        await db.commit()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        await seed_data(db)