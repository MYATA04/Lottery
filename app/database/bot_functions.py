from typing import Any

from app.database.database_functions import execute, fetch_all_data, fetch_one_data, fetch_one_row_data
from app.logger import logger


async def get_user(user_id: int | str) -> dict | None:
    """
    Возвращает все данные о пользователе.

    На вход принимает:
        user_id - Телеграм ID пользователя.

    Возвращает:
        Если данный пользователь есть в базе данных, возвращает словарь:
            {
                'id': str,
                'username': str,
                'fullname': str,
                'notification': str (1 или 0),
                'numbers': str (1,2,6,23,...),
                'phone': str
            }

        Если данный пользователь нет в базе данных, то возвращает None:
            None
    """
    query = (f"SELECT * FROM `user` "  # noqa: S608
             f"WHERE id = '{user_id}'")

    user: list | None = await fetch_one_row_data(query)

    if user is None:  # Если пользователя нет в базе данных, возвращаем None
        return None

    return {
        "id": user[0],
        "username": user[1],
        "fullname": user[2],
        "notification": user[3],
        "numbers": user[4],
        "phone": user[5]
    }


async def add_user(user_id: int | str, username: str, fullname: str) -> None:
    """
    Добавляет пользователя в базу данных.

    На вход принимет:
        user_id - Телеграм ID пользователя,
        username - Логин пользователя в телеграме,
        fullname - Полное имя пользователя в телеграме.

    Возвращает:
        Ничего не возвращает
    """
    user_ids = await get_all_users_ids()

    if user_id in user_ids:  # Если пользователь уже находится в базе данных, то выходим из функции
        return

    query = ("INSERT INTO `user` "
             "    (id, username, fullname, notification, numbers, phone)"
             "VALUES "
             f"    ('{user_id}', '{username}', '{fullname}', '0', '', '')")

    await execute(query)

    logger.info("[DATABASE] В базу данных был добавлен новый пользователь:"
                f"\n\tID: {user_id}"
                f"\n\tUSERNAME: {username}"
                f"\n\tFULLNAME: {fullname}")


async def get_user_numbers(user_id: int | str) -> list[int, Any] | list:
    """
    Возвращает купленные в активном розыгрыше номерки пользователя.

    На вход принимет:
        user_id - Телеграм ID пользователя.

    Возвращает:
        Если у пользователя имеются номерки, то возвразает список с номерками:
            [1, 2, 3, ...]

        Если у пользователя нет номерков, возвращает пустой список:
            []
    """
    query = ("SELECT numbers FROM `user` "  # noqa: S608
             f"WHERE id = '{user_id}'")

    numbers_str = await fetch_one_data(query)

    if not numbers_str:  # Если у пользователя нет купленных номерков, возвращаем пустой список
        return []

    numbers_list: list[str, Any] = numbers_str.split(",")  # Строку из номерков разбиваем в массив с str номерками

    for number_index in range(len(numbers_list)):  # Массив из номерков str переделываем в массив с int номерками
        if not numbers_list[number_index]:
            numbers_list.remove(numbers_list[number_index])  # Убираем номерок если он пустая строка

        else:
            numbers_list[number_index] = int(numbers_list[number_index])  # Меняем тип str номерка в int

    return numbers_list


async def null_all_numbers() -> None:
    """
    Удаляет у всех пользователей их купленные номерки.

    P.S.: Используется когда розыгрыш заканчивается.
    """
    query = ("UPDATE `user` SET "
             "    numbers = ''")

    await execute(query)


async def update_user_data(user_id: int | str, column: str, new_data: int | str) -> None:
    """
    Изменяет данные пользователя в базе данных.

    На вход принимает:
        user_id - Телеграм ID пользователя,
        column - Название столбца,
        new_data - Новое значение в столбце.

    Возвращает:
        Ничего не возвращает
    """
    query = ("UPDATE `user` SET "  # noqa: S608
             f"    {column} = '{new_data}' "
             f"WHERE id = '{user_id}'")

    await execute(query)


async def delete_user_data(user_id: int | str) -> None:
    """
    Удаляет данные пользователя из базы данных.

    На вход принимает:
        user_id - Телеграм ID пользователя.

    Возвращает:
        Ничего не возвращает
    """
    query = ("DELETE FROM `user` "  # noqa: S608
             f"WHERE id = '{user_id}'")

    await execute(query)


