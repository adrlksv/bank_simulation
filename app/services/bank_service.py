from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.models.banks.models import Bank
from app.db.models.branches.models import Branch
from app.db.models.accounts.models import Account


class BankService:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_bank(self, name: str) -> Bank:
        bank = Bank(
            name=name,
        )
        
        self.session.add(bank)
        
        await self.session.commit()
        await self.session.refresh(bank)
        
        return bank

    async def get_bank(self, bank_id: int) -> Bank:
        stmt = await self.session.execute(
            select(Bank).
            where(Bank.id == bank_id)
        )
        
        return stmt.scalar_one_or_none()

        
    async def create_branch(self, bank_id: int) -> Branch:
        branch = Branch(
            bank_id=bank_id,
            balance=Decimal("0.00")
        )
        
        self.session.add(branch)
        
        await self.session.commit()
        await self.session.refresh(branch)
        
        return branch
    
    async def get_branches(self, bank_id: int) -> list[Branch]:
        stmt = await self.session.execute(
            select(Branch)
            .where(Branch.bank_id == bank_id)
        )
        
        branches = stmt.scalars().all()
        
        return branches

    async def deposit_to_branch(self, branch_id, amount: Decimal) -> Branch:
        stmt = await self.session.execute(
            select(Branch)
            .where(Branch.id == branch_id)
        )
        
        branch = stmt.scalar_one_or_none()
        if branch is None:
            raise ValueError(f"Branch with id={branch_id} not found")
        
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")
        
        branch.balance += amount
        
        await self.session.commit()
        
        return branch
    
    async def get_total_comission(self, bank_id: int) -> Decimal:
        stmt = await self.session.execute(
            select(Bank.comission_income)
            .where(Bank.id == bank_id)
        )
        return stmt.scalar_one_or_none() or Decimal("0.00")
    
    async def get_total_client_balance(self, bank_id: int) -> Decimal:
        stmt = await self.session.execute(
            select(func.sum(Account.balance))
            .where(Account.bank_id == bank_id)
        )
        
        return stmt.scalar_one_or_none()
    
    async def get_summary(self, bank_id: int) -> dict:
        bank = await self.get_bank(bank_id=bank_id)
        if not bank:
            raise ValueError(f"Bank with id={bank_id} not found")
        
        total_balance = await self.get_total_client_balance(bank_id=bank_id)
        comission = await self.get_total_comission(bank_id=bank_id)
        
        result = await self.session.execute(
            select(func.count(Account.id))
            .where(Account.bank_id == bank_id)
        )
        
        account_count = result.scalar_one()
        
        result = await self.session.execute(
            select(func.count(Branch.id))
            .where(Branch.bank_id == bank_id)
        )
        
        branch_count = result.scalar_one()
        
        return {
            "bank_name": bank.name,
            "client_total_balance": total_balance,
            "comission_income": comission,
            "total_accounts": account_count,
            "total_branches": branch_count,
        }

    async def add_comission_to_bank(self, bank_id: int, fee: Decimal):
        bank = await self.get_bank(bank_id)
        if bank is None:
            raise ValueError("Bank not found")
        
        bank.comission_income += fee
        
        await self.session.commit()
