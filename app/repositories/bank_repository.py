from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.exceptions import BankNotFoundError

from db.models.banks.models import Bank


class BankRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_bank(self, name: str) -> Bank:
        bank = Bank(
            name=name
        )
        
        self.session.add(bank)
        await self.session.flush()
        
        return bank
    
    async def get_bank(self, bank_id: int) -> Bank:
        query = await self.session.execute(
            select(Bank)
            .where(Bank.id == bank_id)
        )
        
        bank = query.scalar_one_or_none()
        if not bank:
            raise BankNotFoundError(f"Bank with id={bank_id} not found")
        
        return bank
    
    async def add_comission(self, bank_id: int, amount: Decimal) -> Bank:
        bank = await self.get_bank(bank_id)
        bank.comission_income += amount
        
        await self.session.flush()
        
        return bank
    
    async def get_all_banks(self) -> list[Bank]:
        query = await self.session.execute(
            select(Bank)
        )
        
        return query.scalars().all()
