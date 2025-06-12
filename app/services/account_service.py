from decimal import Decimal

from core.exceptions import AccountNotFoundError, InvalidOperationError, NegativeAmountError, NotEnoughFundsError

from db.models.accounts.models import Account
from db.models.transactions.models import OperationType, Transaction, TransactionType
from repositories.account_repository import AccountRepository
from repositories.operation_log_repository import OperationLogRepository
from repositories.transaction_repository import TransactionRepository


class AccountService:
    def __init__(
        self,
        account_repo: AccountRepository,
        transaction_repo: TransactionRepository,
        operation_log_repo: OperationLogRepository
    ):
        self.account_repo = account_repo
        self.transaction_repo = transaction_repo
        self.operation_log_repo = operation_log_repo
        
    async def create_account(self, bank_id: int, client_id: int) -> Account:
        try:
            account = await self.account_repo.create_account(bank_id=bank_id, client_id=client_id)
            await self.operation_log_repo.log_operation(
                client_id,
                OperationType.create_account,
                {
                    "account_id": account.id
                }
            )
            return account
        except Exception as e:
            raise InvalidOperationError(f"Failed to create account: {str(e)}")
    
    async def deposit(self, account_id: int, amount: Decimal, client_id: int):
        try:
            if amount <= 0:
                raise NegativeAmountError("Deposit amount must be positive")
            
            account = await self.account_repo.update_balance(account_id, amount)
            
            await self.transaction_repo.create_transaction(
                None, account_id, amount, Decimal("0.00"), TransactionType.deposit
            )
            
            await self.operation_log_repo.log_operation(
                client_id,
                OperationType.deposit,
                {
                    "account_id": account_id, 
                    "amount": str(amount)
                }
            )
            
            return account
        except AccountNotFoundError:
            raise
        except Exception as e:
            raise InvalidOperationError(f"Deposit failed: {str(e)}")
    
    async def withdraw(self, account_id: int, amount: Decimal, client_id: int) -> Account:
        try:
            if amount <= 0:
                raise NegativeAmountError("Withdrawal amount must be positive")
            
            account = await self.account_repo.get_account(account_id)
            if account.balance < amount:
                raise NotEnoughFundsError("Not enough funds")
            
            account = await self.account_repo.update_balance(account_id, -amount)
            
            await self.transaction_repo.create_transaction(
                account_id, None, amount, Decimal("0.00"), TransactionType.withdraw
            )
            
            await self.operation_log_repo.log_operation(
                client_id,
                OperationType.withdraw,
                {
                    "account_id": account_id,
                    "amount": str(amount)
                }
            )
            
            return account
        except (AccountNotFoundError, NotEnoughFundsError):
            raise
        except Exception as e:
            raise InvalidOperationError(f"Withdrawal failed: {str(e)}")
        
    async def close_account(self, account_id: int, client_id: int) -> None:
        try:
            account = await self.account_repo.get_account(account_id)
            if account.balance != 0:
                raise InvalidOperationError("Account balance must be zero to close it")
            
            await self.account_repo.delete_account(account_id)
            
            await self.operation_log_repo.log_operation(
                client_id,
                OperationType.close_account,
                {
                    "account_id": account_id
                }
            )
        except (AccountNotFoundError, InvalidOperationError):
            raise
        except Exception as e:
            raise InvalidOperationError(f"Failed to close account: {str(e)}")
    
    async def get_account_balance(self, account_id: int) -> Decimal:
        try:
            account = await self.account_repo.get_account(account_id)
            
            return account.balance
        except AccountNotFoundError:
            raise
        except Exception as e:
            raise InvalidOperationError(f"Failed to get balance: {str(e)}")

    async def get_client_accounts(self, client_id: int) -> list[Account]:
        try:
            return await self.account_repo.get_client_accounts(client_id)
        except Exception as e:
            raise InvalidOperationError(f"Failed to get client accounts: {str(e)}")
