from ..directive import DirectiveUtil
from ..nginx_config import NginxConfig
from ..signature import Signature, SignatureBuilder


def matcher(config: NginxConfig) -> Signature:
    signature_builder = SignatureBuilder(config.raw).set_name('Alias traversal') \
                                          .set_reference_url('https://www.acunetix.com/vulnerabilities/web/path-traversal-via-misconfigured-nginx-alias/') \
                                          .set_description('Location for aliases not ending with a / could allow an attacker to read file stored outside the target folder.')

    location_directives = DirectiveUtil.get_directives('location', config.directives)

    for location_directive in location_directives:
        blocks = location_directive.block

        for directive in blocks:
            if directive.directive == 'alias' and not location_directive.get_full_directive().endswith('/'):
                signature_builder.add_flagged(location_directive, config.raw)

    return signature_builder.build()
