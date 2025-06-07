from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models.clients.models import Client
from app.db.models.accounts.models import Account
from app.db.models.transactions.models import OperationLog, OperationType, Transaction, TransactionType

from app.services.bank_service import BankService


class ClientService:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_client(self, telegram_id: int) -> Client:
        client = Client(
            telegram_id=telegram_id
        )
        self.session.add(client)
        
        await self.session.commit()
        await self.session.refresh(client)
        
        return client
    
    async def get_client_by_telegram_id(self, telegram_id: int) -> Client:
        stmt = await self.session.execute(
            select(Client)
            .where(Client.telegram_id == telegram_id)
        )
        
        return stmt.scalar_one_or_none()
    
    async def open_account(self, bank_id: int, client_id: int) -> Optional[Client]:
        account = Account(
            bank_id=bank_id,
            client_id=client_id,
            balance=Decimal("0.00"),
        )
        
        self.session.add(account)
        await self.session.flush()
        
        self.session.add(OperationLog(
            client_id=client_id,
            action=OperationType.create_account,
            data={
                "account_id": account.id
            }
        ))
        
        await self.session.commit()
        
        return account

    async def close_account(self, account_id: int, client_id: int):
        result = await self.session.execute(
            select(Account)
            .where(Account.id == account_id)
        )
        account = result.scalar_one_or_none()
        
        if not account:
            raise ValueError(f"Account with id={account_id} not found")
        if account.balance > 0:
            raise ValueError(f"Account balance must be zero to close it")
        
        await self.session.delete(account)
        
        self.session.add(OperationLog(
            client_id=client_id,
            action=OperationType.close_account,
            data={
                "account_id": account_id,
            }
        ))
        
        await self.session.commit()
        
    async def deposit(self, account_id: int, amount: Decimal, client_id):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")
        
        result = await self.session.execute(
            select(Account)
            .where(Account.id == account_id)
        )
        
        account = result.scalar_one_or_none()
        
        account.balance += amount
        
        transaction = Transaction(
            from_account_id=None,
            to_account_id=account_id,
            amount=amount,
            fee="0.00",
            type=TransactionType.deposit,
        )
        
        self.session.add(transaction)
        
        self.session.add(OperationLog(
            client_id=client_id,
            action=OperationType.deposit,
            data={
                "client_id": client_id,
                "amount": amount,
            }
        ))
        
        await self.session.commit()

    async def withdraw(self, account_id: int, amount: Decimal, client_id: int):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")
        
        result = await self.session.execute(
            select(Account)
            .where(Account.id == account_id)
        )
        
        account = result.scalar_one_or_none()
        
        if not account:
            raise ValueError(f"Account with id={account_id} not found")
        if account.balance < amount:
            raise ValueError("Not enough money on balance")
        
        account.balance -= amount
        
        transaction = Transaction(
            from_account_id=account_id,
            to_account_id=None,
            amount=amount,
            fee="0.00",
            type=TransactionType.withdraw,
        )
        
        self.session.add(transaction)
        
        self.session.add(OperationLog(
            client_id=client_id,
            action=OperationType.withdraw,
            data={
                "client_id": client_id,
                "amount": str(amount),
            }
        ))
        
        await self.session.commit()

    async def transfer(
        self,
        from_account_id: int,
        to_account_id: int,
        amount: Decimal,
        client_id: int,
        fee_percent: Decimal = Decimal("0.001")
    ):
        stmt_from = await self.session.execute(
            select(Account)
            .where(Account.id == from_account_id)
        )
        stmt_to = await self.session.execute(
            select(Account)
            .where(Account.id == to_account_id)
        )
        
        from_account = stmt_from.scalar_one_or_none()
        to_account = stmt_to.scalar_one_or_none()
        
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")
        
        if from_account is None:
            raise ValueError(f"Client with id={from_account_id} not found")
        
        if to_account is None:
            raise ValueError(f"Client with id={to_account_id} not found")
        
        if from_account.bank_id != to_account.bank_id:
            fee_percent = Decimal("0.01")
        
        fee = amount * fee_percent
        total_amount = amount + fee
            
        if total_amount > from_account.balance:
            raise ValueError("Not enough money")
        
        from_account.balance -= total_amount
        to_account.balance += amount
        
        bank_service = BankService(self.session)
        bank_service.add_comission_to_bank(from_account.bank_id, fee)
        
        transaction = Transaction(
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            fee=fee_percent,
            type=TransactionType.transfer,
        )
        
        self.session.add(transaction)
        
        self.session.add(OperationLog(
            client_id=client_id,
            action=OperationType.transfer,
            data={
                "client_id": client_id,
                "amount": str(amount),
            }
        ))
        
        await self.session.commit()
