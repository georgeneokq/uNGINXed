import re
from base64 import b64encode
from datetime import datetime
from os import path
from pathlib import Path
from rich.console import Console
from rich.table import Table

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
            line_number (int): zero-indexed line number

        Returns:
            str: HTML string to be used in the template. Can be marked as safe
        """
        if len(line.strip()) == 0:
            return ''

        # Red text and link for flagged directives
        line_to_signature_mapping = SignatureUtil.get_line_to_signature_mapping(signature_results)
        line_to_flagged_mapping = SignatureUtil.get_line_to_flagged_mapping(signature_results) 
        flagged = line_to_flagged_mapping.get(line_number)
        signature = line_to_signature_mapping.get(line_number)

        if flagged is not None and signature is not None:
            # Form a regex pattern to inject "flagged" css
            pattern = r'([^\s]*)' + '(' + re.escape(line.strip()) + ')'
            modified_line = re.sub(pattern, r'\g<1><a href="{}" class="{}">\g<2></a>'.format(signature.reference_url, signature.severity.name.lower()), line, count=1)
        else:
            # If first attempt on retrieving flagged directive by line number fails,
            # try to perform a regex search from nearest flagged line number.
            # The current line may be a continuation of the previous line
            # TODO: Check that a directive has been fully output to the report,
            #       for optimization

            # Copy line_to_flagged_mapping and sort it in ascending order
            flagged_lines_sorted = list(line_to_flagged_mapping.keys())
            flagged_lines_sorted.sort(reverse=True)

            # Iterate through the list from end to start, until we get a
            # line number smaller than the current line number
            previously_flagged_line_number = -1

            for i in range(len(flagged_lines_sorted)):
                flagged_line_number = flagged_lines_sorted[i]
                if flagged_line_number < line_number:
                    previously_flagged_line_number = flagged_line_number
                    break

            # If previously_flagged_line_number > -1, get substring from
            # that previously flagged line until the next semicolon
            if previously_flagged_line_number > -1:
                lines = config.raw.splitlines()
                # Match until ; or {
                subconfig = re.match(r'^.+?[\{;]', '\n'.join(lines[previously_flagged_line_number-1:]), re.DOTALL).group()

                # Check for overlap between the current line and the subconfig
                pattern = re.compile(r'([^\s]*)' + '(' + re.escape(line.strip()) + ')')
                match = pattern.search(subconfig)
                if match:
                    # Inject "flagged" CSS
                    signature = line_to_signature_mapping.get(previously_flagged_line_number)
                    modified_line = re.sub(pattern, r'\g<1><a href="{}" class="{}">\g<2></a>'.format(signature.reference_url, signature.severity.name.lower()), line, count=1)
                else:
                    # This line is a start of a directive, not a continuation
                    modified_line = re.sub(r'^(\s*)([a-z_]+)', r'\g<1><span class="directive">\g<2></span>', line, count=1)
            else:
                # This line is a start of a directive, not a continuation
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

def report_summary_cli(signature_results: list[Signature]):
    for result in signature_results:
        table = Table(
            title="Signature for {}\n{}".format(result.name, result.description),
            caption="Reference URL: {}".format(result.reference_url),
            min_width=100,
        )
        table.add_column("Line Number", justify="right", style="cyan", no_wrap=True)
        table.add_column("Directive and Argument", style="magenta")
        table.add_column("Column Start", justify="right", style="green")
        table.add_column("Column End", justify="right", style="green")
        if len(result.flagged) > 0:
            for misconfig in result.flagged:
                table.add_row(
                    str(misconfig.get("line")),
                    " ".join(misconfig.get("directive_and_args")),
                    str(misconfig.get("column_start")),
                    str(misconfig.get("column_end")),
                )
                console = Console()
                console.print(table)
                print("\n")


def report_verbose_cli(config: NginxConfig, signature_results: list[Signature]):

    def process_config_line(line: str, line_number: int) -> str:
        """
        Takes in a line from the configuration file.
        The line could contain curly braces, whitespace, letters and numbers.

        Args:
            line (str): A line of NGINX configuration
            line_number (int): zero-indexed line number

        Returns:
            str: rich formatted string that can be viewed in the terminal
        """
        if len(line.strip()) == 0:
            return ""

        # Red text and link for flagged directives
        line_to_signature_mapping = SignatureUtil.get_line_to_signature_mapping(
            signature_results
        )
        line_to_flagged_mapping = SignatureUtil.get_line_to_flagged_mapping(
            signature_results
        )
        flagged = line_to_flagged_mapping.get(line_number)
        signature = line_to_signature_mapping.get(line_number)

        if flagged is not None and signature is not None:
            # Form a regex pattern to inject "flagged" css
            pattern = r"([^\s]*)" + "(" + re.escape(line.strip()) + ")"
            
            modified_line = re.sub(
                pattern,
                f'[bold underline {signature.severity.name.lower()}][link={signature.reference_url}]\g<1> \g<2>[/link][/bold underline {signature.severity.name.lower()}]',  
                line,
                count=1,
            )
        else:
            # If first attempt on retrieving flagged directive by line number fails,
            # try to perform a regex search from nearest flagged line number.
            # The current line may be a continuation of the previous line
            # TODO: Check that a directive has been fully output to the report,
            #       for optimization

            # Copy line_to_flagged_mapping and sort it in ascending order
            flagged_lines_sorted = list(line_to_flagged_mapping.keys())
            flagged_lines_sorted.sort(reverse=True)

            # Iterate through the list from end to start, until we get a
            # line number smaller than the current line number
            previously_flagged_line_number = -1

            for i in range(len(flagged_lines_sorted)):
                flagged_line_number = flagged_lines_sorted[i]
                if flagged_line_number < line_number:
                    previously_flagged_line_number = flagged_line_number
                    break

            # If previously_flagged_line_number > -1, get substring from
            # that previously flagged line until the next semicolon
            if previously_flagged_line_number > -1:
                lines = config.raw.splitlines()
                # Match until ; or {
                subconfig = re.match(
                    r"^.+?[\{;]",
                    "\n".join(lines[previously_flagged_line_number - 1 :]),
                    re.DOTALL,
                ).group()

                # Check for overlap between the current line and the subconfig
                pattern = re.compile(r"([^\s]*)" + "(" + re.escape(line.strip()) + ")")
                match = pattern.search(subconfig)
                if match:
                    # Inject "flagged" CSS
                    signature = line_to_signature_mapping.get(
                        previously_flagged_line_number
                    )
                    modified_line = re.sub(
                        pattern,
                        f'[bold underline {signature.severity.name.lower()}][link={ signature.reference_url}]\g<1> \g<2>[/link][/bold underline {signature.severity.name.lower()}]', 
                        line,
                        count=1,
                    )
                else:
                    # This line is a start of a directive, not a continuation
                    modified_line = re.sub(
                        r"^(\s*)([a-z_]+)",
                        r'\g<1>[blue]\g<2>[/blue]',
                        line,
                        count=1,
                    )
            else:
                # This line is a start of a directive, not a continuation
                modified_line = re.sub(
                    r"^(\s*)([a-z_]+)",
                    r'\g<1>[blue]\g<2>[/blue]',
                    line,
                    count=1,
                )

        # Use regex to color comments (everything after a hash #)
        modified_line = re.sub(
            r"(#.*)", r'[green]\g<1>[/green]', modified_line
        )

        return modified_line or f"[white]{line}[/white]"
    
    table = Table(title=f"{config.filepath}", caption=f"Filepath: {config.filepath}")
    table.add_column("Line No.", style="cyan", no_wrap=True)
    table.add_column("Configuration File", style="magenta")

    console = Console()
    # read file line by line
    with open(config.filepath, "r") as f:
        lines = f.readlines()
        for line_num, line in enumerate(lines, 1):
            line_out = process_config_line(line, line_num)
            table.add_row(f"[dim] {line_num} [/dim]", f"{line_out}")

    console.print(table)
