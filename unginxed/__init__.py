from .nginx_config import NginxConfig
from .signature import get_signatures, Signature


def scan(filepath) -> list[Signature]:
    config = NginxConfig(filepath)
    signatures = get_signatures()
    results = [signature(config) for signature in signatures]
    return results
