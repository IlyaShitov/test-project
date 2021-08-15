import re
from django.utils.deconstruct import deconstructible
from django.core.validators import ValidationError


@deconstructible
class INNValidator:
    """
    Validates if sum of the remainder of the division is == last 2 numbers of INN.
    Each digit in INN is multiplied by a specific index, the sum is then divided.
    https://zapolnenie.info/algoritm-proverki-inn/
    """
    message = 'Please, enter the correct INN.'
    code = 'inn_invalid'
    odds = (3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8)
    inn_regex = r'^[\d+]{12}$'

    def __call__(self, value: str):

        if len(value) == 12:
            if not re.match(self.inn_regex, value):
                raise ValidationError('INN must contain 12 numbers.')

            if not self.inn_validate(value):
                raise ValidationError('Incorrect INN.')
        else:
            raise ValidationError('INN must contain 12 numbers.')

    def inn_validate(self, inn: str) -> bool:
        return inn[-2:] == self.check_control_sum(inn[:-2]) + self.check_control_sum(inn[:-1])

    def check_control_sum(self, part_inn: str) -> str:
        pairs = zip(self.odds[11-len(part_inn):], [int(x) for x in part_inn])
        return str(sum([k * v for k, v in pairs]) % 11 % 10)
