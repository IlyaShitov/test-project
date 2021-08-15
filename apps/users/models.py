from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser

from utils.validators import INNValidator


class User(AbstractUser):

    inn = models.CharField('INN', unique=True, max_length=12, validators=[INNValidator()])

    bill = models.DecimalField('Bill', max_digits=12, decimal_places=2, default=Decimal('0.00'),
                               validators=[MinValueValidator(Decimal('0.00'))])

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
