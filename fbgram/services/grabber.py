from browser import FBBrowser
from db.models import Post
from services.parser import PostParser, parse_posts_html

MAX_PAGES_TO_GRAB = 10


def grab_new_posts(browser: FBBrowser, pages_to_grab: int = MAX_PAGES_TO_GRAB) -> int:
    """
    Grabs new posts from the Facebook feed and saves them to the database.

    Args:
        browser (FBBrowser): An instance of the FBBrowser class.
        pages_to_grab (int): The maximum number of pages to grab.

    Returns:
        int: The number of new posts that were grabbed and saved to the database.
    """
    new_posts_counter = 0
    for page_number in range(pages_to_grab):
        page_html = browser.get_feed_page_html()
        posts_html = parse_posts_html(page_html)
        for post_html in posts_html:
            post_parser = PostParser(post_html)
            if Post.exists().where(Post.id == post_parser.id).run_sync():
                return new_posts_counter
            new_post = Post(
                id=post_parser.id,
                short_html=post_html,
                metadata=post_parser.metadata,
            )
            new_post.save().run_sync()
            new_posts_counter += 1

        browser.goto_next_feed_page()
    return new_posts_counter
