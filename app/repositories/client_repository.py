from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.exceptions import ClientNotFoundError

from db.models.clients.models import Client


class ClientRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_client(self, telegram_id: int) -> Client:
        client = Client(telegram_id=telegram_id)
        
        self.session.add(client)
        await self.session.flush()
        
        return client
    
    async def get_client(self, client_id: int) -> Client:
        query = await self.session.execute(
            select(Client)
            .where(Client.id == client_id)
        )
        
        client = query.scalar_one_or_none()
        if not client:
            raise ClientNotFoundError(f"Client with id={client_id} not found")
        
        return client
    
    async def get_client_by_telegram_id(self, telegram_id: int) -> Client:
        query = await self.session.execute(
            select(Client)
            .where(Client.telegram_id == telegram_id)
        )
        
        client = query.scalar_one_or_none()
        
        if not client:
            raise ClientNotFoundError(f"Client with telegram_id={telegram_id} not found")
        
        return client
