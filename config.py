from os import getenv

WEB_SERVER_HOST = getenv("WEB_SERVER_HOST")
WEB_SERVER_PORT = getenv("WEB_SERVER_PORT")

DB_CONFIG = {
    'engine': getenv('DB_ENGINE', 'postgresql+asyncpg'),
    'user': getenv('DB_USER'),
    'password': getenv('DB_PASSWORD'),
    'host': getenv('DB_HOST'),
    'port': getenv('DB_PORT'),
    'database': getenv('DB_NAME'),
}
