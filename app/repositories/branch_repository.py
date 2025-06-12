from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.exceptions import BranchNotFoundError, ClientNotFoundError
from db.models.clients.models import Client
from db.models.branches.models import Branch


class BranchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_branch(self, bank_id: int) -> Branch:
        branch = Branch(
            bank_id=bank_id,
            balance=Decimal("0.00")
        )
        
        self.session.add(branch)
        await self.session.flush()
        
        return branch
    
    async def get_branch(self, branch_id: int) -> Branch:
        query = await self.session.execute(
            select(Branch)
            .where(Branch.id == branch_id)
        )
        
        branch = query.scalar_one_or_none()
        if not branch:
            raise BranchNotFoundError(f"Branch with id={branch_id} not found")
        
        return branch
    
    async def update_branch_balance(self, branch_id: int, amount: Decimal):
        branch = await self.get_branch(branch_id)
        branch.balance += amount
        
        await self.session.flush()
        
        return branch
    
    async def get_bank_branches(self, bank_id: int) -> list[Branch]:
        query = await self.session.execute(
            select(Branch)
            .where(Branch.bank_id == bank_id)
        )
        
        return query.scalars().all()
