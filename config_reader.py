
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
class BotConfig(BaseModel):
    token: SecretStr


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


