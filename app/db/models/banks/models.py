from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Bank(Base):
    __tablename__ = "bank"
    
    id: Mapped[int] = mapped_column(
        primary_key=True, 
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )
    comission_income: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
