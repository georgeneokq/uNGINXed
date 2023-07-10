from ..directive import DirectiveUtil
from ..nginx_config import NginxConfig
from ..signature import Signature, SignatureBuilder


def matcher(config: NginxConfig) -> Signature:
    signature_builder = SignatureBuilder(config.raw).set_name('Missing Default Value for map Directive') \
                                          .set_reference_url('https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/nginx') \
                                          .set_description('If map is used for authorisation, not including a default value can lead to unexpected behaviour.')

    return_directives = DirectiveUtil.get_directives('map', config.directives)
    for return_directive in return_directives:
        contains_default = False
        for block_directive in return_directive.block:
            if 'default' in block_directive.get_full_directive():
                contains_default = True
        
        if not contains_default:
            signature_builder.add_flagged(return_directive, config.raw)

    return signature_builder.build()
