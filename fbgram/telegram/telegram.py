from datetime import datetime
from typing import Literal

from notifiers import get_notifier


class TelegramBot:
    notifier = get_notifier("telegram")

    def __init__(self, token: str, chat_id: str) -> None:
        self.token = token
        self.chat_id = chat_id

    def send_message(
        self,
        message: str,
        parse_mode: Literal["html", "markdown"] = "markdown",
        disable_web_page_preview: bool = True,
        disable_notification: bool = True,
    ) -> None:
        self.notifier.notify(
            token=self.token,
            chat_id=self.chat_id,
            message=message,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
        )

    def send_test_message(self) -> None:
        current_datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Test message from fbgram at {current_datetime_str}"
        self.send_message(message=message, disable_notification=False)

    @classmethod
    def get_updates(cls, token: str) -> list:
        updates = cls.notifier.updates(token=token)
        return updates
