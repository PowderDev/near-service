import logging
import os
from contextlib import asynccontextmanager
from typing import Annotated

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Header
from fastapi.exceptions import RequestValidationError
from py_near.account import Account

from dtos import HTTPError
from dtos.account import GetAccountBalanceResponse
from dtos.transaction import SendTransactionDTO, SendTransactionResponse
from utils.common import get_tx_error_name
from utils.http import http_error

load_dotenv()

NEAR_PRIVATE_KEY = os.getenv("NEAR_PRIVATE_KEY")
NEAR_ACCOUNT_ID = os.getenv("NEAR_ACCOUNT_ID")
NEAR_RPC_URL = os.getenv("NEAR_RPC_URL")
API_SECRET = os.getenv("API_SECRET")

if not NEAR_PRIVATE_KEY or not NEAR_ACCOUNT_ID or not NEAR_RPC_URL or not API_SECRET:
    raise ValueError("Missing environment variables")

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] | %(levelname)s | %(message)s"
)

logger = logging.getLogger()

file_handler = logging.FileHandler("info.log")
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

acc = Account(NEAR_ACCOUNT_ID, NEAR_PRIVATE_KEY, NEAR_RPC_URL)


@asynccontextmanager
async def lifespan(_):
    await acc.startup()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="NEAR service",
    responses={
        500: {"model": HTTPError, "description": "Internal server error"},
        401: {"model": HTTPError, "description": "Unauthorized"},
        422: {"model": HTTPError}
    },
)


@app.exception_handler(Exception)
def exception_handler(_, exc):
    logger.error(str(exc))
    return http_error(f"Internal server error: {str(exc)}", 500)


@app.exception_handler(RequestValidationError)
def http_exception_handler(_, exc):
    logger.error(exc.errors()[0])
    first_error = exc.errors()[0]
    error_string = f"`{first_error["loc"][-1]}` {first_error["msg"].lower()}"
    return http_error(error_string, 422)


@app.get(
    "/",
    responses={200: {"model": GetAccountBalanceResponse}}
)
async def get_account_balance(x_api_secret: Annotated[str | None, Header()] = None):
    if x_api_secret != API_SECRET:
        return http_error("Unauthorized. Invalid X-API-Secret header", 401)

    result = await acc.get_balance()
    logger.info(f"Account balance: {result} yoktoNEAR")
    return GetAccountBalanceResponse(result={"balance": result})


@app.post(
    "/send-transaction",
    status_code=201,
    responses={
        201: {"model": SendTransactionResponse, "description": "Transaction sent successfully"},
        400: {"model": HTTPError, "description": "Invalid transaction data"},
    }
)
async def send_transaction(
        dto: SendTransactionDTO,
        x_api_secret: Annotated[str | None, Header()] = None,
):
    if x_api_secret != API_SECRET:
        return http_error("Unauthorized. Invalid X-API-Secret header", 401)

    try:
        result = await acc.send_money(dto.to, dto.amount)
    except BaseException as e:
        logger.error(f"Failed to send transaction. Reason: {str(e)}")
        return http_error("Failed to send transaction. Please check your credentials", 401)

    has_failed = bool(result.status.get("Failure"))

    if has_failed:
        logger.error(
            f"Transaction to {dto.userId} ({dto.to}) failed. " +
            f"Reason: {result.status['Failure']}"
        )

        return http_error(
            f"Transaction {result.transaction.hash} failed. " +
            f"Reason: {get_tx_error_name(result)}"
        )

    logger.info(
        f"Transaction to {dto.userId} ({dto.to}) succeeded. " +
        f"Amount: {dto.amount} yoktoNEAR"
    )

    return SendTransactionResponse(result={"tx_hash": result.transaction.hash})


if __name__ == "__main__":
    uvicorn.run(app, host="", port=4000)
