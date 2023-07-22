"""
Serves as a CLI tool to perform the following tasks:

Create a signature file with boilerplate code
    Example: python ./tools/sigs.py create Alias LFI
"""

import argparse as ap
from pathlib import Path
from os import path, listdir
import re


def handle_create(args):
    name = ' '.join(args.name)
    auto_generated_file_name = '_'.join(name.lower().split(' '))

    template = f"""
from ..nginx_config import NginxConfig
from ..signature import Signature, SignatureBuilder


def matcher(config: NginxConfig) -> Signature:
    signature_builder = SignatureBuilder(config.raw).set_name('{name}') \\
                                          .set_reference_url('') \\
                                          .set_description('') \\
                                          .set_severity()

    # Your logic here.
    # Flag out directives using signature_builder.add_flagged(directive, config)

    return signature_builder.build()

    """.strip() + '\n'

    sigs_folder_path = path.join(Path(__file__).parent.parent, 'sigs')
    filepath = path.join(sigs_folder_path, auto_generated_file_name)

    # Check if there are any file names that start with this auto generated name
    sig_files = list(filter(lambda filename: path.isfile(path.join(sigs_folder_path, filename)), listdir(sigs_folder_path)))
    pattern = f'{auto_generated_file_name}(_\\d+)?.py'
    matching_sig_files = list(filter(lambda filename: re.match(pattern, filename), sig_files))
    num_existing_sig_files = len(matching_sig_files)

    if num_existing_sig_files > 0:
        filepath = path.join(Path(__file__).parent.parent, 'sigs', f'{auto_generated_file_name}_{num_existing_sig_files}.py')
    else:
        filepath = path.join(Path(__file__).parent.parent, 'sigs', f'{auto_generated_file_name}.py')

    with open(filepath, 'w') as f:
        f.write(template)

    print(f'Created signature file "{filepath}"')


if __name__ == '__main__':
    argument_parser = ap.ArgumentParser()

    # Add subparser for the "create" command
    subparsers = argument_parser.add_subparsers(dest='command')
    subparsers.required = True

    parser_create = subparsers.add_parser('create')
    parser_create.add_argument('name', nargs='+', type=str, help="Name of the misconfiguration")

    args = argument_parser.parse_args()

    if args.command == 'create':
        handle_create(args)
