from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.transactions.models import Transaction, TransactionType


class TransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_transaction(
        self,
        from_account_id: int,
        to_account_id: int,
        amount: Decimal,
        fee: Decimal,
        type: TransactionType,
    ) -> Transaction:
        transaction = Transaction(
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            fee=fee,
            type=type,
        )
        
        self.session.add(transaction)
        await self.session.flush()
        
        return transaction
    
    async def get_client_transactions(self, client_id: int) -> list[Transaction]:
        query = await self.session.execute(
            select(Transaction)
            .where(Transaction.from_account_id == client_id)
        )
        
        return query.scalars().all()
