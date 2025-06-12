from core.exceptions import AccountNotFoundError, ClientNotFoundError, InvalidOperationError
from db.models.accounts.models import Account
from db.models.clients.models import Client
from db.models.transactions.models import OperationType
from repositories.account_repository import AccountRepository
from repositories.client_repository import ClientRepository
from repositories.operation_log_repository import OperationLogRepository


class ClientService:
    def __init__(
        self,
        client_repo: ClientRepository,
        account_repo: AccountRepository,
        operation_log_repo: OperationLogRepository
    ):
        self.client_repo = client_repo
        self.account_repo = account_repo
        self.operation_log_repo = operation_log_repo

    async def create_client(self, telegram_id: int) -> Client:
        try:
            return await self.client_repo.create_client(telegram_id)
        except Exception as e:
            raise InvalidOperationError(f"Failed to create client: {str(e)}")

    async def get_client(self, client_id: int) -> Client:
        try:
            return await self.client_repo.get_client(client_id)
        except ClientNotFoundError:
            raise
        except Exception as e:
            raise InvalidOperationError(f"Failed to get client: {str(e)}")

    async def get_client_by_telegram_id(self, telegram_id: int) -> Client:
        try:
            return await self.client_repo.get_client_by_telegram_id(telegram_id)
        except ClientNotFoundError:
            raise
        except Exception as e:
            raise InvalidOperationError(f"Failed to get client: {str(e)}")

    async def open_account(self, bank_id: int, client_id: int) -> Account:
        try:
            await self.client_repo.get_client(client_id)  # Check client exists
            account = await self.account_repo.create_account(bank_id, client_id)
            
            await self.operation_log_repo.log_operation(
                client_id,
                OperationType.create_account,
                {"account_id": account.id}
            )
            
            return account
        except (ClientNotFoundError, AccountNotFoundError):
            raise
        except Exception as e:
            raise InvalidOperationError(f"Failed to open account: {str(e)}")

    async def get_client_accounts(self, client_id: int) -> list[Account]:
        try:
            await self.client_repo.get_client(client_id)  # Check client exists
            return await self.account_repo.get_client_accounts(client_id)
        except ClientNotFoundError:
            raise
        except Exception as e:
            raise InvalidOperationError(f"Failed to get client accounts: {str(e)}")
