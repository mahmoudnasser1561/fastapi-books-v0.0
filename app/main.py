from fastapi import FastAPI, Path, Query, HTTPException, Depends, Request
from starlette import status
from fastapi.responses import FileResponse
from sqlalchemy import select, update, delete
from .database import engine, AsyncSessionLocal, AsyncSession, get_db
from .models import Base, Book, seed_data
from .schemas import BookRequest
import socket
import logging

hostname = socket.gethostname()
app = FastAPI()

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

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        await seed_data(db)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Served-By"] = hostname
    logging.info(f"Served {request.url.path} from {hostname}")
    return response

@app.get("/")
def home():
    return {"message": f"Hello from {hostname}"}


@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico") 