async def get_all_users() -> list[dict, Any] | list:
    """
    Возвращает данные всех пользователей.

    На вход принимет:
        Ничего не принимает

    Возвращает:
        Если в базе данных есть хоть один пользователь или больше, то возвращает список со словорями:
            [
                {
                    'id': str,
                    'username': str,
                    'fullname': str,
                    'notification': str (1 или 0),
                    'numbers': str (1,2,3,4,21,...),
                    'phone': str
                },
                . . .
            ]

        Если в базе данных нет ни единого пользователя, возвращает пустой список:
            []
    """
    query = "SELECT * FROM `user`"

    users: list[[str, Any], Any] | None = await fetch_all_data(query)

    if users is None or not users:  # Если в базе данных нет ни единого пользователя, возвращаем пустой список
        return []

    for user_index in range(len(users)):
        users[user_index] = {
            "id": users[user_index][0],
            "username": users[user_index][1],
            "fullname": users[user_index][2],
            "notification": users[user_index][3],
            "numbers": users[user_index][4],
            "phone": users[user_index][5]
        }

    return users


async def get_all_users_ids() -> list[int] | list:
    """
    Возвращает Телеграм ID всех пользователей.

    На вход принимает:
        Ничего не принимает

    Возвращает:
        Если в базе данных есть хоть один пользователь или больше, то возвращает список с int объектами:
            [user1_id, user2_id, . . .]

        Если в базе данных нет ни единого пользователя, возвращает пустой список:
            []
    """
    query = "SELECT id FROM `user`"

    user_ids = await fetch_all_data(query)

    if user_ids is None or not user_ids:
        return []

    return [int(user_list[0]) for user_list in user_ids]


async def check_user_in_db(user_id: int | str) -> bool:
    """
    Чекает, есть ли такой пользователь в базе данных.

    На вход принимает:
        user_id - Телеграм ID пользователя.

    Возвращает:
        Если пользователь есть в базе данных, то возвращает True.

        Если пользователь нет в базе данных, то возвращает False.
    """
    user_id = int(user_id)
    check = await get_user(user_id)

    if isinstance(check, dict):  # Если получаемый объет является словарем, то вовзращаем True
        return True

    return False


async def get_message_from_db(name: str) -> dict | None:
    """
    Возваращет текст и фото сообщения.

    На вход принимает:
        name - Название сообщения.

    Возвращает:
        Если сообщение с таким названием есть в базе данных, то возвращает словарь:
            {
                'text': text[0],
                'photo': text[1]
            }

        Если сообщение с таким названием нет в базе данных, то возвращает None:
            None
    """
    query = (f"SELECT text, photo FROM `texts` "  # noqa: S608
             f"WHERE name = '{name}'")

    text_list: list[str, str] | None = await fetch_one_row_data(query)

    if text_list is None:  # Если сообщение с таким названием нет в базе данных, возвращаем None
        return None

    return {
        "text": text_list[0],
        "photo": text_list[1]
    }


async def set_message_from_db(name: str, text: str, photo: str) -> None:
    """
    Замена текста и фото сообщения.

    На вход принимает:
        name - Название сообщения
        text - Текст сообщения
        photo - Картинка сообщения.

    Возвращает:
        Ничего не возвращает
    """
    check = await get_message_from_db(name)

    if check:
        query = ("UPDATE `texts` SET "  # noqa: S608
                 f"    text = '{text}', photo = '{photo}' "
                 f"WHERE name = '{name}'")  # noqa: S608

    else:
        query = (f"INSERT INTO `texts` "  # noqa: S608
                 f"    (name, text, photo) "
                 f"VALUES "
                 f"    ('{name}', '{text}', '{photo}')")

    await execute(query)


async def check_lottery() -> bool:
    """
    Чекает, активен ли на данный момент розыгрыш.

    На вход принимает:
        Ничего не принимает

    Возвращает:
        Если на данный момент розыгрыш активна, то возвращает True

        Если на данный момент розыгрыш не активна, то возвращает False
    """
    query = ("SELECT flag FROM `lottery` "
             "WHERE id = '1'")

    return bool(int(await fetch_one_data(query)))


