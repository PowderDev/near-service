from pydantic import BaseModel, Field

from . import HTTPSuccess


class AccountBalanceDict(BaseModel):
    balance: int = Field(
        description="Account balance in yoctoNEAR",
        examples=[1000000000000000000000000]
    )


class GetAccountBalanceResponse(HTTPSuccess):
    result: AccountBalanceDict
