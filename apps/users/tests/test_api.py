from decimal import Decimal

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from model_bakery import baker
from parameterized import parameterized
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from apps.users.serializers import UserSerializer
from apps.users.tests.mock_data import USER_INN, LIST_OF_INN, USER_BILL, generate_users

User = get_user_model()


class UserViewSet(APITestCase):

    def auth_user_with_perm(self, permission_code_name: str) -> None:
        """
        Help function to auth user with permission by code_name
        """
        permission = Permission.objects.get(
            codename=permission_code_name,
            content_type=ContentType.objects.get_for_model(User),
        )
        self.user.user_permissions.add(permission)
        self.user = User.objects.get(pk=self.user.pk)
        self.client.force_authenticate(user=self.user)

    def setUp(self) -> None:

        self.user = baker.make(User, inn=USER_INN)
        self.url = reverse('user-list')
        self.data_to_transfer = {
            'user': self.user.pk,
            'amount': USER_BILL,
            'list_of_inn': LIST_OF_INN
        }

    @parameterized.expand([
        ('post', status.HTTP_403_FORBIDDEN),
        ('put', status.HTTP_403_FORBIDDEN),
        ('delete', status.HTTP_403_FORBIDDEN),
        ('get', status.HTTP_200_OK),
        ('options', status.HTTP_200_OK),
        ('post', status.HTTP_400_BAD_REQUEST, 'can_money_transfer'),
    ])
    def test_permission_methods(self, method: str, status_code: int, permission_code_name: str = None):

        url = f'{self.url}{self.user.id}/money_transfer/' if permission_code_name else self.url
        permission_code_name = permission_code_name or f'view_{User._meta.model_name}'

        client_method = getattr(self.client, method)

        response = client_method(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, msg=response.data)

        self.client.force_authenticate(user=self.user)
        response = client_method(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg=response.data)

        self.auth_user_with_perm(permission_code_name)

        response = client_method(url)
        self.assertEqual(response.status_code, status_code, msg=response.data)

    def test_list_method(self):

        generate_users()

        self.auth_user_with_perm(f'view_{User._meta.model_name}')
        # 1: get user, 2: get perm, 3: get count users, 4: get user data
        with self.assertNumQueries(4):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)

        all_users = User.objects.only('id', 'inn', 'first_name', 'last_name', 'username').order_by('-id')
        self.assertEqual(all_users.count(), response.data.get('count'))

        self.assertListEqual(UserSerializer(instance=all_users, many=True).data, response.data.get('results'))

    @parameterized.expand([
        ({'user': 0}, ),
        ({'amount': -1}, ),
        ({'amount': 1.999}, ),
        ({'amount': USER_BILL + 10}, ),
        ({'list_of_inn': ['1', '2', '3', ]}, ),
        ({'list_of_inn': []}, ),
        ({'list_of_inn': LIST_OF_INN + LIST_OF_INN[:2]}, ),
        ({'amount': 0.10}, ),
        ({'amount': 10000000000},),
    ])
    def test_money_transfer_bad_request(self, data_to_transfer: dict):

        generate_users()

        self.data_to_transfer.update(data_to_transfer)

        self.auth_user_with_perm('can_money_transfer')

        response = self.client.post(f'{self.url}{self.user.id}/money_transfer/', self.data_to_transfer, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, msg=response.data)

    @parameterized.expand([
        ({'amount': 0.7, 'list_of_inn': LIST_OF_INN[:8]}, 0.7, Decimal('0.06'), Decimal('0.08')),
        ({'amount': 0.7, 'list_of_inn': LIST_OF_INN[:6]}, 0.7, Decimal('0.04'), Decimal('0.11')),
        ({'amount': 60, 'list_of_inn': LIST_OF_INN[:10]}, 60, Decimal('0'), Decimal('6.00')),
        ({'amount': 10, 'list_of_inn': LIST_OF_INN[:9]}, 10, Decimal('0.01'), Decimal('1.11')),
        ({'amount': 16, 'list_of_inn': LIST_OF_INN + (USER_INN, )}, 16, Decimal('1.00'), Decimal('1.00')),
        ({'amount': 15, 'list_of_inn': LIST_OF_INN + (USER_INN,)}, 16, Decimal('2.05'), Decimal('0.93')),
        ({'amount': 0.15}, 2.15, Decimal('2.00'), Decimal('0.01')),
        ({'amount': 0.15}, 2.15, Decimal('2.00'), Decimal('0.01')),
        ({'amount': 1000000000}, 1000000000, Decimal('0.1'), Decimal('66666666.66')),
    ])
    def test_transfer_money(self, data_to_transfer: dict, user_bill: float,
                            user_bill_after_transfer: Decimal, users_bills_after_transfer: Decimal):

        generate_users()

        self.data_to_transfer.update(data_to_transfer)
        self.user.bill = user_bill
        self.user.save()

        self.auth_user_with_perm('can_money_transfer')
        # 1: get user for auth, 2: get perm, 3: get user for action, 4: check validation count, 5: set savepoint,
        # 6: update user bill, 7: select users by inns, 8: bulk update users bills, 9: release savepoint
        with self.assertNumQueries(9):
            response = self.client.post(f'{self.url}{self.user.id}/money_transfer/', self.data_to_transfer,
                                        format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)

        self.user = User.objects.get(pk=self.user.pk)
        users_bills = list(
            User.objects.filter(
                inn__in=self.data_to_transfer['list_of_inn']
            ).exclude(
                inn=USER_INN
            ).values_list('bill', flat=True)
        )
        self.assertEqual(users_bills.count(users_bills[0]), len(users_bills))
        self.assertEqual(users_bills[0], users_bills_after_transfer)

        self.assertEqual(self.user.bill, user_bill_after_transfer)