async def get_data_lottery() -> dict:
    """
    Возвращает словарь с данными об розыгрыше.

    На вход принимает:
        Ничего не принимает

    Возвращает:
        Словарь с данными об розыгрыше:
            {
                'text': lottery[0],
                'photo': lottery[1],
                'numbers_amount': lottery[2],
                'purchased': lottery[3],
                'price': lottery[4],
                'booked': lottery[5],
                'win_numbers_amount': lottery[6],
                'date': lottery[7]
            }
    """
    query = ("SELECT * FROM `lottery` "
             "WHERE id = '1'")

    lottery: list[str, Any] = (await fetch_one_row_data(query))[1:-1]  # id и flag не берем

    return {
        "text": lottery[0],
        "photo": lottery[1],
        "numbers_amount": lottery[2],
        "purchased": lottery[3],
        "price": lottery[4],
        "booked": lottery[5],
        "win_numbers_amount": lottery[6],
        "date": lottery[7],
    }


async def set_data_lottery(text: str,
                           photo_id: str,
                           numbers_amount: str | int,
                           price: str | int,
                           win_numbers_amount: int | str,
                           date: str) -> None:
    """
    Изменение данных об розыгрыше.

    На вход принимает:
        text - Текст, описание приза
        photo_id - Картинка приза
        numbers_amount - Количество номерков
        price - Цена одного номерка
        win_numbers_amount - Количество победных номерков
        date - Дата создания розыгрыша

    Возвращает:
        Ничего не возвращает
    """
    query = (f"UPDATE `lottery` SET "  # noqa: S608
             f"    text = '{text}', "
             f"    photo = '{photo_id}', "
             f"    numbers_amount = '{numbers_amount}', "
             f"    price = '{price}', "
             f"    booked = '', "
             f"    flag = '1', "
             f"    purchased = '', "
             f"    win_numbers_amount = '{win_numbers_amount}', "
             f"    date = '{date}' "
             f"WHERE id = '1'")

    await execute(query)


async def close_lottery() -> None:
    """
    Закрывает активный розыгрыш.

    На вход принимает:
        Ничего не принимает

    Возвращает:
        Ничего не возвращает
    """
    query = ("UPDATE `lottery` SET "
             "    flag = '0' "
             "WHERE id = '1'")

    await execute(query)

    await null_all_numbers()  # И сразу убираем номерки клиентов
    await del_all_bookeds_from_lottery()  # И убираем все забронированные номерки

    logger.info("[DATABASE] Лотерея была остановлена, купленные номерки клиентов очищены, забронированные номерки "
                "были убраны")


async def update_purchased_lottery_numbers(number: int | str) -> None:
    """
    Добавляет к купленным номеркам еще один номерок в данные розыгрыша.

    На вход принимает:
        number - Номер купленного номерка

    Возвращает:
        Ничего не возвращает
    """
    data = await get_data_lottery()
    purchased = data["purchased"]

    # Сперва, купленные номерки с такого вида - "1,2,4,5,21" делаем вот такой - [1, 2, 4, 5, 21] (Пример)
    try:
        purchased_numbers = list(map(int, purchased.split(",")))

    except ValueError:
        purchased_numbers = []

    purchased_numbers.append(int(number))  # Добавляем в массив номерок
    purchased = ",".join(map(str, purchased_numbers))  # И обратно возвращаем в исходный вид

    query = ("UPDATE `lottery` SET "  # noqa: S608
             f"    purchased = '{purchased}' "
             "WHERE id = '1'")

    await execute(query)

    logger.info(f"[DATABASE] Добавлен новый купленный номерок в розыгрыш: {number}")


async def update_purchased_user_numbers(user_id: int | str, number: int | str) -> None:
    """
    Добавляет к купленным номеркам еще один номерок в данные пользователя.

    На вход принимает:
        user_id - Телеграм ID пользователя
        number - Номер купленного номерка

    Возвращает:
        Ничего не возвращает
    """
    data = await get_user(user_id)
    numbers_str = data["numbers"]

    # Сперва, купленные номерки с такого вида - "1,2,4,5,21" делаем вот такой - [1, 2, 4, 5, 21] (Пример)
    try:
        numbers_list = list(map(int, numbers_str.split(",")))

    except ValueError:
        numbers_list = []

    numbers_list.append(int(number))  # Добавляем в массив номерок
    numbers_str = ",".join(map(str, numbers_list))  # И обратно возвращаем в исходный вид

    query = ("UPDATE `user` SET "  # noqa: S608
             f"    numbers = '{numbers_str}' "
             f"WHERE id = '{user_id}'")

    await execute(query)

    logger.info(f"[DATABASE] Добавлен новый купленный номерок пользователю: {user_id} - {number}")


