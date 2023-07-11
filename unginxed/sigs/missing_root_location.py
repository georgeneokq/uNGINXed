from ..directive import DirectiveUtil
from ..nginx_config import NginxConfig
from ..signature import Signature, SignatureBuilder


def matcher(config: NginxConfig) -> Signature:
    signature_builder = SignatureBuilder(config.raw).set_name('Missing Root Location') \
                                          .set_reference_url('https://blog.detectify.com/2020/11/10/common-nginx-misconfigurations/') \
                                          .set_description('This could potentially leak useful information about the server installation to a remote, unauthenticated attacker.') \
                                          .set_severity(2)

    root_directives = DirectiveUtil.get_directives("root", config.directives)
    if not root_directives:
        selector = config.directives[-1]
        signature_builder.add_flagged(selector, config.raw)

    return signature_builder.build()
