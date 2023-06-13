import crossplane
from .directive import Directive, DirectiveDict, DirectiveUtil


class NginxConfig:
    """Represents an NGINX config file"""
    def __init__(self, filepath: str):
        """Instantiate an NginxConfig object.

        Args:
            filepath (str): Absolute or relative path to the config file
        """
        self.filepath: str = filepath
        self.raw: dict | None = crossplane.parse(filepath)
        self.directives: list[Directive] = []

        config: list[DirectiveDict] = self.raw["config"][0]["parsed"]

        for directive_dict in config:
            directive = Directive()
            self.directives.append(directive)
            DirectiveUtil.recursive_initialize_directives(
                directive,
                directive_dict
            )

    def __repr__(self) -> str:
        return str(self.raw)
