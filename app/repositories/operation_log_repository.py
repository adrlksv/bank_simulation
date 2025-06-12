from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.transactions.models import OperationLog, OperationType


class OperationLogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def log_operation(
        self,
        client_id: int,
        action: OperationType,
        data: dict,
    ) -> OperationLog:
        log = OperationLog(
            client_id=client_id,
            action=action,
            data=data
        )
        
        self.session.add(log)
        await self.session.flush()
        
        return log
    
    async def get_client_operations(self, client_id: int) -> list[OperationLog]:
        query = await self.session.execute(
            select(OperationLog)
            .where(OperationLog.client_id == client_id)
        )
        
        return query.scalars().all()
