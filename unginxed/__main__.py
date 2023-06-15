import argparse as ap
import dataclasses
import json
from .nginx_config import NginxConfig
from .signature import get_signatures


def main():
    argument_parser = ap.ArgumentParser()
    argument_parser.add_argument('file', type=str, help="Path to NGINX configuration file")
    args = argument_parser.parse_args()
    filepath = args.file

    config = NginxConfig(filepath)
    signatures = get_signatures()

    results = [signature(config) for signature in signatures] 
    json_results = json.dumps([dataclasses.asdict(result) for result in results])

    print(json_results)


if __name__ == "__main__":
    main()
