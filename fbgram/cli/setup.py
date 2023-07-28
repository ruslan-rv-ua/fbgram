from random import randint
from time import sleep

import rich
import typer
from db.models import Settings
from rich.prompt import Prompt
from telegram.telegram import TelegramBot

MAX_SETUP_TELEGRAM_BOT_ATTEMPTS = 3


###############################################
# Telegram bot setup
###############################################
def is_telegram_bot_set_up():
    settings = Settings.load()
    return (
        settings.telegram_bot_token is not None
        and settings.telegram_chat_id is not None
    )


def setup_telegram_bot() -> None:
    if is_telegram_bot_set_up():
        rich.print("[green]Telegram bot is set up.[/green]")
        return
    rich.print("You have to set up a telegram bot to use fbgram.")
    rich.print("To do so, follow these steps:")
    rich.print("1. Open Telegram and search for [bold]@BotFather[/bold]")
    rich.print("2. Send [bold]/newbot[/bold] command to BotFather")
    rich.print("3. Follow the instructions to create a new bot")
    rich.print("4. Copy the bot token and paste it here:")

    attempts = MAX_SETUP_TELEGRAM_BOT_ATTEMPTS
    while True:
        token = Prompt.ask("Bot token")
        try:
            updates = TelegramBot.get_updates(token=token)
        except Exception as e:
            rich.print(f"[red]Error: {e}[/red]")
            attempts -= 1
            if attempts == 0:
                rich.print(
                    f"You failed to set up the telegram bot {MAX_SETUP_TELEGRAM_BOT_ATTEMPTS} times."
                )
                raise typer.Abort()
            rich.print('Try again or press "Ctrl+C" to exit.')
            continue
        break

    confirm_number = str(randint(100000, 999999))
    rich.print(
        "Now you have to confirm that you are the owner of this bot. To do this, follow these steps:"
    )
    rich.print("1. Open Telegram and search for your bot")
    rich.print("2. Send [bold]/start[/bold] command to your bot")
    rich.print(f"3. Enter the following number: [bold]{confirm_number}[/bold]")
    while not updates or updates[-1]["message"]["text"] != confirm_number:
        sleep(1)
        updates = TelegramBot.get_updates(token=token)

    chat_id = updates[-1]["message"]["chat"]["id"]
    settings = Settings.load()
    settings.telegram_bot_token = token
    settings.telegram_chat_id = chat_id
    settings.save()
    bot = TelegramBot(token=token, chat_id=chat_id)
    bot.send_test_message()
    rich.print("[green]Telegram bot set up successfully[/green]]\n")


###############################################
# Browser setup
###############################################
def setup_browser():
    print("Setting up browser")


def login_to_facebook():
    print("Logging in to facebook")


def setup():
    """Setup the CLI

    This command is executed when no other subcommand is passed."""
    setup_telegram_bot()
    setup_browser()
    login_to_facebook()
