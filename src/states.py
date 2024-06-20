from aiogram.fsm.state import StatesGroup, State


class BotStates(StatesGroup):
    """Состояния-режимы тренировки
    (menu - состояние без запущенных тренировок)."""
    practice = State()
    menu = State()