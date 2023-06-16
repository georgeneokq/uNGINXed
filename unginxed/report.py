import re
from base64 import b64encode
from datetime import datetime
from os import path
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from xhtml2pdf import pisa

from .nginx_config import NginxConfig
from .signature import Signature, SignatureUtil


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

    # Prepare to load HTML from jinja template
    jinja_env = Environment(
        loader=FileSystemLoader(path.join(Path(__file__).parent, 'templates')),
        autoescape=select_autoescape()
    )

    template = jinja_env.get_template('report.html')

    # Pass in pdf styles from python as these xhtml-specific styles
    # cause linting problems in the html template
    pdf_styles = """
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
    """.strip()

    # Load image base64 data url
    with open(path.join(Path(__file__).parent, 'static', 'img', 'nginx.png'), 'rb') as f:
        cover_page_logo_url = f'data:image/png;base64,{b64encode(f.read()).decode()}'

    def process_config_line(line: str, line_number: int) -> str:
        """
        Takes in a line from the configuration file.
        The line could contain curly braces, whitespace, letters and numbers.

        Args:
            line (str): A line of NGINX configuration

        Returns:
            str: HTML string to be used in the template. Can be marked as safe
        """
        # Red text and link for flagged directives
        line_to_signature_mapping = SignatureUtil.get_line_to_signature_mapping(signature_results)
        line_to_flagged_mapping = SignatureUtil.get_line_to_flagged_mapping(signature_results) 
        flagged = line_to_flagged_mapping.get(line_number)
        signature = line_to_signature_mapping.get(line_number)

        if flagged is not None and signature is not None:
            # Form a regex pattern to inject "flagged" css
            pattern = '(' + r'\s+'.join([re.escape(directive_token) for directive_token in flagged["directive"].split(' ')]) + ')'
            modified_line = re.sub(pattern, r'<a href="{}" class="flagged">\g<1></a>'.format(signature.reference_url), line, count=1)
        else:
            modified_line = re.sub(r'^(\s*)([a-z_]+)', r'\g<1><span class="directive">\g<2></span>', line, count=1)

        # Use regex to color comments (everything after a hash #)
        modified_line = re.sub(r'(#.*)', r'<span class="comment">\g<1></span>', modified_line)

        return modified_line or line

    source_html = template.render(
        signatures=signature_results,
        config=config,
        pdf_styles=pdf_styles,
        logo_url=cover_page_logo_url,
        process_config_line=process_config_line
    )

    # Ensure output path exists
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    output_path = path.join(output_folder, f'{config.filename}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.pdf')

    with open(output_path, 'w+b') as f:
        pisa.CreatePDF(source_html, dest=f)

    return path.abspath(output_path)
