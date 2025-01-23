from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis
from starlette.middleware.cors import CORSMiddleware

from backend import v1
from backend.config import get_redis_url
from backend.exception_handler import register_error_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await Redis.from_url(get_redis_url(),
                                    decode_responses=True,
                                    health_check_interval=30,
                                    retry_on_timeout=True,
                                    )
    app.state.redis = redis
    yield
    await redis.aclose()


app = FastAPI(title='Wallet', openapi_url='/api/openapi.json', docs_url='/api/docs', lifespan=lifespan)

app.include_router(v1.routers.wallets.router, prefix='/api/v1/wallets')


origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST'],
    allow_headers=['Access-Control-Allow-Credentials', 'Access-Control-Allow-Origin', 'Content-Type',
                   'Set-Cookie', 'Access-Control-Allow-Headers'],
)

register_error_handlers(app)
