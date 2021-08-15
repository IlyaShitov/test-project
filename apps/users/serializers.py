from decimal import Decimal, ROUND_HALF_DOWN

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):

    full_name = serializers.CharField(label='Full name', source='get_full_name')

    class Meta:
        model = User
        fields = (
            'id',
            'inn',
            'username',
            'bill',
            'full_name',
        )
        read_only_fields = fields


class MoneyTransferSerializer(serializers.Serializer):

    list_of_inn = serializers.ListSerializer(label='List of INN', child=serializers.CharField(label='INN'),
                                             allow_empty=False)

    amount = serializers.DecimalField(label='Amount', max_digits=12, decimal_places=2, min_value=Decimal('0.01'),
                                      rounding=ROUND_HALF_DOWN)

    def validate_list_of_inn(self, list_of_inn):

        if len(list_of_inn) != len(set(list_of_inn)):
            raise ValidationError('INN in list must be uniq')

        if User.objects.filter(inn__in=list_of_inn).count() != len(list_of_inn):
            raise ValidationError('All INN must be owned by the users')

        return list_of_inn
