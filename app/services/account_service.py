from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select, update

from decimal import Decimal

from app.db.models.clients.models import Client
from app.db.models.accounts.models import Account


class AccountService:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_account(self, bank_id: int, client_id: int) -> Account:
        account = Account(
            bank_id=bank_id,
            client_id=client_id,
            balance=Decimal("0.00"),
        )
        self.session.add(account)
        
        await self.session.commit()
        await self.session.refresh(account)
        
        return account
    
    async def deposit(self, account_id: int, amount: Decimal):
        result = await self.session.execute(
            select(Account).
            where(Account.id == account_id)
        )
        account = result.scalar_one_or_none()
        account.balance += amount
        
        await self.session.commit()
        
        return account
    
    async def withdraw(self, account_id: int, amount: Decimal):
        result = await self.session.execute(
            select(Account).
            where(Account.id == account_id)
        )
        account = result.scalar_one_or_none()
        
        if account.balance < amount:
            raise ValueError("Not enough funds")
        account.balance -= amount
        
        await self.session.commit()
        
        return account

    async def get_accounts(self, client_id: int) -> list[Account]:
        stmt = await self.session.execute(
            select(Account)
            .where(Account.client_id == client_id)
        )
        
        return stmt.scalars().all()
