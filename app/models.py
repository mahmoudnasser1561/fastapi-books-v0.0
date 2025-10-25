from sqlalchemy import Column, Integer, String, select, func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession

class Base(DeclarativeBase):
    pass

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    description = Column(String)
    rating = Column(Integer)
    published_date = Column(Integer)

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