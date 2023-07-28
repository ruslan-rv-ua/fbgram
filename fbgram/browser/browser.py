from pathlib import Path
from subprocess import run
from typing import Self

from playwright._impl._api_types import TimeoutError  # type: ignore
from playwright._impl._driver import compute_driver_executable  # type: ignore
from playwright._impl._driver import get_driver_env
from playwright.sync_api import sync_playwright  # type: ignore


class FBBrowserError(Exception):
    pass


class NoMoreFeedPagesException(FBBrowserError):
    pass


class BrowserAlreadyRunningException(FBBrowserError):
    pass


class BrowserNotRunningException(FBBrowserError):
    pass


class FBBrowser:
    BROWSER_NAME = "firefox"
    BROWSER_EXECUTABLE_NAME = "firefox.exe"
    BROWSER_DATA_DIR = "data"

    LOGIN_INPUT_SELECTOR = "#m_login_email"
    MORE_POSTS_LINK_SELECTOR = "#objects_container section+a"
    FB_RECENT_POSTS_URL = "https://d.facebook.com/home.php?sk=h_chr"

    def __init__(self, headless: bool = True) -> None:
        self.headless = headless
        self.executable_path = FBBrowser.find_executable()
        self.user_data_dir = Path(__file__).resolve().parent / self.BROWSER_DATA_DIR

        self.sync_playwright = None
        self.browser = None
        self.feed_page = None

    def start(self) -> None:
        if self.sync_playwright is not None or self.browser is not None:
            raise BrowserAlreadyRunningException("Browser is already running")
        self.sync_playwright = sync_playwright().start()
        engine = getattr(self.sync_playwright, self.BROWSER_NAME)
        try:
            self.browser = engine.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=self.headless,
                executable_path=self.executable_path,
            )
        except Exception as e:
            raise FBBrowserError(f"Error while launching browser: {e}")
        if self.browser is None:
            raise FBBrowserError("Error while launching browser")
        self.feed_page = self.browser.pages[0]
        self.feed_page.goto(self.FB_RECENT_POSTS_URL)

    def stop(self) -> None:
        if self.sync_playwright is None or self.browser is None:
            raise BrowserNotRunningException("Browser is not running")
        self.browser.close()
        self.sync_playwright.stop()  # type: ignore
        self.feed_page = None
        self.browser = None
        self.sync_playwright = None

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(self, exception_class, exception_value, traceback):
        self.stop()
        if isinstance(exception_value, TimeoutError):
            return True
        return False

    def is_logged_in(self) -> bool:
        """
        Checks if the user is currently logged in to Facebook.

        Returns:
            A boolean indicating whether the user is logged in or not.
        """
        if self.feed_page is None:
            return False
        login_input = self.feed_page.query_selector(self.LOGIN_INPUT_SELECTOR)
        return login_input is None

    def get_feed_page_html(
        self,
    ) -> str:
        """
        Returns the HTML content of the current Facebook feed page.

        Returns:
            A string containing the HTML content of the current Facebook feed page.
        """
        if self.feed_page is None:
            raise BrowserNotRunningException("Browser is not running")
        return self.feed_page.content()

    def goto_next_feed_page(
        self,
    ) -> None:
        """
        Clicks on the "More Posts" link on the current Facebook feed page to navigate to the next page.

        Raises:
            NoMoreFeedPagesException: If there are no more feed pages to navigate to.
        """
        if self.feed_page is None:
            raise BrowserNotRunningException("Browser is not running")
        self.feed_page.click(self.MORE_POSTS_LINK_SELECTOR)

    ###############################################################################
    # browser installation
    ###############################################################################

    @classmethod
    def install(cls) -> int:
        """
        Installs the latest version of the browser specified by the class constant BROWSER_NAME.

        Returns:
            The return code of the installation process.
        """
        driver_executable = compute_driver_executable()
        env = get_driver_env()
        current_path = Path(__file__).resolve().parent
        env.update({"PLAYWRIGHT_BROWSERS_PATH": str(current_path)})

        completed_process = run(
            [
                str(driver_executable),
                "install",
                cls.BROWSER_NAME,
            ],
            env=env,
        )
        return completed_process.returncode

    @classmethod
    def is_installed(cls) -> bool:
        """
        Check if the latest version of the browser specified by the class constant BROWSER_NAME is installed.

        Returns:
            True if the browser is installed, False otherwise.
        """
        return cls.find_executable() is not None

    @classmethod
    def find_executable(cls) -> Path | None:
        """Finds the path to the executable of the latest installed version of the browser specified by the class constant
        BROWSER_NAME.

        Returns:
            The path to the executable of the latest installed version of the browser specified by the class constant
            BROWSER_NAME, or None if the browser is not installed.
        """
        current_path = Path(__file__).resolve().parent
        browser_paths = sorted(current_path.glob(f"{cls.BROWSER_NAME}-*"))
        if len(browser_paths) == 0:
            return None
        latest_browser_path = browser_paths[-1]
        verification_file = latest_browser_path / "INSTALLATION_COMPLETE"
        if not verification_file.exists():
            return None
        executable_path = (
            latest_browser_path / cls.BROWSER_NAME / cls.BROWSER_EXECUTABLE_NAME
        )
        return executable_path
