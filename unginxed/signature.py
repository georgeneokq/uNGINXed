from dataclasses import dataclass
from typing import Optional, Self, TypedDict

from .directive import Directive
from .nginx_config import NginxConfigUtil


class Flagged(TypedDict):
    line: int
    column_start: int
    column_end: int
    directive: str


@dataclass
class Signature:
    name: str
    flagged: list[Flagged]
    reference_url: str
    description: str


class SignatureBuilder:
    """
    Builder class that simplifies creation of a Signature object.
    """
    def __init__(self, config=None, name='', flagged=[], reference_url='', description=''):
        self.config = config
        self.signature = Signature(name, flagged, reference_url, description)

    def build(self) -> Signature:
        """
        Returns:
            Signature
        """
        return self.signature

    def set_name(self, name: str) -> Self:
        """
        Args:
            name (str): Name of signature

        Returns:
            SignatureBuilder: Current builder instance
        """
        self.signature.name = name
        return self

    def set_flagged(self, flagged_list: list[Flagged]):
        """
        Args:
            flagged_list (list[Flagged]): List of Flagged configuration

        Returns:
            SignatureBuilder: Current builder instance
        """
        self.signature.flagged = flagged_list
        return self

    def add_flagged(self, directive: Directive, config: Optional[str] = None):
        """
        Args:
            directive (Directive): Directive object to flag out
            config (str): Raw config file contents. Used to pinpoint location
                          of the directive.

        Returns:
            SignatureBuilder: Current builder instance
        """
        _config = config if config else self.config

        directive_and_args = f'{directive.directive} {" ".join(directive.args)}'.rstrip()

        # If no config is passed, unable to pinpoint location of the directive
        if _config:
            [column_start, column_end] = NginxConfigUtil.get_directive_position(_config, directive_and_args, directive.line)

        self.signature.flagged.append({
            "directive": directive_and_args,
            "line": directive.line,
            "column_start": column_start,
            "column_end": column_end
        })
        return self

    def set_reference_url(self, reference_url: str):
        self.signature.reference_url = reference_url
        return self

    def set_description(self, description: str):
        self.signature.description = description
        return self
