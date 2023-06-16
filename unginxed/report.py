import re
from base64 import b64encode
from datetime import datetime
from os import path
from pathlib import Path

from xhtml2pdf import pisa

from .directive import DirectiveUtil
from .nginx_config import NginxConfig
from .signature import Signature


def _generate_xhtml(config: NginxConfig, signature_results: list[Signature]):
    styles = """
<style>
    @page {
        size: a4 portrait;

        @frame content_frame {
            left: 45pt; width: 512pt; top: 90pt; height: 632pt;
        }

        @frame footer_frame {
            -pdf-frame-content: footer_content;
            left: 0pt;
            width: 512pt;
            top: 772pt;
            height: 20pt;
        }
    }

    body, pre {
        font-family: Arial;
        font-size: 14px;
    }

    .cover-title {
        font-size: 40px;
        font-weight: 700;
    }

    .cover-sub-title {
        font-size: 28px;
        font-weight: 500;
    }

    .center {
        text-align: center;
    }

    .header {
        text-align: center;
        border-bottom-width: 1px;
        border-bottom-color: black;
        border-bottom-style: solid;
    }

    .curly-brace {
        color: #deaa1d;
    }

    .comment {
        color: #109e48;
    }

    .directive {
        color: blue;
    }

    .flagged {
        color: #e80514;
        text-decoration: underline;
    }

    td {
        text-align: center;
        word-wrap: break-word;
    }

    .table-anchor {
        display: inline-block;
    }

    .line-number {
        text-align: right;
        font-style: italic;
        color: gray;
        margin-right: 15px;
        width: 1%;
    }

    .config-content {
        text-align: left;
        white-space: pre;
    }

    .config-overview-table {
        display: block;
        width: 100%;
    }

    .config-overview-table tbody {
        background-color: blue;
    }
</style>
    """.strip()

    # Preprocess config: Underline flagged directives
    processed_set: set[str] = set()
    config_processed = config.raw
    for signature in signature_results:
        for flagged in signature.flagged:
            flagged_directive = flagged["directive"]

            # escape uri special characters
            flagged_directive = flagged_directive.replace('/', '\/').replace('.', '\.').replace('?', '\?').replace('$', '\$')
            
            # NOTE: Might pose a problem if the directive contains chars with special meaning
            pattern = '({})'.format(r'\s+'.join(flagged_directive.split(' ')))

            # Prevent duplicate processing of same directive
            if pattern not in processed_set:
                processed_set.add(pattern)
                config_processed = re.sub(pattern, r'<a href="{}" class="flagged">\g<1></a>'.format(signature.reference_url), config_processed)

    lines = config_processed.splitlines()

    with open(path.join(Path(__file__).parent, 'static', 'img', 'nginx.png'), 'rb') as f:
        cover_page_logo_url = f'data:image/png;base64,{b64encode(f.read()).decode()}'

    configuration_overview = ''.join([f'<tr><td class="line-number">{index + 1}</td><td class="config-content">{line}</td></tr>\n' for index, line in enumerate(lines)])

    # Color for curly braces
    configuration_overview = re.sub(r'([\{\}])', r'<span class="curly-brace">\g<1></span>', configuration_overview)

    # Color for comments
    # NOTE: Currently assumes # always indicates the start of a comment.
    #        If # is used in href during ereprocessing, the report will break
    configuration_overview = re.sub(r'(#.*$)', r'<span class="comment">\g<1></span>', configuration_overview, 0, re.MULTILINE)

    directives_set = DirectiveUtil.get_directives_set(config.directives)

    directives_list = list(directives_set)

    # Form a regex pattern with the unique list of directives
    directives_pattern = rf'^(\d+\s*)({"|".join(directives_list)})([^a-zA-Z\n])'
    configuration_overview = re.sub(directives_pattern, r'\g<1><span class="directive">\g<2>\g<3></span>', configuration_overview, 0, re.MULTILINE)

    html_to_pdf_content = '''
<body>
    <div id="footer_content" align="right">Page
    <pdf:pagenumber/>
    of
    <pdf:pagecount />
    </div>

    <div class="center">
        <h1 class="cover-title">uNGINXed</h1>
        <img src="{}" alt="NGINX" width="200" height="200" />
        <p class="cover-sub-title">Misconfiguration Report</p>
    </div>

    <pdf:nextpage />

    <div>
        <h1 class="header">Table Of Contents</h1>
        <pdf:toc />
    </div>

    <pdf:nextpage />

    <div>
        <h1 class="header">Signatures</h1>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Reference</th>
                    <th>Lines</th>
                </tr>
            </thead>
            <tbody>
                {}
            </tbody>
        </table>
    </div>

    <pdf:nextpage />

    <div>
        <h1 class="header">Configuration Overview</h1>
        <table class="config-overview-table">
            <tbody>
                {}
            </tbody>
        </table>
    </div>

</body>
    '''.format(
        cover_page_logo_url,
        ''.join(
            [
                '<tr>\n<td>{}</td>\n<td>{}</td>\n<td><a class="table-anchor" href="{}">Read More</a></td>\n<td>{}</td></tr>\n'
                .format(signature.name,
                        signature.description,
                        signature.reference_url,
                        (', '.join([str(flagged["line"]) for flagged in signature.flagged]))
                        ) for signature in signature_results
            ]),                                    # Display signature table
        configuration_overview
    ).strip()

    return ''.join([styles, html_to_pdf_content])


def generate_pdf_report(config: NginxConfig, signature_results: list[Signature], output_folder='reports') -> str:
    """
    Generates a PDF report of misconfigurations.

    Args:
        config (NginxConfig): NginxConfig object
        signature_results (list[Signature]): Signature results
        output_folder (str, optional): Folder to write reports to. Defaults to 'reports'.

    Returns:
        str: Absolute file path of report created
    """
    # Ensure output path exists
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    output_path = path.join(output_folder, f'{config.filename}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.pdf')

    with open(output_path, 'w+b') as f:
        source_html = _generate_xhtml(config, signature_results)
        pisa.CreatePDF(source_html, dest=f)
    
    return path.abspath(output_path)
