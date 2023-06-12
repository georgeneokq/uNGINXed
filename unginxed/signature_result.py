from dataclasses import dataclass

from unginxed.directive import Directive


# In report generation, highlight the line number and also show the directive
@dataclass
class SignatureResult:
    lines: list[int]
    directives: list[str]
    reference: str
    additional_description: str
