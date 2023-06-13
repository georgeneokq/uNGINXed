from dataclasses import dataclass, field
from typing import TypedDict, Callable, Self


class DirectiveDict(TypedDict):
    directive: str
    line: int
    args: list[str]
    block: list[dict]


@dataclass
class Directive:
    directive: str = None
    line: int = None
    args: list[str] = field(default_factory=list)
    block: list[Self] = field(default_factory=list)


class DirectiveUtil:
    @staticmethod
    def traverse(directives: list[Directive],
                 callback: Callable[[Directive], None]) -> None:
        """
        Given a list of directives, recursively traverse through the
        tree of directives and performs a callback on each directive.

        params:
            directives: list of Directives objects
            callback(directive): Operation to perform
        """
        for directive in directives:
            callback(directive)
            DirectiveUtil.traverse(directive.block, callback)

    @staticmethod
    def get_directives(directive_name: str,
                       directives: list[Directive]) -> None:
        """
        Given a list of Directives objects and a directive name, retrieve all
        Directive objects with the given name.

        params:
            directive_name: directive name to search for
            directives: list of directives to search through
        """
        retrieved_directives: list[Directive] = []

        def traversal_callback(directive: Directive):
            if directive.directive == directive_name:
                retrieved_directives.append(directive)

        DirectiveUtil.traverse(directives, traversal_callback)

        return retrieved_directives

    @staticmethod
    def recursive_initialize_directives(directive: Directive,
                                        directive_dict: DirectiveDict) -> None:
        directive.directive = directive_dict["directive"]
        directive.line = directive_dict["line"]
        directive.args = directive_dict["args"]
        directive.block = []

        if directive_dict.get("block") is not None:
            for sub_directive_dict in directive_dict.get("block"):
                sub_directive = Directive()
                DirectiveUtil.recursive_initialize_directives(
                    sub_directive,
                    sub_directive_dict
                )
                directive.block.append(sub_directive)