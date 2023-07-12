from ..directive import DirectiveUtil
from ..nginx_config import NginxConfig
from ..signature import Signature, SignatureBuilder

signature_builder: SignatureBuilder = None


def matcher(config: NginxConfig) -> Signature:
    multiline_directives = ['add_header', 'more_set_headers']
    signature_builder = SignatureBuilder(config.raw).set_name('add_header multiline') \
                                          .set_reference_url('https://github.com/yandex/gixy/blob/master/docs/en/plugins/addheadermultiline.md') \
                                          .set_description('Multi-line headers are deprecated (see RFC 7230). Some clients never supports them (e.g. IE/Edge).') \
                                          .set_severity(1)
    add_header_directives = [add_header_directives for directive in multiline_directives for add_header_directives in DirectiveUtil.get_directives(directive, config.directives)]
    for directive in add_header_directives:
        if directive.directive == 'add_header':
            if '\n' in directive.get_full_args():
                signature_builder.add_flagged(directive, config.raw)
        
        if directive.directive == "more_set_headers":
            for arg in directive.args:
                 if arg in ['-s', '-t'] or arg.startswith('-'):
                    #dont run the code below if the arg is a flag
                    pass
                 elif '\n' in arg:
                    signature_builder.add_flagged(directive, config.raw)

    return signature_builder.build()
