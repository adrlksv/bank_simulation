from sqlalchemy import Integer, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Branch(Base):
    __tablename__ = "branch"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False,
        index=True,
    )
    bank_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("bank.id"),
        nullable=False,
    )
    balance: Mapped[float] = mapped_column(
        Numeric(12, 2),
        default=0,
    )
