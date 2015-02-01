import Queue as queue
import threading

import winsound

import error_handler
import event
import id_logger
import shop
import shop_user
import shop_user_database
import io_moderator
import shop_check_in_exceptions

MESSAGE = 0
ACTIONS_DICT = 1

CLOSED = "closed"
OPENING = "opening"
STANDBY = "standby"
UNLOCKED = "unlocked"
ADDING_USER = "adding_user"
ADDING_USERS = "adding_users"
REMOVING_USER = "removing_user"
CLEARING_DEBT = "clearing debt"
CHANGING_POD = "changing pod"

NOISE_OPENING = "resources\\sounds\\thx.wav"
NOISE_CLOSING = "resources\\sounds\\shutdown.wav"
NOISE_SUCCESS = "\\resources\\sounds\\success_ding.wav"
NOISE_ERROR = "\\resources\\sounds\\error_buzz.wav"
NOISE_CLEARING_DEBT = "\\resources\\sounds\\cha_ching.wav"
NOISE_CHARGING_USER = "\\resources\\sounds\\sad_trombone.wav"

# TODO: any clean way to avoid unused function parameters?


def _process_card_swipe(function_to_decorate):
        def card_swipe_processor(self, id_number, cargo):
            try:
                user = self._shop_user_database.get_shop_user(id_number)
            except shop_check_in_exceptions.NonexistentUserError as error:
                self._play_noise(NOISE_ERROR)
                return self._error_handler.handle_error(self._state, error), cargo
            else:
                return function_to_decorate(self, user, cargo)

        return card_swipe_processor


