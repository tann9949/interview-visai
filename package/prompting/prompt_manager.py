from jinja2 import Environment, PackageLoader


class NewsExtractionPromptManager(object):

    def __init__(self) -> None:
        self.manager = prompt_manager = Environment(
            loader=PackageLoader("package", package_path="prompting/templates")
        )

    def system_prompt(self) -> str:
        return self.manager.get_template("system_prompt.md").render()
    
    def extract_info(self, **kwargs) -> str:
        return self.manager.get_template("extract_info.md").render(
            **kwargs
        )
