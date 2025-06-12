

class BaseException(Exception):
    def __init__(self,  message):
        super().__init__(message)
        self.message = message
        
    def __str__(self):
        return f"{self.message}"
    

class BankSystemError(BaseException):
    pass

class NotEnoughFundsError(BaseException):
    pass

class AccountNotFoundError(BaseException):
    pass

class BankNotFoundError(BaseException):
    pass

class BranchNotFoundError(BaseException):
    pass

class ClientNotFoundError(BaseException):
    pass

class InvalidOperationError(BaseException):
    pass

class AccountNotClosedError(BaseException):
    pass

class NegativeAmountError(BaseException):
    pass

class SameAccountTransferError(BaseException):
    pass
