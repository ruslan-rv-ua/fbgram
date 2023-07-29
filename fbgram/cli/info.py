from cli.setup import is_telegram_bot_set_up
from db.models import Post, PostStatus
from piccolo.query.methods.select import Count
from rich.console import Console
from rich.table import Table

from fbgram import __version__
from fbgram.browser.browser import FBBrowser

console = Console()


def info_facilities():
    table = Table(title="FBGram Info", show_header=True, header_style="bold")
    table.add_column("Item", style="dim")
    table.add_column("Value")
    table.add_column("Description")

    table.add_row(
        "FBGram version",
        __version__,
    )

    table.add_row(
        "Telegram Bot is set up",
        "yes" if is_telegram_bot_set_up() else "no",
        "Run `fbgram setup` to set up the Telegram bot"
        if not is_telegram_bot_set_up()
        else "",
    )

    table.add_row(
        "Browser is installed",
        "yes" if FBBrowser.is_installed() else "no",
        "Run `fbgram setup` to install the browser"
        if not FBBrowser.is_installed()
        else "",
    )

    with console.status("Checking..."):
        with FBBrowser() as browser:
            is_logged_in = browser.is_logged_in()

    table.add_row(
        "You are logged in to Facebook",
        "yes" if is_logged_in else "no",
        "Run `fbgram setup` to log in to Facebook" if not is_logged_in else "",
    )

    console.print(table)


def info_db():
    table = Table(
        title="Posts in Database", show_header=True, header_style="bold white"
    )

    table.add_column("Status")
    table.add_column("Count")
    table.add_column("Description")

    statuses_count = Post.select(Post.status, Count()).group_by(Post.status).run_sync()
    statuses_mapping = {item["status"]: item["count"] for item in statuses_count}

    new_count = statuses_mapping.get(PostStatus.NEW, 0)
    table.add_row(
        "new",
        str(new_count),
        "Run [bold white]`fbgram send`[/bold white] to send them to Telegram"
        if new_count
        else "",
    )

    sent_count = statuses_mapping.get(PostStatus.SENT, 0)
    table.add_row(
        "sent",
        str(sent_count),
        "",
    )

    table.add_row("total", str(sum(statuses_mapping.values())))

    console.print(table)


def info():
    info_facilities()
    info_db()
