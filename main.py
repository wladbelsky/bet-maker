import uvicorn
from fastapi import FastAPI

from config import WEB_SERVER_HOST, WEB_SERVER_PORT, DB_CONFIG
from database.postgres import Database
from routes.bets import router as bets_router
from routes.events import router as events_router


async def prepare_db() -> None:
    db = Database(DB_CONFIG)
    await db.prepare_tables()

app = FastAPI()
app.add_event_handler("startup", prepare_db)
app.include_router(bets_router)
app.include_router(events_router)


if __name__ == '__main__':
    uvicorn.run(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
