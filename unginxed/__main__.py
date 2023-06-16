import argparse as ap

from .nginx_config import NginxConfig
from .report import generate_pdf_report
from .signature import get_signatures


def main():
    argument_parser = ap.ArgumentParser()
    argument_parser.add_argument('file', type=str, help="Path to NGINX configuration file")
    argument_parser.add_argument('--pdf-output', default="reports", type=str, help="Optional PDF report output directory")
    args = argument_parser.parse_args()
    filepath = args.file
    pdf_output_path = args.pdf_output

    config = NginxConfig(filepath)
    signatures = get_signatures()

    results = [signature(config) for signature in signatures]

    report_path = generate_pdf_report(config, results, output_folder=pdf_output_path)

    print(f'Generated report at {report_path}')


if __name__ == "__main__":
    main()
