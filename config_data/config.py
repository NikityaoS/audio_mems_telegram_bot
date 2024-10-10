from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]


@dataclass
class MongDB:
    user_name: str
    password: str
    db: str
    auth_mech: str


@dataclass
class Config:
    tg_bot: TgBot


@dataclass
class Config_db:
    mongodb: MongDB


def load_config() -> Config:
    env: Env = Env()
    env.read_env()
    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_ids=list(map(int, env.list('ADMIN_ID')))))


def load_config_db() -> Config_db:
    env: Env = Env()
    env.read_env()
    return Config_db(
        mongodb=MongDB(
            user_name=env('MONGO_USERNAME'),
            password=env('MONGO_PASSWORD'),
            db=env('MONGO_DB'),
            auth_mech=env('MONGO_AUTH_MECH')
        )
    )
