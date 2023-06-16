from dataclasses import dataclass, field
from typing import Callable, Self, TypedDict


class DirectiveDict(TypedDict):
    """
    TypedDict for type hinting a dictionary that represents
    a directive, retrieved from crossplane library
    """
    directive: str
    line: int
    args: list[str]
    block: list[dict]


@dataclass
class Directive:
    """
    Data class that represents a directive
    """
    directive: str = None
    line: int = None
    args: list[str] = field(default_factory=list)
    block: list[Self] = field(default_factory=list)

    def get_full_directive(self):
        return ' '.join([self.directive, *self.args])


class DirectiveUtil:
    """
    Utility class for handling Directive objects
    """
    @staticmethod
    def traverse(directives: list[Directive],
                 callback: Callable[[Directive], None]) -> None:
        """
        Given a list of directives, recursively traverse through the
        tree of directives and performs a callback on each directive.

        Args:
            directives (list[Directive]): list of Directive objects
            callback (Callable[[Directive], None]): Operation to perform
        """
        for directive in directives:
            callback(directive)
            DirectiveUtil.traverse(directive.block, callback)

    @staticmethod
    def get_directives_set(directives: list[Directive]) -> set[str]:
        """
        Get a full unique set of directive names

        Args:
            directives (list[Directive]): List of directives to retrieve from

        Returns:
            set[str]
        """
        directive_set = set()
        DirectiveUtil.traverse(directives, lambda directive: directive_set.add(directive.directive))
        return directive_set

    @staticmethod
    def get_directives(directive_name: str,
                       directives: list[Directive]) -> list[Directive]:
        """
        Given a list of Directives objects and a directive name, retrieve all
        Directive objects with the given name.

        Args:
            directive_name (str): Directive name to search for
            directives (list[Directive]): List of directives to search through

        Returns:
            List of directives
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
        """
        Use this method on a top-level Directive object. Each directive object
        will have its properties filled in using the provided corresponding
        dictionary of values.

        Args:
            directive (Directive): Top-level Directive object to initialize with values
            directive_dict (DirectiveDict): Dictionary to copy values from
        """
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
