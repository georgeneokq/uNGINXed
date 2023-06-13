import crossplane
from .directive import Directive, DirectiveDict
from typing import Callable


class NginxConfig:
    def __init__(self, filepath: str):
        self.filepath: str = filepath
        self.raw: dict | None = crossplane.parse(filepath)
        self.parsed: list[Directive] = []

        config: list[DirectiveDict] = self.raw["config"][0]["parsed"]

        for directive_dict in config:
            directive = Directive()
            self.parsed.append(directive)
            recursive_initialize_directives(directive, directive_dict)

    def get_raw_config(self) -> dict | None:
        return None if self.raw is None else self.raw['config'][0]

    def get_directive(self, directive: str) -> dict | None:
        '''
        Retrives a dictonary relating to a directive
        '''
        if self.raw is None:
            return None
        for block in self.parsed:
            if 'directive' in block.keys() and block['directive'] == directive:
                return block
        return None

    def get_directive_blocks(self, directive: str) -> list[dict]:
        '''
        Retrieves a list of blocks associated with a directive.
        '''
        directive_dict = self.get_directive(directive)
        return [] if directive_dict is None else directive_dict['block']

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


def recursive_initialize_directives(directive: Directive, directive_dict: DirectiveDict):
    directive.directive = directive_dict["directive"]
    directive.line = directive_dict["line"]
    directive.args = directive_dict["args"]
    directive.block = []

    if directive_dict.get("block") is not None:
        for sub_directive_dict in directive_dict.get("block"):
            sub_directive = Directive()
            recursive_initialize_directives(sub_directive, sub_directive_dict)
            directive.block.append(sub_directive)
