from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from selenium_plugin.hooks.selenium_hook import SeleniumHook


class SeleniumOperator(BaseOperator):
    """
    Selenium Operator
    """

    template_fields = ["script_args"]

    @apply_defaults
    def __init__(
        self, selenium_address, script, script_args, container_download_path="", *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.selenium_address = selenium_address
        self.container_download_path = container_download_path
        self.script = script
        self.script_args = script_args

    def execute(self, context):
        hook = SeleniumHook(self.selenium_address, self.container_download_path)
        hook.create_driver()
        hook.run_script(self.script, self.script_args)
