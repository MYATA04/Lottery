import toml

from app.logger import logger


class Config:

    def __init__(self) -> None:
        with open("config.toml") as file:
            self._config_data = toml.load(file)

        self.BOT_TOKEN = self._config_data['BOT_TOKEN']
        self.ADMINS_IDS = self._config_data['ADMINS_IDS']
        self.PAY_TOKEN = self._config_data['PAY_TOKEN']

    def __write_to_config(self) -> None:
        """
        Меняет все данные в конфиг файле - config.toml
        """
        with open("config.toml", "w") as file:
            toml.dump(self._config_data, file)

        logger.info(f"[CONFIG] Данные конфига изменились:"
                    f"\n\t{self._config_data}")

    def add_del_admin(self, user_id: int | str, flag: bool = True) -> None:
        """
        Добавляет новый ADMIN_ID в конфиг файл - config.toml если flag = True
        Удаляет ADMIN_ID из конфиг файла - config.toml если flag = False
        """
        if flag:
            self._config_data['ADMINS_IDS'].append(int(user_id))
            logger.info(f"[CONFIG] Админ был добавлен: {user_id}")

        else:
            self._config_data['ADMINS_IDS'].remove(int(user_id))
            logger.info(f"[CONFIG] Админ был удален: {user_id}")

        self.ADMINS_IDS = self._config_data['ADMINS_IDS']

        self.__write_to_config()

    def set_pay_token(self, new_token: str) -> None:
        """
        Меняет токен для оплаты в конфиг файле - config.toml
        """
        self._config_data['PAY_TOKEN'] = new_token
        self.PAY_TOKEN = new_token

        logger.info(f"[CONFIG] Изменен токен для оплаты: {new_token}")

        self.__write_to_config()

    def reload_objects(self):
        """
        Меняет данные в классе на новые
        """
        with open("config.toml") as file:
            self._config_data = toml.load(file)

        self.BOT_TOKEN = self._config_data['BOT_TOKEN']
        self.ADMINS_IDS = self._config_data['ADMINS_IDS']
        self.PAY_TOKEN = self._config_data['PAY_TOKEN']


config = Config()
