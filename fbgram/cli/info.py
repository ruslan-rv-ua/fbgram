from cli.setup import is_telegram_bot_set_up
from db.models import Post, PostStatus
from rich.console import Console
from rich.table import Table

from fbgram import __version__
from fbgram.browser.browser import FBBrowser

console = Console()


def info_facilities():
    table = Table(title="FBGram Info", show_header=False, header_style="bold")
    table.add_column("Item")
    table.add_column("Value")

    table.add_row(
        "FBGram version",
        __version__,
    )

    table.add_row(
        "Telegram Bot is set up",
        "yes"
        if is_telegram_bot_set_up()
        else "no, run [bold white]`fbgram setup`[/bold white]",
    )

    table.add_row(
        "Browser is installed",
        "yes"
        if FBBrowser.is_installed()
        else "no, run [bold white]`fbgram setup`[/bold white]",
    )

    with console.status("Checking..."):
        with FBBrowser() as browser:
            is_logged_in = browser.is_logged_in()

    table.add_row(
        "You are logged in to Facebook",
        "yes" if is_logged_in else "no, run [bold white]`fbgram setup`[/bold white]",
    )

    console.print(table)


def info_db():
    table = Table(
        title="Posts in Database", show_header=True, header_style="bold white"
    )

    table.add_column("Status")
    table.add_column("Count")

    statuses_mapping = Post.get_posts_count_by_status()

    new_count = statuses_mapping.get(PostStatus.NEW, 0)
    column_2 = str(new_count)
    if new_count:
        column_2 += (
            "\nRun [bold white]`fbgram grab`[/bold white] to grab them from Facebook."
        )
    table.add_row("new", column_2)

    failed_count = statuses_mapping.get(PostStatus.FAILED, 0)
    column_2 = str(failed_count)
    if failed_count:
        column_2 += "\nRun [bold white]`fbgram send --status failed`[/bold white] to retry sending them to Telegram."
    table.add_row("failed", column_2)

    sent_count = statuses_mapping.get(PostStatus.SENT, 0)
    column_2 = str(sent_count)
    table.add_row("sent", column_2)

    total_count = sum(statuses_mapping.values())
    column_2 = str(total_count)
    table.add_row("total", column_2)

    console.print(table)


def info():
    info_facilities()
    info_db()
