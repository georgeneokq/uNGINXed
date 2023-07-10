from ..directive import DirectiveUtil
from ..nginx_config import NginxConfig
from ..signature import Signature, SignatureBuilder


def matcher(config: NginxConfig) -> Signature:
    crlf_directives = ['rewrite', 'return', 'add_header', 'proxy_set_header', 'proxy_pass']
    crlf_indicators = ['$uri', '$document_uri']
    signature_builder = SignatureBuilder(config.raw).set_name('CRLF Injection') \
                                          .set_reference_url('https://www.acunetix.com/vulnerabilities/web/crlf-injection-http-response-splitting-web-server/') \
                                          .set_description('Improper usage of normalized URI variables $uri and $document_uri could allow an attacker to perform cross site scripting.') \
                                          .set_severity(3)

    return_directives = [return_directive for directive in crlf_directives for return_directive in DirectiveUtil.get_directives(directive, config.directives)]

    for return_directive in return_directives:
        if any(crlf_indicator in return_directive.get_full_args() for crlf_indicator in crlf_indicators):
            signature_builder.add_flagged(return_directive, config.raw)

    return signature_builder.build()
