from ..directive import DirectiveUtil
from ..nginx_config import NginxConfig
from ..signature import Signature, SignatureBuilder


def matcher(config: NginxConfig) -> Signature:
    crlf_indicators = ['$uri', '$document_uri']
    signature_builder = SignatureBuilder(config.raw).set_name('CRLF Injection') \
                                          .set_reference_url('https://www.acunetix.com/vulnerabilities/web/crlf-injection-http-response-splitting-web-server/') \
                                          .set_description('Improper usage of normalized URI variables $uri and $document_uri could allow an attacker to perform cross site scripting.')

    return_directives = DirectiveUtil.get_directives('return', config.directives)

    for return_directive in return_directives:
        if any(crlf_indicator in return_directive.get_full_args() for crlf_indicator in crlf_indicators):
            signature_builder.add_flagged(return_directive, config.raw)

    return signature_builder.build()
