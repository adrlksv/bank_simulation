from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models.accounts.models import Account


class TransactionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def transfer(self, from_account_id: int, to_account_id: int, amount: Decimal):
        stmt_from = await self.session.execute(
            select(Account).
            where(Account.id == from_account_id)
        )
        account_from = stmt_from.scalar_one_or_none()
        
        stmt_to = await self.session.execute(
            select(Account).
            where(Account.id == to_account_id)
        )
        account_to = stmt_to.scalar_one_or_none()
        
        if account_from.balance < amount:
            raise ValueError("Not enough funds")
        
        account_from -= amount
        account_to += amount
        
        await self.session.commit()
        
        return account_from, account_to
