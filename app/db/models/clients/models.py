from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class Client(Base):
    __tablename__ = "client"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False,
        index=True,
    )
    telegram_id: Mapped[int] = mapped_column(unique=True)
