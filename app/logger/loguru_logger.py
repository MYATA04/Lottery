import sys

from loguru import logger

logger.remove()  # Убираем базовые настройки логгера

logger = logger.opt(colors=True)  # Разрешаем теги для форматирования

# Логгер для файлов с архивацией после того как файл превысет лимит в 100МБ в весе или каждые 30 дней
logger.add(
    "logger/logs/logs.log",
    rotation="100 MB",
    compression="zip",
    retention="30 days",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {file}:{line} | {message}",
    level="DEBUG",
)

# Логгер для консоли с тегами для форматирования
logger.add(
    sys.stdout,
    colorize=True,
    format="<b><e>{time:YYYY-MM-DD at HH:mm:ss}</e></b> | <c>{level}</c> | {file}:{line} | <level>{message}</level>",
    level="DEBUG",
)

logger.level(name="INFO", color="<m>")
logger.level(name="CRITICAL", color="<v><r><bold>")
logger.level(name="DEBUG", color="<c>")
logger.level(name="WARNING", color="<y><bold>")
logger.level(name="ERROR", color="<r><bold>")