async def update_booked_lottery_numbers(number: int | str, type_append: bool = True) -> None:
    """
    Добавляет к забронированным номеркам еще один номерок, или Убирает с забронированных номерков наш номерок с данных розыгрыша.

    На вход принимает:
        number - Номер забронированного номерка
        type_append - True, если нужно добавить, False, если нужно убрать, дефолтна на добавить

    Возвращает:
        Ничего не возвращает
    """
    data = await get_data_lottery()
    booked = data["booked"]

    # Сперва, забронированные номерки с такого вида - "1,2,4,5,21" делаем вот такой - [1, 2, 4, 5, 21] (Пример)
    try:
        booked_numbers = list(map(int, booked.split(",")))
    except ValueError:
        booked_numbers = []

    if type_append:
        booked_numbers.append(int(number))  # Добавляем в массив номерок
    else:
        booked_numbers.remove(int(number))  # Убираем с массива номерок

    booked = ",".join(map(str, booked_numbers))  # И обратно возвращаем в исходный вид

    query = (f"UPDATE `lottery` SET "  # noqa: S608
             f"    booked = '{booked}' "
             f"WHERE id = '1'")

    await execute(query)

    if type_append:
        logger.info(f"[DATABASE] Добавлен новый забронированный номерок к розыгрышу: {number}")
    else:
        logger.info(f"[DATABASE] Убран забронированный номерок с розыгрыша: {number}")


async def check_user_notification(user_id: int | str) -> bool | None:
    """
    Чекает, включены ли уведомления у пользователя.

    На вход принимает:
        user_id - ID пользователя

    Возвращает:
        Если пользователь есть в базе данных, то True, если у него включены уведомления, False, если у него отключены уведомления

        Если такого пользователя нет в базе данных, то возвращает None
    """
    query = (f"SELECT notification FROM `user` "  # noqa: S608
             f"WHERE id = '{user_id}'")

    try:
        return bool(int(await fetch_one_data(query)))

    except TypeError:
        return None


async def get_users_ids_and_notifications() -> list[[int, bool], Any] | list:
    """
    Возвращает Телеграм ID и Разрешение на уведомление всех пользователей с базы данных.

    На вход принимает:
        Ничего не принимает

    Возвращает:
        Если в базе данных есть пользователи, то список из списков:
            [[user1_id, notification1(bool)], [user2_id, notification2(bool)], . . .]

        Если в базе данных нет пользователей, то пустой список:
            []
    """
    query = ("SELECT id, notification "  # noqa: S608
             "FROM `user` ")

    users: list[[int, bool], Any] | None = [
        [int(user_list[0]), bool(user_list[1])] for user_list in await fetch_all_data(query)
    ]

    if users is None:
        return []

    return users


async def set_user_notification(user_id: int | str, notification: bool) -> None:
    """
    Устанавливает разрешение на уведомления пользователя.

    На вход принимает:
        user_id - ID пользователя
        notification - True, если нужно разрешить уведомления, False, если нужно отключить уведомления

    Возвращает:
        Ничего не возвращает
    """
    query = (f"UPDATE `user` SET "  # noqa: S608
             f"    notification = '{int(notification)}' "
             f"WHERE id = '{user_id}'")

    await execute(query)

    logger.info(f"[DATABASE] Изменено разрешение на отправку уведомлений : {user_id} - {notification}")


async def get_users_ids_and_numbers_who_player_lottery() -> list[[int, [int, Any]]] | list:
    """
    Возвращает Телеграм ID и список номерков, которых игроки купили.

    На вход принимает:
        Ничего не принимает

    Возвращает:
        Если в базе данных есть пользователи, то список из списков:
            [[user1_id, [1, 2, 4, 5, 21]], [user2_id, [3, 12, 45]], . . .]

        Если в базе данных нет пользователей, то пустой список:
            []
    """
    query = ("SELECT id, numbers "  # noqa: S608
             "FROM `user` ")

    response = await fetch_all_data(query)

    if response is None:
        return []

    return [[
        int(user_list[0]), list(map(int, user_list[1].split(",")))
    ] for user_list in response]


async def del_all_bookeds_from_lottery() -> None:
    """
    Удаляет все забронированные номерки розыгрыша.

    На вход принимает:
        Ничего не принимает

    Возвращает:
        Ничего не возвращает
    """
    query = ("UPDATE `lottery` SET "
             "    booked = '' "
             "WHERE id = '1'")

    await execute(query)

    logger.info(f"[DATABASE] Убраны все забронированные номерки с розыгрыша")
