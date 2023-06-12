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
                 callback: Callable[[Directive, Directive], None]) -> None:
        """
        Given a list of directives, recursively traverse through the
        tree of directives and performs a callback on each directive.

        params:
            directives: top-level list of directives
            callback(current_directive, parent_directive): Operation to perform
        """
        directive: Directive
        for directive in directives:
            callback(directive)
            DirectiveUtil.traverse(directive.block, callback)

    @staticmethod
    def get_directives(directive_name: str, directives: list[Directive]):
        retrieved_directives: list[Directive] = []

        def traversal_callback(directive: Directive):
            if directive.directive == directive_name:
                retrieved_directives.append(directive)

        DirectiveUtil.traverse(directives, traversal_callback)

        return retrieved_directives
