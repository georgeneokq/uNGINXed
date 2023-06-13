import crossplane
from .directive import Directive, DirectiveDict, DirectiveUtil
from typing import Callable


class NginxConfig:
    """Represents an NGINX config file
    """
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


class ConfigUtil:
    @staticmethod
    def traverse_config_raw(directives: list[DirectiveDict],
                            callback: Callable[[DirectiveDict, DirectiveDict], None]) -> None:
        """
        Traverses through a config list generated by crossplane,
        and runs a callback on each config.

        parameters:
            directives: List of directives to traverse
            callback(current_directive: Directive, parent_directive: Directive)
        """
        for directive in directives:
            callback(directive)
            ConfigUtil.traverse_config_raw(
                directive.get("block", []),
                callback
            )
