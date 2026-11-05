from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import Integer, String, Text, DateTime, func
from datetime import datetime


class Base(DeclarativeBase):
    pass


class CollectedData(Base):
    __tablename__ = "collecteddata"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    item_id : Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
