import shop
import fsm
import shop_user
import shop_check_in_exceptions
import event
import io_moderator
from mailer import Mailer
import winsound

DEFAULT_ERROR_MESSAGE = "\0ACTION NOT\n\rRECOGNIZED. CNFM"
ERROR_RESOLVED = "error_resolved"
ERROR_NOT_RESOLVED = "error_not_resolved"


class ErrorHandler(object):
    def __init__(self, event_q, message_q, shop_):
        self._event_q = event_q
        self._message_q = message_q
        self._shop = shop_
        self._mailer = Mailer()
        # TODO: Right now errors are sometimes passed in as events, sometimes errors. Homogenize.
        self._messages_to_display = {
            shop_check_in_exceptions.NonexistentUserError: "\0NONEXISTENT\n\rUSER",
            shop_check_in_exceptions.InvalidUserError: "\0ERR - INVALID\n\rUSER - CONFIRM",
            shop_check_in_exceptions.MoneyOwedError: "\0ERR - USER OWES\n\rMONEY - CONFIRM",
            shop_check_in_exceptions.NonProctorError: "\0ERR - USER IS\n\rNOT A PROCTOR",
            shop_check_in_exceptions.NonPodError: "\0ERR - USER IS\n\rNOT A POD",
            shop_check_in_exceptions.ShopOccupiedError: "\0ERR\n\rSHOP IS OCCUPIED",
            shop_check_in_exceptions.OutOfDateTestError: "\0ERR - EXPIRED\n\rSAFETY TEST",
            shop_check_in_exceptions.ShopAlreadyOpenError: "\0ERR SHOP\n\rALREADY OPEN",
            shop_check_in_exceptions.PodRequiredError: "\0ERR - ONLY POD\n\rCANNOT SIGN OUT",
            shop_user.DEFAULT_NAME: "\0ERR - LACK\n\r PERMISSIONS",
            event.CARD_SWIPE:  "\0ERR - IGNORING\n\r SWIPE, CONFIRM",
            event.CARD_REMOVE: "\0ERR -REINSRT OR\n\rCNFRM, SLOT: ",
            event.CARD_INSERT: "\0ERR - UNINSERT\n\rSLOT:",
            event.SWITCH_FLIP_OFF: "\0ERR - TURN\n\rSHOP BACK ON"
            }

        self._no_confirm_state_error_combos = [
            (fsm.CLOSED, shop_check_in_exceptions.ShopUserError),
            (fsm.CLOSED, shop_check_in_exceptions.NonexistentUserError),
            (fsm.CLOSED, shop_check_in_exceptions.NonProctorError),
            (fsm.STANDBY, shop_check_in_exceptions.UnauthorizedUserError)
        ]

        self._default_event_to_action_map = {
            event.CARD_INSERT: self._handle_card_insert_default,
            event.CARD_REMOVE: self._handle_card_remove_default,
            event.BUTTON_CONFIRM: self._handle_confirm_default,
        }

        self._error_specific_event_to_action_map = {
            event.CARD_REMOVE: {
                event.CARD_INSERT: self._handle_card_reinsert,
                event.BUTTON_CONFIRM: self._handle_card_removed_not_reinserted
            },
            event.CARD_INSERT: {
                event.CARD_REMOVE: self._handle_card_uninsert,
                event.BUTTON_CONFIRM: self._handle_unrecognized_event
            },
            shop_check_in_exceptions.ShopOccupiedError: {
                event.SWITCH_FLIP_ON: self._handle_shop_open
            },
            event.SWITCH_FLIP_OFF: {
                event.SWITCH_FLIP_ON: self._handle_shop_open
            }

        }

    def _requires_no_confirmation(self, state, error):
        for (no_confirm_state, no_confirm_error) in self._no_confirm_state_error_combos:
            if state == no_confirm_state and self._same_error(error, no_confirm_error):
                return True
        return False

    @staticmethod
    def _same_error(e, template_e):
        """
        Determines if e is an instance of error class template_e OR if e equals template_e
        """

        try:
            return isinstance(e, template_e)
        except TypeError:
            return e == template_e

    def handle_error(self, return_state, error, error_data=None):
        # winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS)

        while True:

            self._report_error(error, error_data)

            if self._requires_no_confirmation(return_state, error):
                return return_state

            next_event = self._event_q.get()
            if next_event.key == event.TERMINATE_PROGRAM:
                # TODO: Find better way to terminate prgm from error, currently need 2 signals
                self._event_q.put(event.Event(event.TERMINATE_PROGRAM))
                return return_state

            action = self._get_action(error, next_event)

            result = action(next_event.data, error_data)

            if result == ERROR_RESOLVED:
                return return_state

    def _report_error(self, error, error_data):
        print 'going to report', error
        error_msg = self._messages_to_display.get(error, DEFAULT_ERROR_MESSAGE)
        error_msg += str(error_data) if error_data else ""
        print 'with msg', error_msg
        self._send_message_format_safe(error_msg)

    def _send_message_format_safe(self, msg):
        self._message_q.put(io_moderator.safe_format_msg(msg))

    def _get_action(self, error, next_event):
        try:
            action = self._error_specific_event_to_action_map[error][next_event.key]
        except KeyError:
            try:
                action = self._default_event_to_action_map[next_event.key]
            except KeyError:
                action = self._handle_unrecognized_event

        return action

    def _handle_card_reinsert(self, new_slot, old_slot):
        if new_slot == old_slot:
            return ERROR_RESOLVED
        else:
            self.handle_error(None, event.CARD_INSERT, new_slot)
            return ERROR_NOT_RESOLVED

    def _handle_card_uninsert(self, new_slot, old_slot):
        if new_slot == old_slot:
            return ERROR_RESOLVED
        else:
            self.handle_error(None, event.CARD_REMOVE, new_slot)
            return ERROR_NOT_RESOLVED

    def _handle_card_removed_not_reinserted(self, unused_data=None, old_slot=None):
        assert old_slot is not None
        name = "".join(self._shop.get_user_s_name(old_slot))[:14]
        self._send_message_format_safe("\0%s\n\rleft the shop!" % name)
        users = self._shop.get_user_s(old_slot)
        self._mailer._send_id_card_email_s(users)
        self._shop.discharge_user_s(old_slot)
        return ERROR_RESOLVED

    def _handle_card_insert_default(self, new_slot, unused_error_data=None):
        self.handle_error(None, event.CARD_INSERT, new_slot)
        return ERROR_NOT_RESOLVED

    def _handle_card_remove_default(self, new_slot, unused_error_data=None):
        self.handle_error(None, event.CARD_REMOVE, new_slot)
        return ERROR_NOT_RESOLVED

    def _handle_confirm_default(self, unused_data=None, unused_error_data=None):
        return ERROR_RESOLVED

    def _handle_unrecognized_event(self, unused_data=None, unused_error_data=None):
        return ERROR_NOT_RESOLVED

    def _handle_shop_open(self, unused_date=None, unused_error_data=None):
        return ERROR_RESOLVED

