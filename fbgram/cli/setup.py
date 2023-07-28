from random import randint
from time import sleep

import rich
import typer
from browser.browser import FBBrowser
from db.models import Settings
from rich.prompt import Prompt
from telegram.telegram import TelegramBot

MAX_SETUP_TELEGRAM_BOT_ATTEMPTS = 3
MAX_LOGIN_ATTEMPTS = 3


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
    if FBBrowser.is_installed():
        rich.print(
            f"[green]Browser is installed. Using {FBBrowser.BROWSER_NAME.upper()}."
        )
        return
    rich.print(
        f"Browser is not installed. Installing {FBBrowser.BROWSER_NAME.upper()}..."
    )
    try:
        FBBrowser.install()
    except Exception as e:
        rich.print(f"[red]Error: {e}[/red]")
        raise typer.Abort()
    rich.print(
        f"[green]Browser {FBBrowser.BROWSER_NAME.upper()} installed successfully.[/green]\n"
    )


def login_to_facebook():
    with FBBrowser() as browser:
        if browser.is_logged_in():
            rich.print("[green]You are already logged in to Facebook.[/green]")
            return

    attempts = MAX_LOGIN_ATTEMPTS
    while True:
        rich.print("Log in to Facebook in the browser window that just opened.")
        rich.print("You should see your feed after logging in.")
        rich.print("Press any key when you are done.")
        with FBBrowser(headless=False) as browser:
            attempts -= 1
            typer.pause()
            if browser.is_logged_in():
                break
        if attempts == 0:
            rich.print(f"You failed to log in to Facebook {MAX_LOGIN_ATTEMPTS} times.")
            raise typer.Abort()
        rich.print("Seems like you are not logged in yet.")
        rich.print('Try again or press "Ctrl+C" to exit.')

    rich.print("[green]You are logged in to Facebook.[/green]\n")


def setup():
    """Set up FBGram"""
    setup_telegram_bot()
    setup_browser()
    login_to_facebook()
