from importlib import import_module
from os import listdir, path
from typing import Callable
import argparse as ap
import json
import dataclasses
from .nginx_config import NginxConfig
from .directive import Directive


def main():
    argument_parser = ap.ArgumentParser()
    argument_parser.add_argument('file', type=str, help="Path to NGINX configuration file")
    args = argument_parser.parse_args()
    filepath = args.file

    config = NginxConfig(filepath)
    directives = config.directives
    signatures = get_signatures()

    results = [signature(directives) for signature in signatures]
    
    json_results = json.dumps([dataclasses.asdict(result) for result in results])
    print(json_results)


def get_signatures(signatures_folder=None) -> list[Callable[[list[Directive]], None]]:
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
        signatures_folder = path.join(__file__, '..', 'sigs')

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
            pass

    return signatures


if __name__ == "__main__":
    main()
