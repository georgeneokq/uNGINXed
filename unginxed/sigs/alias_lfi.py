from ..directive import Directive, DirectiveUtil
from ..signature_result import SignatureResult, Flagged
from ..nginx_config import NginxConfig, NginxConfigUtil


def matcher(config: NginxConfig) -> SignatureResult:
    signature_result = SignatureResult([], 'https://google.com', '')

    location_directives = DirectiveUtil.get_directives('location', config.directives)

    for location_directive in location_directives:
        blocks = location_directive.block

        for directive in blocks:
            if directive.directive == 'alias' and not location_directive.directive.endswith('/'):
                directive_and_args = f'{location_directive.directive} {" ".join(location_directive.args)}'.strip()
                line_number = location_directive.line
                directive_position = NginxConfigUtil.get_directive_position(config, directive_and_args, line_number)
                flagged: Flagged = {
                    'line': line_number,
                    'directive': directive_and_args,
                    'column_start': directive_position[0],
                    'column_end': directive_position[1]
                }
                signature_result.flagged.append(flagged)

    return signature_result
