from dataclasses import dataclass


# In report generation, highlight the line number and also show the directive
@dataclass
class SignatureResult:
    lines: list[int]
    directives: list[str]
    reference: str
    additional_description: str
