from ..directive import Directive, DirectiveUtil
from ..signature_result import SignatureResult


def matcher(directives: list[Directive]) -> SignatureResult:
    signature_result = SignatureResult([], [], 'https://www.google.com', '')

    location_directives = DirectiveUtil.get_directives('location', directives)

    for location_directive in location_directives:
        blocks = location_directive.block

        for directive in blocks:
            if directive.directive == 'alias' and not location_directive.directive.endswith('/'):
                signature_result.lines.append(location_directive.line)
                signature_result.directives.append(
                    f'{location_directive.directive} {" ".join(location_directive.args)}')

    return signature_result
