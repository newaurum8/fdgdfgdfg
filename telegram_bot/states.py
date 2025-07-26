from aiogram.fsm.state import State, StatesGroup

class DealCreationStates(StatesGroup):
    waiting_seller_id = State()
    waiting_title = State()
    waiting_description = State()
    waiting_amount = State()
    confirmation = State()

class DealChatStates(StatesGroup):
    writing_message = State()
    sending_photo = State()
    sending_file = State()

class DisputeStates(StatesGroup):
    describing_problem = State()
    attaching_evidence = State()

class FindDealStates(StatesGroup):
    waiting_deal_id = State()

class ProfileStates(StatesGroup):
    editing_info = State()