from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_view, extend_schema, inline_serializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

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

        serializer = MoneyTransferSerializer(
            data=request.data,
            context={'user': request.user},
        )
        serializer.is_valid(raise_exception=True)

        user.transfer_money(
            serializer.validated_data['list_of_inn'],
            serializer.validated_data['amount'],
        )

        return Response({'message': 'All done'})
