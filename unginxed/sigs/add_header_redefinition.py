from ..directive import DirectiveUtil
from ..nginx_config import NginxConfig
from ..signature import Signature, SignatureBuilder

signature_builder: SignatureBuilder = None


def matcher(config: NginxConfig) -> Signature:
    signature_builder = SignatureBuilder(config.raw).set_name('add_header Redefinition') \
                                          .set_reference_url('https://github.com/yandex/gixy/blob/master/docs/en/plugins/addheaderredefinition.md') \
                                          .set_description('Lower level add_header redefinition overwrites higher level add_header definitions, causing high level definitions to be lost.') \
                                          .set_severity(1)
    add_header_directives = DirectiveUtil.get_directives('add_header', config.directives)
    for directive in add_header_directives:
        temp = [d for d in directive.parent.parent.block if d.directive == 'add_header']
        if temp:
            signature_builder.add_flagged(directive, config.raw)

    return signature_builder.build()
