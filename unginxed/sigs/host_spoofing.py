from ..directive import DirectiveUtil
from ..nginx_config import NginxConfig
from ..signature import Signature, SignatureBuilder


def matcher(config: NginxConfig) -> Signature:
    signature_builder = SignatureBuilder(config.raw).set_name('Host Spoofing') \
                                          .set_reference_url('https://github.com/yandex/gixy/blob/master/docs/en/plugins/hostspoofing.md') \
                                          .set_description('Usage of $http_host instead of $host may lead to unexpected behaviour (such as phishing and SSRF) due to order of precedence')

    proxy_header_directives = DirectiveUtil.get_directives('proxy_set_header', config.directives)
    for directive in proxy_header_directives:
        if 'Host' in directive.args and '$http_host' in directive.args:
            signature_builder.add_flagged(directive, config.raw)

    return signature_builder.build()
