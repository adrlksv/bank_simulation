from decimal import Decimal

from db.models.transactions.models import Transaction

from db.models.transactions.models import TransactionType, OperationType

from core.exceptions import (
    AccountNotFoundError,
    NotEnoughFundsError,
    NegativeAmountError,
    SameAccountTransferError,
    InvalidOperationError
)

from repositories.account_repository import AccountRepository
from repositories.bank_repository import BankRepository
from repositories.operation_log_repository import OperationLogRepository
from repositories.transaction_repository import TransactionRepository


class TransactionService:
    def __init__(
        self,
        account_repo: AccountRepository,
        bank_repo: BankRepository,
        transaction_repo: TransactionRepository,
        operation_log_repo: OperationLogRepository
    ):
        self.account_repo = account_repo
        self.bank_repo = bank_repo
        self.transaction_repo = transaction_repo
        self.operation_log_repo = operation_log_repo

    async def transfer(
        self,
        from_account_id: int,
        to_account_id: int,
        amount: Decimal,
        client_id: int
    ) -> Transaction:
        try:
            if amount <= 0:
                raise NegativeAmountError("Transfer amount must be positive")
                
            if from_account_id == to_account_id:
                raise SameAccountTransferError("Cannot transfer to the same account")

            from_account = await self.account_repo.get_account(from_account_id)
            to_account = await self.account_repo.get_account(to_account_id)

            if from_account.balance < amount:
                raise NotEnoughFundsError("Not enough funds")

            is_same_bank = from_account.bank_id == to_account.bank_id
            fee = (amount * Decimal("0.01")).quantize(Decimal("0.01")) if not is_same_bank else Decimal("0.00")

            await self.account_repo.update_balance(from_account_id, -amount)
            await self.account_repo.update_balance(to_account_id, amount - fee)

            if not is_same_bank:
                await self.bank_repo.add_commission(to_account.bank_id, fee)

            transaction = await self.transaction_repo.create_transaction(
                from_account_id,
                to_account_id,
                amount,
                fee,
                TransactionType.transfer
            )

            await self.operation_log_repo.log_operation(
                client_id,
                OperationType.transfer,
                {
                    "from_account": from_account_id,
                    "to_account": to_account_id,
                    "amount": str(amount),
                    "fee": str(fee)
                }
            )

            return transaction
        except (
            AccountNotFoundError,
            NotEnoughFundsError,
            NegativeAmountError,
            SameAccountTransferError
        ):
            raise
        except Exception as e:
            raise InvalidOperationError(f"Transfer failed: {str(e)}")
