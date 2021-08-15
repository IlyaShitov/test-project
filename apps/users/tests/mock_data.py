from typing import List

from django.contrib.auth import get_user_model
from model_bakery import baker

User = get_user_model()

USER_INN = '031473063921'
USER_BILL = 0.15
LIST_OF_INN = (
    '089931674169',
    '807044778410',
    '190124586099',
    '910652482319',
    '233206048990',
    '590755958293',
    '538047207826',
    '740748858710',
    '423174411167',
    '508845617168',
    '538090067332',
    '270398188692',
    '813276814314',
    '754990672647',
    '000000000000',
)


def generate_users(list_of_inn: List[str] = LIST_OF_INN) -> None:
    """
    Help function to generate users by list of inn
    """
    for inn in list_of_inn:
        baker.make(User, inn=inn)
