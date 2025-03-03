from fastapi import APIRouter, Depends, Request
from redis.asyncio import Redis
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from starlette.responses import JSONResponse

from backend.database import get_session
from backend.v1.models import Wallet
from backend.v1.schemas import OperationRequest
from backend.validators import is_valid_uuid

router = APIRouter()

def get_redis(request: Request) -> Redis:
    return request.app.state.redis

@router.post('/{wallet_uuid}/operation')
async def wallet_operation(
        wallet_uuid: str,
        operation_request: OperationRequest,
        redis: Redis = Depends(get_redis),
        session_maker=Depends(get_session),
) -> JSONResponse:
    """Change wallet balance with selected operation"""

    if not is_valid_uuid(wallet_uuid):
        return JSONResponse(status_code=400, content={'message': 'Invalid wallet UUID'})
    async with session_maker as session:
        query = select(Wallet).where(Wallet.uuid == wallet_uuid)
        result = await session.execute(query)
        wallet = result.scalar_one_or_none()
        if not wallet:
            return JSONResponse(status_code=404, content={'message': 'Wallet not found'})
        if operation_request.operationType == 'DEPOSIT':
            wallet.balance += operation_request.amount
        else:
            wallet.balance -= operation_request.amount
            if wallet.balance < 0:
                return JSONResponse(status_code=400, content={'message': 'Not enough balance'})
        try:
            await session.commit()
            await redis.set(wallet_uuid, str(wallet.balance), ex=3600)
        except SQLAlchemyError:
            await session.rollback()
            return JSONResponse(status_code=400, content={'message': 'Operation failed'})
        return JSONResponse(status_code=200, content={'message': 'Operation succeeded'})


@router.get('/{wallet_uuid}')
async def get_balance(
        wallet_uuid: str,
        redis: Redis = Depends(get_redis),
        session_maker=Depends(get_session),
) -> JSONResponse:
    """Get wallet balance"""

    if not is_valid_uuid(wallet_uuid):
        return JSONResponse(status_code=400, content={'message': 'Invalid wallet UUID'})

    cached_balance = await redis.get(wallet_uuid)
    if cached_balance:
        return JSONResponse({'uuid': wallet_uuid, 'balance': str(cached_balance)})

    async with session_maker as session:
        query = select(Wallet).where(Wallet.uuid == wallet_uuid)
        result = await session.execute(query)
        wallet = result.scalar_one_or_none()
        if not wallet:
            return JSONResponse(status_code=404, content={'message': 'Wallet not found'})
    await redis.set(wallet_uuid, str(wallet.balance), ex=3600)
    return JSONResponse({'uuid': wallet_uuid, 'balance': str(wallet.balance)})
