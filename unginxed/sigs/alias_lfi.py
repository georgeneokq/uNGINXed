from ..directive import Directive
from ..signature_result import SignatureResult
import numpy as np

def matcher(directives: list[Directive]) -> SignatureResult:
    signature_result = SignatureResult([], [], 'http://localhost', '')

    location_directives: list[Directive] = list(np.array(list(filter(lambda item: len(item) != 0, list(
        map(lambda directive: Directive.from_dict(directive).get_directives('location'), directives)
    )))).flatten())
 
    for location_directive in location_directives:
        blocks = location_directive.block
        
        for directive_dict in blocks:
            directive = Directive.from_dict(directive_dict)
            if directive.directive == 'alias' and not location_directive.directive.endswith('/'):
                signature_result.lines.append(location_directive.line)
                signature_result.directives.append(f'{location_directive.directive} {" ".join(location_directive.args)}')

    return signature_result