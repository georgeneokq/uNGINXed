from dataclasses import dataclass, field
from typing import TypedDict

class DirectiveDict(TypedDict):
    directive: str
    line: int
    args: list[str]
    block: list[dict]

@dataclass
class Directive:
    directive: str
    line: int
    args: list[str] = field(default_factory=list)
    block: list[dict] = field(default_factory=list)

    def get_directives(self, directive_name, recursive=True):
        def recursive_get_directives(current_directive: Directive, directives_list=[]):
            for directive_dict in current_directive.block:
                directive = Directive.from_dict(directive_dict)
                if directive_name == directive_dict["directive"]:
                    directives_list.append(directive)
                recursive_get_directives(directive, directives_list)

            return directives_list

        directives = recursive_get_directives(self)

        return directives

    @staticmethod
    def from_dict(dict: DirectiveDict):
        return Directive(dict["directive"], dict["line"], dict.get("args", []), dict.get("block", []))