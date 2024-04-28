from pydantic import BaseModel, Field

from . import HTTPSuccess


class SendTransactionDTO(BaseModel):
    userId: str = Field(description="User ID", examples=["user123"])
    amount: int = Field(gt=0, examples=[10 ** 24])
    to: str = Field(description="Recipient's account ID", examples=["recipient.near"])


class TxHashDict(BaseModel):
    tx_hash: str = Field(
        description="Transaction hash",
        examples=["HHVNiRJgRrRYT7NVCgPxCrc2SGoEMP1gZYqfvdU7252b"]
    )


class SendTransactionResponse(HTTPSuccess):
    result: TxHashDict
