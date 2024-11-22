from aiogram import Router
from .test import admin_router


def get_routers() -> list[Router]:
    return [
        admin_router,
        # user_router,
    ]
