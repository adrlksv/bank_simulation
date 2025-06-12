from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from core.exceptions import AccountNotClosedError, AccountNotFoundError
from db.models.accounts.models import Account


class AccountRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_account(self, account_id: int) -> Account:
        query = await self.session.execute(
            select(Account)
            .where(Account.id == account_id)
        )
        
        account = query.scalar_one_or_none()
        if not account:
            raise AccountNotFoundError(f"Account with id={account_id} not found")
        
        return account
    
    async def create_account(self, bank_id: int, client_id: int):
        account = Account(
            bank_id=bank_id,
            client_id=client_id,
            balance=Decimal("0.00")
        )
        self.session.add()
        
        await self.session.flush()
        
        return account
    
    async def update_balance(self, account_id: int, amount: Decimal) -> Account:
        account = self.get_accout(account_id)
        account.balance += amount
        
        await self.session.flush()
        
        return account
    
    async def delete_account(self, account_id: int) -> None:
        account = self.get_accout(account_id)
        if account.balance != 0:
            raise AccountNotClosedError("Account balance must be zero to close it")
        
        await self.session.delete(account)
        await self.session.flush()
        
    async def get_client_accounts(self, client_id: int) -> list[Account]:
        query = await self.session.execute(
            select(Account)
            .where(Account.client_id == client_id)
        )
        
        return query.scalars().all()
    
    async def get_bank_accounts_total(self, bank_id: int) -> Decimal:
        query = await self.session.execute(
            select(func.sum(Account.balance))
            .where(Account.bank_id == bank_id)
        )
        
        return query.scalar()
