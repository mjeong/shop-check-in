import Queue as queue

import id_logger
import shop_user
import event
import fsm

USER_POD = shop_user.ShopUser("1", "POD Joe", "email", 0, 0, True)
USER_PROCTOR = shop_user.ShopUser("0", "Proctor Joe", "email", 0, 0, True)
USER_CERTIFIED = shop_user.ShopUser("0", "Joe Schmoe", "email", 0, 0, False)
USER_INVALID = shop_user.ShopUser("0", shop_user.UNAUTHORIZED)

CARD_SWIPE_POD = event.Event(event.CARD_SWIPE, USER_POD)
CARD_SWIPE_PROCTOR = event.Event(event.CARD_SWIPE, USER_PROCTOR)
CARD_SWIPE_CERTIFIED = event.Event(event.CARD_SWIPE, USER_CERTIFIED)
CARD_SWIPE_INVALID = event.Event(event.CARD_SWIPE, USER_INVALID)

CARD_INSERT = event.Event(event.CARD_INSERT, 5)
CARD_REMOVE = event.Event(event.CARD_REMOVE, 5)

SWITCH_FLIP_ON = event.Event(event.SWITCH_FLIP_ON, "")
SWITCH_FLIP_OFF = event.Event(event.SWITCH_FLIP_OFF, "")

BUTTON_CANCEL = event.Event(event.BUTTON_CANCEL, "")
BUTTON_CONFIRM = event.Event(event.BUTTON_CONFIRM)
BUTTON_MONEY = event.Event(event.BUTTON_MONEY, "")
BUTTON_CHANGE_POD = event.Event(event.BUTTON_CHANGE_POD, "")
BUTTON_CLEAR_USER = event.Event(event.BUTTON_CLEAR_USER, "")

TERMINATE_PROGRAM = event.Event(event.TERMINATE_PROGRAM)

class TestFsmDataOperations:

    def test_opening_process_switch_flip(self):
        assert True == False
        # should be the proctor on duty
        # log should have correct information

    def test_unlocked_process_closing_shop_success(self):
        assert True == False
        # should be no pod
        # log should have correct info

    def test_unlocked_process_closing_shop_failure(self):
        assert True == False
        # should still be pod
        # should be at least one user in shop
        # log should have correct info

    def test_adding_user_s_process_slot_one_user(self):
        assert True == False
        # should have a user in the correct slot
        # log should have correct info

    def test_adding_user_s_process_slot_two_users(self):
        assert True == False
        # should have two users in the correct slot
        # log should have correct info

    def test_removing_user_process_slot_reinsert_user(self):
        assert True == False
        # shop state should not change
        # log should have correct info

    def test_removing_user_process_slot_transfer_user(self):
        assert True == False
        # should have user(s) transfered to new slot
        # log should have correct info

    def test_removing_using_process_discharge(self):
        assert True == False
        # should empty slot
        # log should have correct info

    def test_clearing_debt_process_card_swipe_single_user(self):
        assert True == False
        # user debt should increase by fixed amount
        # log should have correct info

    def test_clearing_debt_process_card_swipe_two_users(self):
        assert True == False
        # both user debts should increase by fixed amount
        # log should have correct info

    def test_clearing_debt_process_card_swipe(self):
        assert True == False
        # user debt should be zeroed
        # log should have correct info

    def test_changing_pod_process_add_pod(self):
        assert True == False
        # should be an additional pod
        # log should have correct info

    def test_changing_pod_process_remove_pod_success(self):
        assert True == False
        # should remove correct proctor
        # log should have correct info

    # have to add check to make sure user has no debt and is
    #certified before letting them work

