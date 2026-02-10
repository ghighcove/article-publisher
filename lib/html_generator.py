"""
Markdown to HTML converter with LinkedIn-optimized styling.

Generates standalone HTML files with embedded CSS for professional article presentation.
"""

import markdown2


def generate_html(markdown_text, title="Article"):
    """Convert markdown text to styled HTML.

    Args:
        markdown_text: Markdown source text
        title: HTML page title

    Returns:
        Complete HTML document with embedded styles
    """
    # Convert markdown to HTML with extras
    html_content = markdown2.markdown(
        markdown_text,
        extras=[
            'fenced-code-blocks',
            'tables',
            'header-ids',
            'smarty-pants',
            'break-on-newline'
        ]
    )

    # LinkedIn-optimized CSS
    css = """
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #000000e6;
            max-width: 740px;
            margin: 40px auto;
            padding: 20px;
            background: #ffffff;
        }

        h1 {
            font-size: 36px;
            font-weight: 600;
            line-height: 1.2;
            margin-bottom: 8px;
            color: #000000;
        }

        h2 {
            font-size: 28px;
            font-weight: 600;
            line-height: 1.3;
            margin-top: 32px;
            margin-bottom: 12px;
            color: #000000;
        }

        h3 {
            font-size: 22px;
            font-weight: 600;
            line-height: 1.4;
            margin-top: 24px;
            margin-bottom: 10px;
            color: #000000;
        }

        p {
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 16px;
            color: #000000e6;
        }

        em {
            font-style: italic;
            color: #00000099;
            font-size: 14px;
        }

        strong {
            font-weight: 600;
            color: #000000;
        }

        a {
            color: #0a66c2;
            text-decoration: none;
            transition: color 0.15s ease;
        }

        a:hover {
            color: #004182;
            text-decoration: underline;
        }

        ul, ol {
            margin-bottom: 16px;
            padding-left: 24px;
        }

        li {
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 8px;
            color: #000000e6;
        }

        code {
            font-family: 'Courier New', Courier, monospace;
            background: #f3f2ef;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 14px;
        }

        pre {
            background: #f3f2ef;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            margin-bottom: 16px;
        }

        pre code {
            background: none;
            padding: 0;
        }

        blockquote {
            border-left: 3px solid #0a66c2;
            padding-left: 16px;
            margin-left: 0;
            margin-bottom: 16px;
            color: #00000099;
            font-style: italic;
        }

        hr {
            border: none;
            border-top: 1px solid #e0e0e0;
            margin: 32px 0;
        }

        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 16px;
        }

        th, td {
            border: 1px solid #e0e0e0;
            padding: 12px;
            text-align: left;
        }

        th {
            background: #f3f2ef;
            font-weight: 600;
        }

        .subtitle {
            font-size: 20px;
            line-height: 1.4;
            color: #00000099;
            margin-bottom: 24px;
            font-weight: 400;
        }

        .attribution {
            font-size: 14px;
            line-height: 1.5;
            color: #00000099;
            font-style: italic;
            margin-bottom: 32px;
            padding-bottom: 24px;
            border-bottom: 1px solid #e0e0e0;
        }
    """

    # Complete HTML template
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{css}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

    return html_template


def save_html(markdown_text, output_path, title="Article"):
    """Convert markdown to HTML and save to file.

    Args:
        markdown_text: Markdown source text
        output_path: Path to save HTML file
        title: HTML page title

    Returns:
        Path to saved HTML file
    """
    html = generate_html(markdown_text, title)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return output_path
