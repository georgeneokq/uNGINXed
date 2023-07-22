import argparse as ap
from pathlib import Path
from rich import print as rprint
from sys import argv

from .nginx_config import NginxConfig
from .report import generate_pdf_report, report_summary_cli, report_verbose_cli
from .signature import get_signatures


UNGINXED_VERSION = "0.1.1"
UNGINXED_LOGO = """
        _   _  _____ _____ _   ___   __        _ 
       | \ | |/ ____|_   _| \ | \ \ / /       | |
  _   _|  \| | |  __  | | |  \| |\ V / ___  __| |
 | | | | . ` | | |_ | | | | . ` | > < / _ \/ _` |
 | |_| | |\  | |__| |_| |_| |\  |/ . \  __/ (_| |
  \__,_|_| \_|\_____|_____|_| \_/_/ \_\___|\__,_| 
A static vulnerability scanner for NGINX Configuration
          """


def main():
    argument_parser = ap.ArgumentParser(
        prog=UNGINXED_LOGO,
        description="A tool to detect misconfigurations in NGINX configuration files",
        epilog="Example: poetry run python unginxed /etc/nginx/nginx.conf",
    )
    argument_parser.add_argument(
        "file", type=str, help="Path to NGINX configuration file"
    )
    argument_parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"READY TO BE uNGINXed? This is version {UNGINXED_VERSION}",
    )
    argument_parser.add_argument(
        "-o",
        "--pdf-output",
        type=str,
        help="Optional PDF report output directory",
    )
    argument_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Prints nginx configuration report",
    )
    argument_parser.add_argument(
        "-s",
        "--summary",
        action="store_true",
        help="Prints summary report",
    )

    if len(argv) == 1:
        argument_parser.print_usage()
        exit(1)

    args = argument_parser.parse_args()
    filepath = args.file
    pdf_output_path = args.pdf_output

    # Use _print function for the rest of the program, in place of
    # python's built-in print() and rich's print().
    # To use rich's print, pass in keyword argument rich=True
    if pdf_output_path:
        # If PDF output is provided, enforce that nothing is printed
        # for the rest of the program
        def _print(*args, **kwargs):
            pass
    else:
        def _print(*args, **kwargs):
            if kwargs.get('rich'):
                rprint(*args)
            else:
                print(*args)


    # Attempt to parse the config file, exit the program if failed
    try:
        config = NginxConfig(filepath)
    except (RuntimeError, IsADirectoryError):
        print('Invalid NGINX config given!')
        exit(1)

    # Print ASCII art
    _print(UNGINXED_LOGO)

    # Run signatures on the configuration file
    signatures = get_signatures()
    results = [signature(config) for signature in signatures]

    # If PDF output path is provided, generate the report and retrieve path
    report_path = generate_pdf_report(config, results, output_folder=pdf_output_path) if pdf_output_path is not None else None

    if report_path is None and not args.summary and not args.verbose:
        _print('''
Specify either one of the following flags to get started:
-o/--pdf-output <report_output_folder>: For report generation
-su/--summary: For printing summary to stdout
-v/--verbose: For print verbose analysis to stdout
              '''.strip())

    if args.summary:
        report_summary_cli(results)

    if args.verbose:
        report_verbose_cli(config, results)

    if args.summary or args.verbose:
        total_flagged = sum(len(result.flagged) for result in results)
        if total_flagged == 0:
            _print("No misconfigurations found. You are safe FOR NOW!\n\n", rich=True)
        else:
            _print(
                f"You have been NGINXED! {total_flagged} directive flagged in your configuration\n\n", rich=True)

    if report_path:
        report_path = Path(report_path)

if __name__ == "__main__":
    main()
