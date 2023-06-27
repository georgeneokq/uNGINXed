import argparse as ap
import pyperclip
from pathlib import Path
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from .nginx_config import NginxConfig
from .report import generate_pdf_report
from .signature import get_signatures, Signature


UNGINXED_VERSION = "0.1.1"
UNGINXED_LOGO = """
        _   _  _____ _____ _   ___   __        _ 
       | \ | |/ ____|_   _| \ | \ \ / /       | |
  _   _|  \| | |  __  | | |  \| |\ V / ___  __| |
 | | | | . ` | | |_ | | | | . ` | > < / _ \/ _` |
 | |_| | |\  | |__| |_| |_| |\  |/ . \  __/ (_| |
  \__,_|_| \_|\_____|_____|_| \_/_/ \_\___|\__,_| 

          """

def report_summary_cli(signature_results: list[Signature]):
    for result in signature_results:
        table = Table(title="Signature for {}\n{}".format(result.name, result.description), caption="Reference URL: {}".format(result.reference_url))
        table.add_column("Line Number", justify="right", style="cyan", no_wrap=True)
        table.add_column("Directive and Argument", style="magenta")
        table.add_column("Column Start", justify="right", style="green")
        table.add_column("Column End", justify="right", style="green")
        if len(result.flagged) > 0:
            for misconfig in result.flagged:
                table.add_row(str(misconfig.get('line')), ' '.join(misconfig.get('directive_and_args')), str(misconfig.get('column_start')), str(misconfig.get('column_end')))
                console = Console()
                console.print(table)
                print("\n")

def main():
    argument_parser = ap.ArgumentParser(prog=UNGINXED_LOGO,
                    description='A tool to detect misconfigurations in NGINX configuration files',
                    epilog='Example: poetry run python unginxed /etc/nginx/nginx.conf')
    argument_parser.add_argument('file', type=str, help="Path to NGINX configuration file")
    argument_parser.add_argument('-v', '--version', action="version", version="READY TO BE uNGINXed? This is version {0}".format(UNGINXED_VERSION))
    argument_parser.add_argument('-o', '--pdf-output', default="reports", type=str, help="Optional PDF report output directory")
    argument_parser.add_argument('-s', '--summary', default="summary", type=str, help="Prints summary of report to console")
    args = argument_parser.parse_args()
    filepath = args.file
    pdf_output_path = args.pdf_output

    config = NginxConfig(filepath)
    print(UNGINXED_LOGO)
    signatures = get_signatures()

    results = [signature(config) for signature in signatures]
    if pdf_output_path is not None:
        report_path = generate_pdf_report(config, results, output_folder=pdf_output_path)

    total_flagged = sum(len(result.flagged) for result in results)

    if total_flagged == 0:
        rprint("No misconfigurations found. You are safe FOR NOW!\n\n")
    else:
        rprint("You have been NGINXED! {} directive flagged in your configuration\n\n".format(total_flagged))

    report_summary_cli(results)
    
    if report_path:
        report_path = Path(report_path)
        pyperclip.copy(str(report_path))
        print("Jinxed with bad luck? Check your NGINX report at:")
        # Print the clickable URL
        rprint(report_path)



if __name__ == "__main__":
    main()
