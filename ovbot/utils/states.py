from aiogram.fsm.state import State, StatesGroup


class ReminderForm(StatesGroup):
    name_reminder: State = State()
    choose_time: State = State()
    reminder_days: State = State()
    text_reminder: State = State()
    days: State = State()
    month_days: State = State()
    add_db_reminder_time: State = State()
    delete_reminder_id: State = State()
    handle_delete_reminder_id: State = State()
    start_reminder_id: State = State()
    stop_reminder_id: State = State()
