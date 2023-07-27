from fbgram.services.parser import LinkParser, parse_posts_html


# parse_posts_html
# Path: fbgram\services\parser.py
def test_parse_posts_html():
    assert parse_posts_html(posts_html="") == []


def test_link_parser():
    link_parser = LinkParser(
        url="https://www.facebook.com/hashtag/hashtag",
        text="#hashtag",
        is_external=True,
    )
    assert (
        link_parser.as_markdown()
        == "[#hashtag](https://www.facebook.com/hashtag/hashtag)"
    )
