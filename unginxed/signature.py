from dataclasses import dataclass
from importlib import import_module
from os import listdir, path
from pathlib import Path
from typing import Callable, Optional, Self, TypedDict

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


def get_signatures(signatures_folder=None) -> list[Callable[[list[Directive]], Signature]]:
    """
    Retrieves a list of signatures.
    Each signature should be a python file in the specified signatures folder,
    containing a function named "matcher". Each matcher function takes in
    a list of Directive objects as a parameter.

    Args:
        signatures_folder: If not provided, defaults to 'sigs' folder.

    Returns:
        list[Callable[[list[Directive]], None]]: _description_
    """
    signatures = []

    if signatures_folder is None:
        signatures_folder = path.join(Path(__file__).parent, 'sigs')

    filenames = list(filter(
        lambda filename: filename.endswith('.py') and not filename.endswith('__'),
        listdir(signatures_folder))
    )

    for filename in filenames:
        try:
            signature = import_module(
                f'.sigs.{filename.rstrip(".py")}',
                package=__package__
            )
            signatures.append(signature.matcher)
        except Exception:
            print(f'Unknown error loading signature from {path.join(signatures_folder, filename)}')

    return signatures
