import rich
from db.models import Post, PostStatus, Settings
from services.parser import PostParser
from telegram.telegram import TelegramBot


def send(status: PostStatus = PostStatus.NEW) -> None:
    settings = Settings.load()
    bot = TelegramBot(
        token=settings.telegram_bot_token, chat_id=settings.telegram_chat_id
    )
    posts_to_send = Post.objects().where(Post.status == status).run_sync()
    if not posts_to_send:
        rich.print("Nothing to send.")
        return
    rich.print(f"Sending {len(posts_to_send)} posts to Telegram...")
    sent_count = 0
    for post in posts_to_send:
        message = PostParser(post.short_html).get_short_text()
        try:
            bot.send_message(message)
            post.status = PostStatus.SENT
            sent_count += 1
        except Exception as e:
            #! TODO: log this: rich.print(f"[red]Error: {e}[/red]")
            post.status = PostStatus.FAILED
        post.save().run_sync()
    rich.print(f"Sent {sent_count} posts to Telegram.")
