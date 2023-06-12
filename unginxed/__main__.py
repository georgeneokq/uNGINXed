from .sigs.alias_lfi import matcher
from .config import Config

def main():
    config = Config("examples/default.conf")
    signature_result = matcher(config.parsed)
    print(signature_result)


if __name__ == "__main__":
    main()
