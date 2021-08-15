from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.validators import ValidationError
from model_bakery import baker
from parameterized import parameterized

from apps.users.tests.mock_data import LIST_OF_INN

User = get_user_model()


class UserTestCase(TestCase):

    @parameterized.expand([
        ('', ),
        ('1', ),
        ('009931674169', ),
        ('42317441116711', ),
        ('423174411168', ),
    ])
    def test_invalid_inn(self, inn: str):
        user = baker.prepare(User, inn=inn)
        with self.assertRaises(ValidationError):
            user.full_clean()

    @parameterized.expand([(inn, ) for inn in LIST_OF_INN])
    def test_valid_inn(self, inn: str):
        user = baker.prepare(User, inn=inn)
        user.full_clean()

    @parameterized.expand([
        (-1, ),
        (1.999, ),
        (10000000000, ),
    ])
    def test_invalid_bill(self, bill: float):
        user = baker.prepare(User, bill=bill)
        with self.assertRaises(ValidationError):
            user.full_clean()
