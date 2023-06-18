from ..directive import DirectiveUtil
from ..nginx_config import NginxConfig
from ..signature import Signature, SignatureBuilder
from re import compile


def _uses_regex(arg: str) -> bool:
    return compile(arg).groups != 0


def _uses_vars(arg: str) -> bool:
    return '$' in arg


def matcher(config: NginxConfig) -> Signature:
    signature_builder = SignatureBuilder(config.raw).set_name('SSRF') \
                                          .set_reference_url('https://github.com/yandex/gixy/blob/master/docs/en/plugins/ssrf.md') \
                                          .set_description('Possible SSRF due to attacker controlled parameters to proxy_pass, without restrictions(internal)')

    location_directives = DirectiveUtil.get_directives('location', config.directives)
    for location_directive in location_directives:
        blocks = location_directive.block
        directives = [directive.directive for directive in blocks]
        if 'internal' in directives:
            continue
        # case of proxy pass without internal and location has regex
        proxy_pass = [directive for directive in blocks if directive.directive == 'proxy_pass']
        location_arg = location_directive.get_full_args()
        for pp_arg in proxy_pass[0].args:
            if proxy_pass and _uses_regex(location_arg) and _uses_vars(pp_arg):
                signature_builder.add_flagged(location_directive, config.raw)
            # case of proxy pass with variable without internal
            elif proxy_pass and not _uses_regex(location_arg) and _uses_vars(pp_arg):
                signature_builder.add_flagged(proxy_pass[0], config.raw)


    return signature_builder.build()
