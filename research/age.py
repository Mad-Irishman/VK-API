import datetime as dt
import typing as tp
from statistics import median

from vkapi.friends import get_friends


def age_predict(user_id: int) -> tp.Optional[float]:
    """
    Наивный прогноз возраста пользователя по возрасту его друзей.

    Возраст считается как медиана среди возраста всех друзей пользователя.

    :param user_id: Идентификатор пользователя.
    :return: Медианный возраст пользователя или None, если возраст не удалось определить.
    """
    friends = get_friends(user_id=user_id, fields=["bdate"])
    current_year = dt.datetime.now().year
    ages = []

    for friend in friends.items:
        bdate = friend.get("bdate")
        if bdate:
            try:
                birth_year = int(bdate.split(".")[-1])
                if len(bdate.split(".")[-1]) == 4:
                    age = current_year - birth_year
                    ages.append(age)
            except (ValueError, IndexError):
                continue

    return median(ages) if ages else None
