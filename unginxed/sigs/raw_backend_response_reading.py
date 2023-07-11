from ..directive import DirectiveUtil
from ..nginx_config import NginxConfig
from ..signature import Signature, SignatureBuilder


def matcher(config: NginxConfig) -> Signature:
    signature_builder = SignatureBuilder(config.raw).set_name('Raw Backend Response Reading') \
                                          .set_reference_url('https://blog.detectify.com/2020/11/10/common-nginx-misconfigurations') \
                                          .set_description('If Nginx does not understand the request type, usage of proxy_hide_header and proxy_intercept_errors will fail to hide potential sensitive information') \
                                          .set_severity(1)

    hide_headers_directive = DirectiveUtil.get_directives('proxy_hide_header', config.directives)
    for directive in hide_headers_directive:
        sub_directives = [sub_directive.directive for sub_directive in directive.parent.block]
        if 'proxy_intercept_errors' in sub_directives:
            signature_builder.add_flagged(directive, config.raw)

    return signature_builder.build()
