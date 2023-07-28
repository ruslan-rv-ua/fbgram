from cli.setup import is_telegram_bot_set_up
from db.models import Post
from piccolo.query.methods.select import Count
from rich.console import Console
from rich.table import Table

console = Console()


def info_facilities():
    table = Table(title="FBGram Info", show_header=True, header_style="bold")
    table.add_column("Item", style="dim")
    table.add_column("Value")
    table.add_column("Description")

    table.add_row(
        "Telegram Bot is set up",
        "yes" if is_telegram_bot_set_up() else "no",
        "Run `fbgram setup` to set up the Telegram bot"
        if not is_telegram_bot_set_up()
        else "",
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
    print(statuses_mapping)
    for status in ["new", "sent", "failed"]:
        table.add_row(status, str(statuses_mapping.get(status, 0)))

    table.add_row("total", str(sum(statuses_mapping.values())))

    console.print(table)


def info():
    # info_facilities()
    info_db()
