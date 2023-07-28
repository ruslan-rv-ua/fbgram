from fbgram.browser import FBBrowser


def not_test_browser_launch():
    # TODO: test this
    assert FBBrowser.is_installed()
    browser = FBBrowser(headless=False)
    browser.start()
    assert browser.is_logged_in() == False
    browser.stop()
