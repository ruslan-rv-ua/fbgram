import json
from dataclasses import dataclass
from typing import Self
from urllib.parse import parse_qs, urljoin, urlparse

from emoji import replace_emoji
from selectolax.parser import HTMLParser, Node

FB_BASE_URL: str = "https://d.facebook.com/"


def parse_posts_html(posts_html: str) -> list[str]:
    """
    Parse the HTML of a Facebook feed page and return a list of posts HTML.

    Args:
        posts_html (str): The HTML of a Facebook feed page.

    Returns:
        list[str]: A list of posts HTML.
    """
    parser = HTMLParser(posts_html)
    article_tags = parser.css("section > article")
    return [article_tag.html or "" for article_tag in article_tags]


@dataclass
class LinkParser:
    url: str | None
    text: str
    is_external: bool

    @classmethod
    def from_node(cls, a_tag: Node) -> Self:
        text = a_tag.text().strip()
        if is_http_url(text):
            return cls(url=text, text=text, is_external=True)

        url = a_tag.attrs.get("href", default="").strip()
        if not url:
            return cls(url=None, text=text, is_external=False)

        redirect_urls = find_links_in_params(url)
        external_redirect_urls = [
            redirect_url for redirect_url in redirect_urls if is_http_url(redirect_url)
        ]
        if external_redirect_urls:
            url = external_redirect_urls[0]

        if not is_http_url(url):  # this is internal Facebook link
            return cls(url=urljoin(FB_BASE_URL, url), text=text, is_external=False)

        return cls(url=url, text=text, is_external=True)

    def as_markdown(self) -> str:
        return f"[{self.text}]({self.url})"


class HeaderParser:
    def __init__(self, text: str) -> None:
        cleaned_text = text.replace(" > \u200e", " — ")
        if not cleaned_text.endswith("."):
            cleaned_text = f"{cleaned_text}."
        cleaned_text = f"{cleaned_text}\n\n"
        self.text = cleaned_text

    @classmethod
    def from_node(cls, h3_tag: Node) -> Self:
        return cls(text=h3_tag.text())


class PostParser:
    def __init__(self, article_tag_html: str | None) -> None:
        if not article_tag_html:
            raise ValueError("article_tag_html cannot be empty or None.")
        self.article_tag_html = article_tag_html

        parser = HTMLParser(article_tag_html)
        article_tag = parser.css_first("article")

        self.metadata: dict = json.loads(article_tag.attrs.get("data-ft", default="{}"))
        self.id = self.metadata.get("top_level_post_id")

    @property
    def full_post_url(self) -> str:
        """Returns the URL to the full post.

        Returns:
            A string representing the URL to the full post.
        """
        return urljoin(FB_BASE_URL, self.id)

    def as_dict(self) -> dict:
        """
        Returns a dictionary representation of the post.

        Returns:
            dict: A dictionary containing the post's id, metadata, and short HTML.
        """
        return {
            "id": self.id,
            "metadata": self.metadata,
            "short_html": self.article_tag_html,
        }

    def get_short_text(
        self,
        remove_emoji: bool = True,
        keep_links: bool = True,
        facebook_post_link_text: str | None = "See full post on Facebook",
    ) -> str:
        """
        Returns the short text of the post.

        Args:
            remove_emoji (bool, optional): Whether to remove emojis from the text. Defaults to True.

        Returns:
            str: The short text of the post.
        """
        parser = HTMLParser(self.article_tag_html)
        article_tag = parser.css_first("article")

        # unwrap <div> tag
        div_tag = article_tag.css_first("article > div")
        if div_tag is not None:
            div_tag.unwrap()
        # unwarp unwanted tags
        article_tag.unwrap_tags(["span", "strong", "div"])
        # remove unwanted tags
        article_tag.strip_tags(tags=["footer", "img"])
        # unwrap all <p> tags
        for p_tag in article_tag.css("p"):
            p_tag.replace_with(f"{p_tag.text()}\n")

        # h3 headers to text
        for h3_tag in article_tag.css("h3"):
            h3_tag.replace_with(HeaderParser.from_node(h3_tag).text)

        # process inner article tags
        inner_article_tagss = article_tag.css("article > article")
        for inner_article_tag in inner_article_tagss:
            inner_post_parser = PostParser(article_tag_html=inner_article_tag.html)
            inner_article_tag.replace_with(
                inner_post_parser.get_short_text(
                    remove_emoji=remove_emoji,
                    keep_links=keep_links,
                    facebook_post_link_text=None,
                )
            )

        # process links
        for a_tag in article_tag.css("a"):
            link_parser = LinkParser.from_node(a_tag)
            if not link_parser.text:
                a_tag.decompose()
                continue

            # check if this is hashtag
            if link_parser.text.startswith("#"):
                a_tag.decompose()
                continue

            # add whitespace before and after link text
            link_parser.text = f" {link_parser.text} "

            if keep_links and link_parser.is_external:
                a_tag.replace_with(link_parser.as_markdown())
            else:
                a_tag.replace_with(link_parser.text)

        # replace all <br> tags with new line
        for br_tag in article_tag.css("br"):
            br_tag.replace_with("\n")

        # get post text
        article_text = cleanup_text(
            article_tag.text(),
            remove_emoji=remove_emoji,
            remove_consecutive_newlines=False,
            remove_consecutive_spaces=False,
            strip_every_line=True,
        )

        # add link to full post
        if facebook_post_link_text is not None:
            full_post_link = LinkParser(
                url=self.full_post_url,
                text=facebook_post_link_text,
                is_external=True,
            ).as_markdown()
            article_text = f"{article_text}\n\n{full_post_link}"

        return article_text


def is_http_url(url: str) -> bool:
    """
    Returns whether a URL is a HTTP URL.

    Args:
        url (str): The URL to check.

    Returns:
        A boolean representing whether the URL is a HTTP URL.
    """
    return url.startswith("http://") or url.startswith("https://")


def remove_long_query_params(url: str) -> None:
    """
    Removes query parameters with long values from a URL.

    Args:
        url (str): The URL to remove query parameters from.

    Returns:
        A string representing the URL with query parameters removed.
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    for param, values in query_params.items():
        for value in values:
            if len(value) > 128:
                url = url.replace(f"{param}={value}", "")


def find_links_in_params(url: str) -> list:
    """
    Finds links in the URL's parameters and returns them.

    Args:
        url (str): The URL to search for links in the parameters.

    Returns:
        A list of links found in the URL's parameters.
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    links = []
    for param in query_params.values():
        for value in param:
            if "http" in value:
                links.append(value)
    return links


def cleanup_text(
    text: str,
    remove_emoji: bool = True,
    remove_consecutive_newlines: bool = True,
    remove_consecutive_spaces: bool = True,
    strip_every_line: bool = True,
) -> str:
    text = text.strip()
    # remove consecutive newlines
    if remove_consecutive_newlines:
        while "\n\n" in text:
            text = text.replace("\n\n", "\n")
    # remove consecutive spaces
    if remove_consecutive_spaces:
        while "  " in text:
            text = text.replace("  ", " ")
    # remove emoji
    if remove_emoji:
        text = replace_emoji(text)
    # strip every line
    if strip_every_line:
        text = "\n".join(line.strip() for line in text.split("\n"))

    return text
