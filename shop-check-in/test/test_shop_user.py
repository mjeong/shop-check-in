import shop_user
import sample_users


class TestShopUser:

    def test_is_shop_certified_failure_unauthorized(self):
        assert sample_users.USER_INVALID.is_shop_certified() is False

    def test_is_shop_certified_failure_invalid_test(self):
        assert sample_users.USER_WAY_OUT_OF_DATE.is_shop_certified() is False

    def test_is_shop_certified_succeed(self):
        assert sample_users.USER_CERTIFIED.is_shop_certified() is True

    def test_is_proctor_failure_not_certified(self):
        assert sample_users.USER_PROCTOR_OUT_OF_DATE.is_proctor() is False

    def test_is_proctor_failure_not_proctor(self):
        assert sample_users.USER_CERTIFIED.is_proctor() is False

    def test_is_proctor_succeed(self):
        assert sample_users.USER_PROCTOR.is_proctor() is True

    def test_has_valid_safety_test_failure_way_out_of_date(self):
        user = shop_user.ShopUser()
        assert user._has_valid_safety_test() is False

    def test_has_valid_safety_test_failure_slightly_out_of_date(self):
        assert sample_users.USER_JUST_OUT_OF_DATE._has_valid_safety_test() is False

    def test_has_valid_safety_test_succeed(self):
        assert sample_users.USER_CERTIFIED._has_valid_safety_test() is True

    def test_has_valid_safety_test_succeed_one_day_left(self):
        assert sample_users.USER_JUST_IN_DATE._has_valid_safety_test() is True
