from aiogram.fsm.state import State, StatesGroup


class CommentState(StatesGroup):
    waiting_text = State()


class SearchState(StatesGroup):
    waiting_query = State()
