from airflow.hooks.base_hook import BaseHook
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
import logging
import time


class SeleniumHook(BaseHook):
    """
    Creates a Selenium Docker container on the host and controls the
    browser by sending commands to the remote server.
    """

    def __init__(self, selenium_address, container_download_path):
        logging.info("initialised hook")
        self.selenium_address = selenium_address
        self.sel_downloads = container_download_path

    def create_driver(self):
        """
        creates and configure the remote Selenium webdriver.
        """
        logging.info("creating driver")
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920x1080")
        chrome_driver = "http://{}:4444/wd/hub".format(self.selenium_address)
        while True:
            try:
                driver = webdriver.Remote(
                    command_executor=chrome_driver,
                    desired_capabilities=DesiredCapabilities.CHROME,
                    options=options,
                )
                print("remote ready")
                break
            except:
                print("remote not ready, sleeping for ten seconds.")
                time.sleep(10)
        # Enable downloads in headless chrome.
        driver.command_executor._commands["send_command"] = (
            "POST",
            "/session/$sessionId/chromium/send_command",
        )
        params = {
            "cmd": "Page.setDownloadBehavior",
            "params": {"behavior": "allow", "downloadPath": self.sel_downloads},
        }
        driver.execute("send_command", params)
        self.driver = driver

    def run_script(self, script, args):
        """
        This is a wrapper around the python script which sends commands to
        the docker container. The first variable of the script must be the web driver.
        """
        script(self.driver, *args)