class BoardFsm(object):

    def __init__(self, event_q, message_q, shop_user_db):
        self._state = CLOSED
        self._shop = shop.Shop()
        self._shop_user_database = shop_user_db
        self._event_q = event_q
        self._message_q = message_q
        self._error_handler = error_handler.ErrorHandler(event_q)

        self._state_data = {
            CLOSED: ("\nShop closed.\n\rProctor swipe",
                     {event.CARD_SWIPE: self._closed_process_card_swipe}),

            OPENING: ("\nStarting up!\n\rFlip switch",
                      {event.BUTTON_CANCEL: self._go_to_closed_state,
                       event.SWITCH_FLIP_OFF: self._opening_process_switch_flip}),

            STANDBY: ("\nBoard locked.\n\rPOD swipe",
                      {event.CARD_SWIPE: self._standby_process_card_swipe}),

            UNLOCKED: ("\nBoard Unlocked.\n\rTake any action",
                       {event.BUTTON_CANCEL: self._go_to_standby_state,
                        event.CARD_SWIPE: self._unlocked_process_card_swipe,
                        event.CARD_REMOVE: self._go_to_remove_user_state,
                        event.BUTTON_MONEY: self._go_to_clear_money_state,
                        event.BUTTON_CHANGE_POD: self._go_to_change_pod_state,
                        event.SWITCH_FLIP_ON: self._unlocked_process_closing_shop}),

            ADDING_USER: ("\nAdding user.\n\rSwipe/insert card",
                          {event.CARD_SWIPE: self._adding_user_process_card_swipe,
                           event.CARD_INSERT: self._adding_user_s_process_slot,
                           event.BUTTON_CANCEL: self._go_to_standby_state}),

            ADDING_USERS: ("\nAdding users.\n\rInsert cards",
                           {event.CARD_INSERT: self._adding_user_s_process_slot,
                            event.BUTTON_CANCEL: self._go_to_standby_state}),

            REMOVING_USER: ("\nRemoving user(s).\n\r(R)nsrt/clr/chrg",
                            {event.CARD_INSERT: self._removing_user_process_slot,
                             event.BUTTON_DISCHARGE_USER: self._removing_user_process_discharge,
                             event.BUTTON_MONEY: self._removing_user_process_charge}),

            CLEARING_DEBT: ("\nClearing debt.\n\rSwipe card",
                            {event.CARD_SWIPE: self._clearing_debt_process_card_swipe,
                             event.BUTTON_CANCEL: self._go_to_standby_state}),

            CHANGING_POD: ("\nChanging POD.\n\rSwipe card",
                           {event.CARD_SWIPE: self._changing_pod_process_card_swipe,
                            event.BUTTON_CANCEL: self._go_to_standby_state})
            }

    def run_fsm(self):
        cargo = None
        
        while True:
            state_message = self._state_data[self._state][MESSAGE]
            state_actions = self._state_data[self._state][ACTIONS_DICT]

            self._message_q.put(state_message)
            
            next_event = self._event_q.get()

            if next_event.key == event.TERMINATE_PROGRAM:
                return self._state
            
            try:
                self._state, cargo = state_actions[next_event.key](next_event.data, cargo)
            except KeyError:
                self._state = self._error_handler.handle_error(self._state, next_event.key)

    def _go_to_closed_state(self, ignored_event_data, ignored_cargo):
        self._play_noise(NOISE_CLOSING)
        return CLOSED, None

    def _go_to_standby_state(self, ignored_event_data, ignored_cargo):
        self._play_noise(NOISE_SUCCESS)
        return STANDBY, None

    def _go_to_remove_user_state(self, slot, ignored_cargo):
        return REMOVING_USER, slot
    
    def _go_to_clear_money_state(self, ignored_event_data, ignored_cargo):
        return CLEARING_DEBT, None

    def _go_to_change_pod_state(self, ignored_event_data, ignored_cargo):
        return CHANGING_POD, None

    @_process_card_swipe
    def _closed_process_card_swipe(self, user, ignored_cargo):
        try:
            user.is_proctor()
        except shop_check_in_exceptions.ShopUserError as error:
            self._play_noise(NOISE_ERROR)
            return self._error_handler.handle_error(self._state, error), ignored_cargo
        else:
            self._play_noise(NOISE_SUCCESS)
            return OPENING, user

    def _opening_process_switch_flip(self, ignored_event_data, user):
        self._shop.open_(user)
        self._play_noise(NOISE_OPENING)
        return STANDBY, None

    @_process_card_swipe
    def _standby_process_card_swipe(self, user, ignored_cargo):
        if self._shop.is_pod(user):
            self._play_noise(NOISE_SUCCESS)
            return UNLOCKED, user
        else:
            self._play_noise(NOISE_ERROR)
            return self._error_handler.handle_error(self._state, shop_user.DEFAULT_NAME), ignored_cargo

    @_process_card_swipe
    def _unlocked_process_card_swipe(self, user, ignored_cargo):
        try:
            user.is_shop_certified()
        except shop_check_in_exceptions.ShopUserError as error:
            self._play_noise(NOISE_ERROR)
            return self._error_handler.handle_error(self._state, error), ignored_cargo
        else:
            self._play_noise(NOISE_SUCCESS)
            return ADDING_USER, [user]

    def _unlocked_process_closing_shop(self, ignored_event_data, user):
        try:
            self._shop.close_(user)
        except shop_check_in_exceptions.ShopOccupiedError as error:
            self._play_noise(NOISE_ERROR)
            return self._error_handler.handle_error(self._state, error), user
        else:
            self._play_noise(NOISE_CLOSING)
            return CLOSED, None

    @_process_card_swipe
    def _adding_user_process_card_swipe(self, second_user, first_user):
        try:
            second_user.is_shop_certified()
        except shop_check_in_exceptions.ShopUserError as error:
            self._play_noise(NOISE_ERROR)
            return self._error_handler.handle_error(self._state, error), first_user
        else:
            self._play_noise(NOISE_SUCCESS)
            return ADDING_USERS, first_user + [second_user]

    def _adding_user_s_process_slot(self, slot, user_s):
        self._shop.add_user_s_to_slot(user_s, slot)
        self._play_noise(NOISE_SUCCESS)
        return STANDBY, None

    def _removing_user_process_slot(self, slot, prev_slot):
        self._shop.replace_or_transfer_user(slot, prev_slot)
        self._play_noise(NOISE_SUCCESS)
        return STANDBY, None
        
    def _removing_user_process_discharge(self, ignored_event_data, slot):
        self._shop.discharge_user_s(slot)
        self._play_noise(NOISE_SUCCESS)
        return STANDBY, None

    def _removing_user_process_charge(self, ignored_event_data, slot):
        user_s = self._shop.discharge_user_s(slot)

        for user in user_s:
            self._shop_user_database.increase_debt(user)

        self._play_noise(NOISE_CHARGING_USER)

        return STANDBY, None

    @_process_card_swipe
    def _clearing_debt_process_card_swipe(self, user, ignored_cargo):
        try:
            self._shop_user_database.clear_debt(user)
        except shop_check_in_exceptions.NonexistentUserError as error:
            self._play_noise(NOISE_ERROR)
            return self._error_handler.handle_error(self._state, error), ignored_cargo
        else:
            self._play_noise(NOISE_CLEARING_DEBT)
            return STANDBY, user

    @_process_card_swipe
    def _changing_pod_process_card_swipe(self, user, ignored_cargo):
        try:
            self._shop.change_pod(user)
        except shop_check_in_exceptions.ShopCheckInError as error:
            self._play_noise(NOISE_ERROR)
            return self._error_handler.handle_error(self._state, error), ignored_cargo
        else:
            self._play_noise(NOISE_SUCCESS)
            return STANDBY, None

    def _play_noise(self, noise):
        thread_play_noise = threading.Thread(target=winsound.PlaySound, args=(noise, winsound.SND_FILENAME))
        thread_play_noise.daemon = True
        thread_play_noise.start()


def main():
    event_q = queue.Queue()
    message_q = queue.Queue()

    shop_user_db = shop_user_database.ShopUserDatabase()
    board = BoardFsm(event_q, message_q, shop_user_db)

    thread_id_logger = id_logger.IdLogger(event_q)
    thread_id_logger.daemon = True
    thread_io_moderator = io_moderator.IoModerator(event_q, message_q)

    thread_id_logger.start()
    thread_id_logger.daemon = True
    thread_io_moderator.start()

    while True:
        board.run_fsm()

if __name__ == "__main__":
    main()
