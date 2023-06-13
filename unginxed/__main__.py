from .sigs.alias_lfi import matcher
from .nginx_config import NginxConfig


def main():
    config = NginxConfig("examples/default.conf")
    signature_result = matcher(config.directives)
    print(signature_result)


if __name__ == "__main__":
    main()