class TestFsmStateTransitions:

    def test_closed_invalid_events(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_INSERT)
        event_q.put(BUTTON_CONFIRM)
        event_q.put(CARD_REMOVE)
        event_q.put(BUTTON_CONFIRM)
        event_q.put(SWITCH_FLIP_ON)
        event_q.put(BUTTON_CONFIRM)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(BUTTON_CONFIRM)
        event_q.put(BUTTON_CANCEL)
        event_q.put(BUTTON_CONFIRM)
        event_q.put(BUTTON_CONFIRM)
        event_q.put(BUTTON_CONFIRM)
        event_q.put(BUTTON_MONEY)
        event_q.put(BUTTON_CONFIRM)
        event_q.put(BUTTON_CHANGE_POD)
        event_q.put(BUTTON_CONFIRM)
        event_q.put(BUTTON_CLEAR_USER)
        event_q.put(BUTTON_CONFIRM)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.CLOSED
        print

    def test_cancel_opening(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(BUTTON_CANCEL)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.CLOSED
        print

    def test_open_shop(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.STANDBY
        print

    def test_unlock_fail(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_CERTIFIED)
        event_q.put(BUTTON_CONFIRM)
        event_q.put(CARD_SWIPE_PROCTOR)
        event_q.put(BUTTON_CONFIRM)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.STANDBY
        print

    def test_unlock_shop(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.UNLOCKED
        print

    def test_cancel_unlock(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(BUTTON_CANCEL)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.STANDBY
        print

    def test_unlock_swipe_user(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(CARD_SWIPE_CERTIFIED)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.ADDING_USER
        print

    def test_unlock_swipe_proctor(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.ADDING_USER
        print

    def test_unlock_swipe_invalid(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(CARD_SWIPE_INVALID)
        event_q.put(BUTTON_CONFIRM)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.UNLOCKED
        print

    def test_unlock_remove(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(CARD_REMOVE)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.REMOVING_USER
        print

    def test_unlock_money(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(BUTTON_MONEY)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.CLEARING_DEBT
        print

    def test_unlock_change_pod(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(BUTTON_CHANGE_POD)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.CHANGING_POD
        print

    def test_unlock_close(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(CARD_REMOVE)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.REMOVING_USER
        print

    def test_unlock_add_user_cancel(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(BUTTON_CANCEL)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.STANDBY
        print

    def test_unlock_add_user(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(CARD_INSERT)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.STANDBY
        print

    def test_unlock_add_user_swipe(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(CARD_SWIPE_CERTIFIED)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.ADDING_USERS
        print

    def test_unlock_add_users_insert(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(CARD_SWIPE_CERTIFIED)
        event_q.put(CARD_INSERT)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.STANDBY
        print

    def test_unlock_add_user_cancel(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(CARD_SWIPE_CERTIFIED)
        event_q.put(BUTTON_CANCEL)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.STANDBY
        print

    def test_remove_cancel(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(CARD_REMOVE)
        event_q.put(CARD_INSERT)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.STANDBY
        print

    def test_remove_clear(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(CARD_REMOVE)
        event_q.put(BUTTON_CLEAR_USER)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.STANDBY
        print

    def test_remove_money(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(CARD_REMOVE)
        event_q.put(BUTTON_MONEY)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.STANDBY
        print

    def test_clearing_debt_cancel(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(BUTTON_MONEY)
        event_q.put(BUTTON_CANCEL)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.STANDBY
        print

    def test_clearing_debt_valid_swipe(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(BUTTON_MONEY)
        event_q.put(CARD_SWIPE_CERTIFIED)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.STANDBY
        print

    def test_clearing_debt_invalid_swipe(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(BUTTON_MONEY)
        event_q.put(CARD_SWIPE_INVALID)
        event_q.put(BUTTON_CONFIRM)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.CLEARING_DEBT
        print

    def test_unlock_change_pod_cancel(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(BUTTON_CHANGE_POD)
        event_q.put(BUTTON_CANCEL)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.STANDBY
        print

    def test_unlock_change_pod_add_proctor(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(BUTTON_CHANGE_POD)
        event_q.put(CARD_SWIPE_PROCTOR)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.STANDBY
        print

    def test_unlock_change_pod_remove_pod_fail(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(BUTTON_CHANGE_POD)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(BUTTON_CONFIRM)
        event_q.put(BUTTON_CANCEL)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.STANDBY
        print

    def test_unlock_change_pod_remove_pod(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(BUTTON_CHANGE_POD)
        event_q.put(CARD_SWIPE_PROCTOR)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(BUTTON_CHANGE_POD)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.STANDBY
        print

    def test_unlock_change_pod_err(self):
        event_q = queue.Queue()
        shop_user_database = shop_user.ShopUserDatabaseSpoof()
        board = fsm.BoardFsm(event_q, shop_user_database)
        
        event_q.put(CARD_SWIPE_POD)
        event_q.put(SWITCH_FLIP_OFF)
        event_q.put(CARD_SWIPE_POD)
        event_q.put(BUTTON_CHANGE_POD)
        event_q.put(CARD_SWIPE_CERTIFIED)
        event_q.put(BUTTON_CONFIRM)
        event_q.put(BUTTON_CANCEL)
        event_q.put(TERMINATE_PROGRAM)

        print "\n"
        end_state = board.run_fsm()
        assert end_state == fsm.STANDBY
        print