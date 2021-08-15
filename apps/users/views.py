from decimal import Decimal

from django.db import transaction
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_view, extend_schema, inline_serializer
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from utils.decimal import round_decimal
from apps.users.permissions import UserViewSetPermission
from apps.users.serializers import serializers, UserSerializer, MoneyTransferSerializer

User = get_user_model()


@extend_schema_view(
    list=extend_schema(
        summary='Get all users',
        description='Get all users with pagination',
    ),
    retrieve=extend_schema(
        summary='Get user by ID',
        description='Get user by ID',
    ),
    money_transfer=extend_schema(
        request=MoneyTransferSerializer,
        responses=inline_serializer('MoneyTransferSuccessResponseSerializer', {'message': serializers.CharField()}),
        summary='Transfer money',
        description='Transfer money each user by INN list (each INN must be uniq and belong to user in DB)',
    )
)
class UserViewSet(ReadOnlyModelViewSet):

    queryset = User.objects.only('id', 'inn', 'first_name', 'last_name', 'username', 'bill').order_by('-id')
    serializer_class = UserSerializer
    permission_classes = (UserViewSetPermission, )

    @action(detail=True, methods=['POST'])
    def money_transfer(self, request, *args, **kwargs):

        user = self.get_object()

        serializer = MoneyTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        list_of_inn, amount = serializer.validated_data.values()

        if user.bill < amount:
            raise ParseError('Users bill does not have enough money')

        amount_per_user = round_decimal(amount / len(list_of_inn))

        if amount_per_user < Decimal('0.01'):
            raise ParseError('Amount too small to be split')

        with transaction.atomic():
            user.bill = round_decimal(user.bill - amount_per_user * len(list_of_inn))
            user.save()

            users_to_replenish = User.objects.only('id', 'bill').filter(inn__in=list_of_inn)
            for user_to_replenish in users_to_replenish:
                user_to_replenish.bill = round_decimal(user_to_replenish.bill + amount_per_user)
            User.objects.bulk_update(users_to_replenish, ['bill'], batch_size=100)

        return Response({'message': 'All done'})
