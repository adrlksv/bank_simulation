from decimal import Decimal

from core.exceptions import (
    BankNotFoundError,
    BranchNotFoundError,
    InvalidOperationError
)
from db.models.banks.models import Bank
from db.models.branches.models import Branch
from repositories.account_repository import AccountRepository
from repositories.bank_repository import BankRepository
from repositories.branch_repository import BranchRepository


class BankService:
    def __init__(
        self,
        bank_repo: BankRepository,
        branch_repo: BranchRepository,
        account_repo: AccountRepository
    ):
        self.bank_repo = bank_repo
        self.branch_repo = branch_repo
        self.account_repo = account_repo

    async def create_bank(self, name: str) -> Bank:
        try:
            return await self.bank_repo.create_bank(name)
        except Exception as e:
            raise InvalidOperationError(f"Failed to create bank: {str(e)}")

    async def get_bank(self, bank_id: int) -> Bank:
        try:
            return await self.bank_repo.get_bank(bank_id)
        except BankNotFoundError:
            raise
        except Exception as e:
            raise InvalidOperationError(f"Failed to get bank: {str(e)}")

    async def create_branch(self, bank_id: int) -> Branch:
        try:
            await self.bank_repo.get_bank(bank_id)
            return await self.branch_repo.create_branch(bank_id)
        except BankNotFoundError:
            raise
        except Exception as e:
            raise InvalidOperationError(f"Failed to create branch: {str(e)}")

    async def get_branches(self, bank_id: int) -> list[Branch]:
        try:
            await self.bank_repo.get_bank(bank_id)
            return await self.branch_repo.get_bank_branches(bank_id)
        except BankNotFoundError:
            raise
        except Exception as e:
            raise InvalidOperationError(f"Failed to get branches: {str(e)}")

    async def deposit_to_branch(self, branch_id: int, amount: Decimal) -> Branch:
        try:
            if amount <= 0:
                raise InvalidOperationError("Deposit amount must be positive")
                
            return await self.branch_repo.update_branch_balance(branch_id, amount)
        except BranchNotFoundError:
            raise
        except Exception as e:
            raise InvalidOperationError(f"Failed to deposit to branch: {str(e)}")

    async def get_total_commission(self, bank_id: int) -> Decimal:
        try:
            bank = await self.bank_repo.get_bank(bank_id)
            return bank.comission_income
        except BankNotFoundError:
            raise
        except Exception as e:
            raise InvalidOperationError(f"Failed to get commission: {str(e)}")

    async def get_total_client_balance(self, bank_id: int) -> Decimal:
        try:
            return await self.account_repo.get_bank_accounts_total(bank_id)
        except Exception as e:
            raise InvalidOperationError(f"Failed to get client balance: {str(e)}")

    async def get_summary(self, bank_id: int) -> dict:
        try:
            bank = await self.bank_repo.get_bank(bank_id)
            total_balance = await self.get_total_client_balance(bank_id)
            commission = await self.get_total_commission(bank_id)
            branches = await self.get_branches(bank_id)
            accounts_count = await self.account_repo.get_bank_accounts_count(bank_id)
            
            return {
                "bank_name": bank.name,
                "client_total_balance": total_balance,
                "comission_income": commission,
                "total_accounts": accounts_count,
                "total_branches": len(branches),
            }
        except BankNotFoundError:
            raise
        except Exception as e:
            raise InvalidOperationError(f"Failed to get summary: {str(e)}")
