import rich
import typer
from browser.browser import FBBrowser
from services.grabber import grab_new_posts


def grab():
    if not FBBrowser.is_installed():
        rich.print(
            f"[red]Browser is not installed. Please run `fbgram setup` first.[/red]"
        )
        raise typer.Abort()

    with FBBrowser() as browser:
        if not browser.is_logged_in():
            rich.print(
                f"[red]You are not logged in to Facebook. Please run `fbgram setup` first.[/red]"
            )
            raise typer.Abort()
        rich.print("Grabbing new posts from Facebook...")
        new_posts_count = grab_new_posts(browser)
        if new_posts_count == 0:
            rich.print("No new posts found.")
            return
    rich.print(f"Grabbed {new_posts_count} new posts from Facebook.")
    return
