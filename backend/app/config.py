import os
from dotenv import dotenv_values
from pydantic import BaseSettings
from functools import lru_cache


def get_env_file():
    my_env = {
        **dotenv_values(".env"),  # load local file development variables
        **os.environ,  # override loaded values with system environment variables
    }
    return my_env


config_env = get_env_file()


class Settings(BaseSettings):
    PORT: int = config_env["PORT"]
    HOST: str = config_env["HOST"]
    JWT_SECRET: str = config_env["JWT_SECRET"]
    DATABASE_URL = config_env['DATABASE_URL']
    origins: list[str] = config_env["origins"]
    
    REMOTE_HOST:str = config_env['REMOTE_HOST']
    REMOTE_PORT: int = config_env['REMOTE_PORT']
    REMOTE_PROTOCOLE: str = config_env['REMOTE_PORT']
    
    class Config:
        def __init__(self):
            pass

        env_file = '.env'

    @property
    def URL(self) -> str:
        protocol = 'https' if self.HTTPS else 'http'
        return f'{protocol}://{self.HOST}'


Configs = Settings()


# print('Configs:\n', Configs)


@lru_cache()
def get_settings():
    return Configs
