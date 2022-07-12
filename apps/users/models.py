from decimal import Decimal
from typing import List

from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser

from utils.decimal import round_decimal
from utils.validators import INNValidator


class User(AbstractUser):

    inn = models.CharField(
        'INN',
        unique=True,
        max_length=12,
        validators=[INNValidator()]
    )

    bill = models.DecimalField(
        'Bill',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    @transaction.atomic()
    def transfer_money(self, list_of_inn: List[str], amount: Decimal):
        amount_per_user = round_decimal(amount / len(list_of_inn))

        self.bill = round_decimal(self.bill - amount_per_user * len(list_of_inn))
        self.save()

        users_to_replenish = User.objects.only('id', 'bill').filter(inn__in=list_of_inn)
        for user_to_replenish in users_to_replenish:
            user_to_replenish.bill = round_decimal(user_to_replenish.bill + amount_per_user)

        self.__class__.objects.bulk_update(users_to_replenish, ['bill'], batch_size=100)

    class Meta:
        # Т.к. пользователь может быть много, то вешаем индексы
        indexes = [
            models.Index(name='inn_index', fields=['inn', ]),
        ]
        permissions = [
            ('can_money_transfer', 'Can money transfer'),
        ]
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username
