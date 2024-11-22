
from functools import lru_cache
from os import path
from typing import TypeVar, Type

from attr import dataclass
from pydantic import BaseModel, SecretStr, PostgresDsn, FilePath, field_validator
from yaml import load

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader

ConfigType = TypeVar("ConfigType", bound=BaseModel)

ROOT_DIR = path.dirname(path.abspath(__file__))
conf_file = path.join(ROOT_DIR, "config.yml")

@dataclass
class NatsConfig(BaseModel):
    servers: list[str]

@dataclass
class BotConfig(BaseModel):
    token: SecretStr
    admin_ids: list[int]

@dataclass
class DbConfig(BaseModel):
    dsn: str
    is_echo: bool

@dataclass
class WebHookConfig(BaseModel):
    web_server_host: str
    web_server_port: int
    webhook_path: str
    webhook_secret: str
    base_webhook_url: str
    webhook_ssl_cert: FilePath
    webhook_ssl_priv: FilePath

    @field_validator("webhook_ssl_cert", mode="before")
    @classmethod
    def abs_cert(cls, webhook_ssl_cert):
        return path.join(ROOT_DIR, webhook_ssl_cert)


    @field_validator("webhook_ssl_priv", mode="before")
    @classmethod
    def abs_priv(cls, webhook_ssl_priv):
        return path.join(ROOT_DIR, webhook_ssl_priv)


@lru_cache(maxsize=1)
def parse_config_file() -> dict:
    # Проверка наличия переменной окружения, которая переопределяет путь к конфигу
    if conf_file is None:
        error = "Could not find settings file"
        raise ValueError(error)
    # Чтение файла, попытка распарсить его как YAML
    with open(conf_file, "rb") as file:
        config_data = load(file, Loader=SafeLoader)
    return config_data


@lru_cache
def get_config(model: Type[ConfigType], root_key: str) -> ConfigType:
    config_dict = parse_config_file()
    if root_key not in config_dict:
        error = f"Key {root_key} not found"
        raise ValueError(error)
    return model.model_validate(config_dict[root_key])


