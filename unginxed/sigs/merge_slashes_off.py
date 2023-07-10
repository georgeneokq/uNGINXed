from ..directive import DirectiveUtil
from ..nginx_config import NginxConfig
from ..signature import Signature, SignatureBuilder


def matcher(config: NginxConfig) -> Signature:
    signature_builder = SignatureBuilder(config.raw).set_name('Merge Slashes Off') \
                                          .set_reference_url('https://blog.detectify.com/2020/11/10/common-nginx-misconfigurations/') \
                                          .set_description('The merge_slashes directive is set to "on" by default. If Nginx is used as a reverse-proxy and the application that’s being proxied is vulnerable to local file inclusion, using extra slashes in the request could leave room for exploits.')

    return_directives = DirectiveUtil.get_directives('merge_slashes', config.directives)
    for return_directive in return_directives:
        if 'off' in return_directive.get_full_args():
            signature_builder.add_flagged(return_directive, config.raw)

    return signature_builder.build()
