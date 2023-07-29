import typer

from .grab import grab
from .info import info
from .send import send
from .setup import setup

app = typer.Typer(
    no_args_is_help=True, add_completion=False, rich_markup_mode="markdown"
)


@app.callback()
def docs():
    """# FBGram — Facebook to Telegram

    This command is executed when no other subcommand is passed.


    > This is the help of the main command.


    #! TODO: Add more help here"""
    ...


app.command(name="grab")(grab)

app.command(name="setup")(setup)
app.command(name="send")(send)
app.command(name="info")(info)


@app.command(name="news")
def news():
    """Grab new posts from Facebook and send them to Telegram"""
    grab()
    send()
