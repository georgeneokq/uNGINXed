from ..directive import DirectiveUtil
from ..nginx_config import NginxConfig
from ..signature import Signature, SignatureBuilder


def matcher(config: NginxConfig) -> Signature:
    signature_builder = SignatureBuilder(config.raw).set_name('Dangerous Root Location') \
                                          .set_reference_url('https://blog.detectify.com/2020/11/10/common-nginx-misconfigurations/') \
                                          .set_description('Setting the root folder to / raises risk of private information leak, especially when a path traversal vulnerability is present') \
                                          .set_severity(3)

    BLACKLIST = ['/', '/etc', '/etc/', '/root/', '/root']

    root_directives = DirectiveUtil.get_directives("root", config.directives)
    for directive in root_directives:
        # root should only have one arg
        arg = directive.args[0]
        if arg in BLACKLIST:
            signature_builder.add_flagged(directive, config.raw)

    return signature_builder.build()
