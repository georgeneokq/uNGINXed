from ..directive import DirectiveUtil
from ..nginx_config import NginxConfig
from ..signature import Signature, SignatureBuilder


def matcher(config: NginxConfig) -> Signature:
    signature_builder = SignatureBuilder(config.raw).set_name('Valid Referers') \
                                          .set_reference_url('https://github.com/yandex/gixy/blob/master/docs/en/plugins/validreferers.md') \
                                          .set_description('none is an allowed referer amongst other filtered referers')

    referers_directives = DirectiveUtil.get_directives('valid_referers', config.directives)
    for directive in referers_directives:
        if len(directive.args) > 1 and 'none' in directive.args:
            signature_builder.add_flagged(directive, config.raw)

    return signature_builder.build()
