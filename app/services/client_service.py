from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models.clients.models import Client
from app.db.models.accounts.models import Account
from app.db.models.transactions.models import OperationLog, OperationType


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
