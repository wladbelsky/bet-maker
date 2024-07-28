import sqlalchemy
from typing import Dict, Type
from database.models import metadata
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine


class Singleton(type):
    _instances: Dict[Type, Dict[str, object]] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = {}
        key = str(args) + str(kwargs)
        if not any((args, kwargs,)):
            if len(cls._instances[cls]) == 1:
                return list(cls._instances[cls].values())[0]
            else:
                raise ValueError("No key provided and multiple instances exist")
        if key not in cls._instances[cls]:
            cls._instances[cls][key] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls][key]


class Database(metaclass=Singleton):
    def __init__(self, db_config: dict | None = None):
        self.engine: AsyncEngine = create_async_engine(self.prepare_connection_string(db_config),
                                                       pool_size=10,
                                                       echo=False)
        self.session_class = sqlalchemy.orm.sessionmaker(bind=self.engine, class_=AsyncSession)

    async def prepare_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

    def get_session(self) -> AsyncSession:
        return self.session_class()

    async def close(self):
        await self.engine.dispose()

    @staticmethod
    def prepare_connection_string(config: dict):
        """
        Prepares the connection string for the database.
        :param config: The config dictionary.
        :return: The connection string.
        """
        config = config.copy()
        user = config.pop('user') or ''
        password = config.pop('password') or ''
        host = config.pop('host')
        port = config.pop('port') or ''
        database = config.pop('database') or ''
        engine = config.pop('engine')
        return (f'{engine}://{user}{":" if user and password else ""}'
                f'{password}{"@" if user and password else ""}{host}{":" if port else ""}{port}'
                f'{"/" if database else ""}{database}{"?" if config else ""}'
                f'{"&".join(f"{key}={value}" for key, value in config.items())}')

    @classmethod
    def get_instance(cls):
        return cls()
