import re
from os import path
from pathlib import Path
from typing import Optional

import crossplane

from .directive import Directive, DirectiveDict, DirectiveUtil


class NginxConfig:
    """Represents an NGINX config file"""
    def __init__(self, filepath: str):
        """Instantiate an NginxConfig object.

        Args:
            filepath (str): Absolute or relative path to the config file

        Properties:
            filepath: File path to the config
            raw: Contents of the config file, unparsed
            config: Parsed tree of directives
        """

        if not path.exists(filepath):
            raise IOError(f'Invalid file path "{filepath}" provided.')
        
        self.filepath: str = filepath
        self.filename: str = Path(filepath).stem

        with open(filepath) as f:
            self.raw: str = f.read()

        self.directives: list[Directive] = []

        config: list[DirectiveDict] = crossplane.parse(filepath)["config"][0]["parsed"]
        if not config:
            raise RuntimeError('Invalid NGINX config!')

        for directive_dict in config:
            directive = Directive()
            self.directives.append(directive)
            DirectiveUtil.recursive_initialize_directives(
                directive,
                directive_dict
            )

    def __repr__(self) -> str:
        return str(self.raw)


class NginxConfigUtil:
    @staticmethod
    def get_directive_position(config: str,
                               directive_and_args: list[str],
                               line_number: int) -> tuple[int, int]:
        """
        Given a directive along with its line number, get the
        start column index and end column index. The retrieved position
        uses one-based indexing.
        A line number is required as there may be multiple of the same
        directive in a configuration file.

        Args:
            config (str): Raw config file contents
            directive (str): Directive and its arguments
            line_number (int): Line number. If not given or not found
                               on first try, the entire file will be
                               traversed and will return the result of
                               the first match. Uses one-based indexing

        Returns:
            tuple[int, int]: Start and end index of the directive, one-indexed
        """

        # Form a regex string to handle irregular number of spaces / newline.
        # Also account for quotes around each arg.
        pattern = r'\s+'.join(['[\'\"]?{}[\'\"]?'.format(re.escape(arg)) for arg in directive_and_args])

        # Using the specified line, create a substring that starts from that line.
        # The directive being searched for could span multiple lines.
        config_trimmed = '\n'.join(config.splitlines()[line_number-1:])
        match = re.search(pattern, config_trimmed)

        if match:
            [start_index, end_index] = match.span()
            return (start_index + 1, end_index + 1)

        return None
