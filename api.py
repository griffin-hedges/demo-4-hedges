from fastapi import APIRouter, HTTPException
from typing import Dict, Optional
from utils import create_and_fund_wallet, transfer_asa, get_asa_balance, burn_tokens
import logging
from pydantic import BaseModel

class BuyCoinsRequest(BaseModel):
    amount: int
    asa_id: int
    address: str
    price: float

class GetBalanceRequest(BaseModel):
    address: str
    asa_id: int

class SellCoinsRequest(BaseModel):
    address: str
    asa_id: int
    amount: int

api_router = APIRouter()
logger = logging.getLogger(__name__)

@api_router.get("/")
def read_root():
    return {"message": "API is running"}

@api_router.post("/wallet/generate")
async def generate_wallet():
    try:
        wallet = create_and_fund_wallet()
        return {
            "message": "Wallet generated successfully",
            "wallet_address": wallet["address"],
            "private_key": wallet["private_key"],
            "mnemonic": wallet["mnemonic"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/coins/sell")
async def sell_coins(request: SellCoinsRequest):
    try:
        # Add sell coins logic here
        burn_tokens(request.address, request.asa_id, request.amount)
        return {"message": f"Successfully sold {request.amount} {request.asa_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/coins/buy") 
async def buy_coins(request: BuyCoinsRequest):
    logger.info(f"Received buy_coins request with amount: {request.amount}, asa_id: {request.asa_id}, address: {request.address}, price: {request.price}")

    try:
        transfer_asa(request.address, request.asa_id, request.amount, request.price)
        
        return {
            "message": f"Successfully bought {request.amount} {request.asa_id} at {request.price}",
            "address": request.address,
            "asa_id": request.asa_id,
            "price": request.price
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/coins/balance")
async def get_balance(address: str, asa_id: int):
    try:
        balance = get_asa_balance(address, asa_id)
        return {
            "message": f"Successfully got balance for {address} {asa_id}",
            "address": address,
            "asa_id": asa_id,
            "balance": balance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
