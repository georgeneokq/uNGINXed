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
        "-v",
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
        "-vv",
        "--verbose",
        default="verbose",
        action="store_true",
        help="Prints nginx configuration report",
    )
    argument_parser.add_argument(
        "-s",
        "--summary",
        default="summary",
        action="store_true",
        help="Prints summary report",
    )
    if len(argv) == 1:
        argument_parser.print_usage()
        exit(1)
    args = argument_parser.parse_args()
    filepath = args.file
    pdf_output_path = args.pdf_output

    try:
        config = NginxConfig(filepath)
    except (RuntimeError, IsADirectoryError) :
        print('Invalid NGINX config given!')
        return
    print(UNGINXED_LOGO)
    signatures = get_signatures()

    results = [signature(config) for signature in signatures]
    report_path = generate_pdf_report(config, results, output_folder=pdf_output_path) if pdf_output_path is not None else None

    total_flagged = sum(len(result.flagged) for result in results)

    if total_flagged == 0:
        rprint("No misconfigurations found. You are safe FOR NOW!\n\n")
    else:
        rprint(
            f"You have been NGINXED! {total_flagged} directive flagged in your configuration\n\n")

    if args.summary:
        report_summary_cli(results)

    if args.verbose:
        report_verbose_cli(config, results)

    if report_path:
        report_path = Path(report_path)
        rprint(
            f"Jinxed with bad luck? :thumbs_down:\nCheck your full uNGINXed report at: [link=file://{str(report_path)}] {str(report_path)} [/link]")
        # Print the clickable URL


if __name__ == "__main__":
    main()
