from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models.accounts.models import Account
from app.db.models.transactions.models import Transaction, TransactionType


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
        
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")
        
        if account_from.balance < amount:
            raise ValueError("Not enough funds")
        
        is_other_bank = account_from.bank_id != account_to.bank_id
        
        fee = (amount * Decimal("0.01")).quantize(Decimal("0.01")) if is_other_bank else Decimal("0.00")
        
        account_from.balance -= amount
        account_to.balance += (amount - fee)
        
        transaction = Transaction(
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            fee=fee,
            type=TransactionType.transfer,
        )
        
        self.session.add(transaction)
        await self.session.commit()
        
        return transaction
