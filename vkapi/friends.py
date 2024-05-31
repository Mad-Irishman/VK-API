import dataclasses
import time
import typing as tp

import requests
from vkapi import config, session

QueryParams = tp.Optional[tp.Dict[str, tp.Union[str, int]]]


@dataclasses.dataclass(frozen=True)
class FriendsResponse:
    count: int
    items: tp.List[tp.Dict[str, tp.Any]]


def get_friends(
    user_id: tp.Optional[int] = None, count: int = 5000, offset: int = 0, fields: tp.Optional[tp.List[str]] = None
) -> FriendsResponse:
    """
    Получить список идентификаторов друзей пользователя или расширенную информацию
    о друзьях пользователя (при использовании параметра fields).

    :param user_id: Идентификатор пользователя, список друзей для которого нужно получить.
    :param count: Количество друзей, которое нужно вернуть.
    :param offset: Смещение, необходимое для выборки определенного подмножества друзей.
    :param fields: Список полей, которые нужно получить для каждого пользователя.
    :return: Объект класса FriendsResponse.
    """
    access_token = config.VK_CONFIG["access_token"]
    v = config.VK_CONFIG["version"]
    response = session.get(
        url=f"friends.get?access_token={access_token}&user_id={user_id}&fields={','.join(
            fields) if fields is not None else None}&count={count}&offset={offset}&v={v}"
    )
    return FriendsResponse(count=response.json()["response"]["count"], items=response.json()["response"]["items"])


class MutualFriends(tp.TypedDict):
    id: int
    common_friends: tp.List[int]
    common_count: int


def get_mutual(
    source_uid: tp.Optional[int] = None,
    target_uid: tp.Optional[int] = None,
    target_uids: tp.Union[tp.List[int], tp.List[str], None] = None,
    order: str = "",
    count: tp.Optional[int] = None,
    offset: int = 0,
    progress=None,
) -> tp.List[MutualFriends]:
    """
    Получить список идентификаторов общих друзей между парой пользователей.
    Можно воспользоваться методом friends.getMutual, заполнив данные, требуемые ВК
    для предоставления вам доступа к друзьям. Или через метод friends.get и множества.

    :param source_uid: Идентификатор пользователя, чьи друзья пересекаются с друзьями пользователя с идентификатором target_uid.
    :param target_uid: Идентификатор пользователя, с которым необходимо искать общих друзей.
    :param target_uids: Cписок идентификаторов пользователей, с которыми необходимо искать общих друзей.
    :param order: Порядок, в котором нужно вернуть список общих друзей.
    :param count: Количество общих друзей, которое нужно вернуть.
    :param offset: Смещение, необходимое для выборки определенного подмножества общих друзей.
    :param progress: Callback для отображения прогресса.
    """
    access_token = config.VK_CONFIG["access_token"]
    v = config.VK_CONFIG["version"]
    if target_uids is not None:
        if len(target_uids) < 100:
            target_uids = list(map(lambda x: str(x), target_uids))
            mutual_friends = session.get(
                url=f"friends.getMutual?access_token={access_token}&source_uid={source_uid}&target_uid={target_uid if target_uid is not None else ''}&target_uids={
                    ','.join(target_uids)}&order={order}&count={count if count is not None else ''}&offset={offset}&v={v}"
            ).json()["response"]
            return [
                MutualFriends(
                    id=i["id"], common_friends=i["common_friends"], common_count=i["common_count"])
                for i in mutual_friends
            ]
        else:
            mutual_friends = []
            target_uids = list(map(str, target_uids))
            for off in range(0, len(target_uids), 100):
                mutual_friends.extend(
                    session.get(
                        url=f"friends.getMutual?access_token={access_token}&source_uid={source_uid}&target_uid={target_uid if target_uid is not None else ''}&target_uids={
                            ','.join(target_uids[off:off + 100])}&order={order}&count={count if count is not None else ''}&offset={off}&v={v}"
                    ).json()["response"]
                )
                time.sleep(0.34)
            return [
                MutualFriends(
                    id=i["id"], common_friends=i["common_friends"], common_count=i["common_count"])
                for i in mutual_friends
            ]

    else:
        mutual_friends = session.get(
            url=f"friends.getMutual?access_token={access_token}&source_uid={source_uid}&target_uid={target_uid if target_uid is not None else ''}&target_uids={
                target_uids if target_uids is not None else ''}&order={order}&count={count if count is not None else ''}&offset={offset}&v={v}"
        ).json()["response"]
        return mutual_friends
