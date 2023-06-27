import argparse as ap
import pyperclip
from pathlib import Path

from .nginx_config import NginxConfig
from .report import generate_pdf_report
from .signature import get_signatures

UNGINXED_VERSION = "0.1.1"
UNGINXED_LOGO = """
        _   _  _____ _____ _   ___   __        _ 
       | \ | |/ ____|_   _| \ | \ \ / /       | |
  _   _|  \| | |  __  | | |  \| |\ V / ___  __| |
 | | | | . ` | | |_ | | | | . ` | > < / _ \/ _` |
 | |_| | |\  | |__| |_| |_| |\  |/ . \  __/ (_| |
  \__,_|_| \_|\_____|_____|_| \_/_/ \_\___|\__,_| 

          """

def main():
    argument_parser = ap.ArgumentParser(prog=UNGINXED_LOGO,
                    description='A tool to detect misconfigurations in NGINX configuration files',
                    epilog='Example: poetry run python unginxed /etc/nginx/nginx.conf')
    argument_parser.add_argument('file', type=str, help="Path to NGINX configuration file")
    argument_parser.add_argument('-v', '--version', action="version", version="READY TO BE uNGINXed? This is version {0}".format(UNGINXED_VERSION))
    argument_parser.add_argument('-o', '--pdf-output', default="reports", type=str, help="Optional PDF report output directory")
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
        print("No misconfigurations found. You are safe FOR NOW!\n\n")
    else:
        print("You have been NGINXED! {} directive flagged in your configuration".format(total_flagged))

        for result in results:
            print("Signature for {}".format(result.name))
            if len(result.flagged) > 0:
                for misconfig in result.flagged:
                    print("\tMisconfiguration found in line {} ".format(misconfig.get('line')))
                    print("\tDirective and Argument:\n\t{}".format(misconfig.get('directive_and_args')))
                    print()
    
    if report_path:
        report_path = Path(report_path)
        pyperclip.copy(str(report_path))
        print("Jinxed with bad luck? Check your NGINX report at:")
        # Print the clickable URL
        print(report_path)



if __name__ == "__main__":
    main()
