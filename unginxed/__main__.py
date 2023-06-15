import argparse as ap
import dataclasses
import json
from .nginx_config import NginxConfig
from .signature import get_signatures
from .report import generate_pdf_report


def main():
    argument_parser = ap.ArgumentParser()
    argument_parser.add_argument('file', type=str, help="Path to NGINX configuration file")
    args = argument_parser.parse_args()
    filepath = args.file

    config = NginxConfig(filepath)
    signatures = get_signatures()

    results = [signature(config) for signature in signatures] 

    report_path = generate_pdf_report(config, results)
    print(f'Generated report at {report_path}')


if __name__ == "__main__":
    main()
