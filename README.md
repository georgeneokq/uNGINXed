# uNGINXed

A tool that generates reports about misconfigurations in specified NGINX configuration files.

The reports may be in JSON format or PDF.

## Adding signatures

Signatures come in the form of python code.

In the sigs folder, create a new python file which contains a function named `matcher`.
The function takes in an NGINXConfig object as a parameter, and should return a `Signature` object as a result.
Use the `SignatureBuilder` class to build your signatures, as it abstracts the complicated logic away from creating the Signature.

### Command line tool

Use the `tools/sigs.py` tool to create a signature python file which contains boilerplate to get you started.

Example usage (from `unginxed` folder):
```
python ./tools/sigs.py create Alias LFI
```

This creates a file named `alias_lfi.py`, with the following boilerplate code:

```python
from ..nginx_config import NginxConfig
from ..signature import Signature, SignatureBuilder


def matcher(config: NginxConfig) -> Signature:
    signature_builder = SignatureBuilder(config.raw).set_name('Alias LFI') \
                                          .set_reference_url('') \
                                          .set_description('')

    # Your logic here.
    # Flag out directives using signature_builder.add_flagged(directive, config)

    return signature_builder.build()
```