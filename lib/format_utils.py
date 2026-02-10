"""
Markdown-to-Google-Docs formatting utilities.

Parses Markdown text into clean text + formatting directives, then converts
directives into Google Docs API batchUpdate requests.

Two-pass approach:
  1. parse_markdown(text) -> (clean_text, directives)
  2. build_formatting_requests(directives, insert_index) -> list[dict]

Enhanced with hyperlink support: [text](url)
"""

import re
from collections import namedtuple

# type: heading_2, heading_3, bold, bullet, hr, hidden, link
# meta: optional dict with extra info (e.g. {'url': '...'} for links)
FormatDirective = namedtuple('FormatDirective', ['start', 'end', 'type', 'meta'])

# Google Blue for date headings
GOOGLE_BLUE = {'red': 0.102, 'green': 0.451, 'blue': 0.910}  # #1a73e8


def parse_markdown(text):
    """Parse Markdown text into clean text and formatting directives.

    Returns:
        (clean_text, directives): clean_text has Markdown syntax stripped;
        directives is a list of FormatDirective with character offsets into clean_text.
    """
    lines = text.split('\n')
    clean_lines = []
    directives = []
    offset = 0  # running character offset in the clean text

    for line in lines:
        stripped = line.rstrip()

        # --- Horizontal rule ---
        if re.match(r'^-{3,}\s*$', stripped):
            clean_line = '\u200B'  # zero-width space as placeholder
            line_start = offset
            line_end = offset + len(clean_line)
            directives.append(FormatDirective(line_start, line_end, 'hr', None))
            clean_lines.append(clean_line)
            offset += len(clean_line) + 1  # +1 for newline
            continue

        # <!-- SECTION:... --> markers — keep text, mark as hidden
        section_match = re.match(r'^(<!--\s*/?SECTION:.+?-->)\s*$', stripped)
        if section_match:
            clean_line = section_match.group(1)
            line_start = offset
            line_end = offset + len(clean_line)
            directives.append(FormatDirective(line_start, line_end, 'hidden', None))
            clean_lines.append(clean_line)
            offset += len(clean_line) + 1
            continue

        # ## Heading 2
        h2_match = re.match(r'^##\s+(.+)$', stripped)
        if h2_match and not stripped.startswith('###'):
            clean_line = h2_match.group(1)
            line_start = offset
            line_end = offset + len(clean_line)
            directives.append(FormatDirective(line_start, line_end, 'heading_2', None))
            clean_lines.append(clean_line)
            offset += len(clean_line) + 1
            continue

        # ### Heading 3
        h3_match = re.match(r'^###\s+(.+)$', stripped)
        if h3_match:
            clean_line = h3_match.group(1)
            line_start = offset
            line_end = offset + len(clean_line)
            directives.append(FormatDirective(line_start, line_end, 'heading_3', None))
            clean_lines.append(clean_line)
            offset += len(clean_line) + 1
            continue

        # - Bullet items
        bullet_match = re.match(r'^-\s+(.+)$', stripped)
        if bullet_match:
            raw_content = bullet_match.group(1)
            # Strip bold and links from bullet content
            clean_line = _strip_inline_formatting(raw_content, offset, directives)
            line_start = offset
            line_end = offset + len(clean_line)
            directives.append(FormatDirective(line_start, line_end, 'bullet', None))
            clean_lines.append(clean_line)
            offset += len(clean_line) + 1
            continue

        # Regular line — strip bold and link markers inline
        clean_line = _strip_inline_formatting(stripped, offset, directives)
        clean_lines.append(clean_line)
        offset += len(clean_line) + 1

    clean_text = '\n'.join(clean_lines)
    return clean_text, directives


def _strip_inline_formatting(text, base_offset, directives):
    """Remove **bold** and [link](url) markers from text, recording directives.

    Processes links first (they can contain bold), then bold.
    Returns the clean text with markdown markers removed.
    """
    # First pass: extract links
    result = []
    i = 0
    clean_offset = 0

    while i < len(text):
        # Look for [text](url) pattern
        link_match = re.match(r'\[([^\]]+)\]\(([^)]+)\)', text[i:])
        if link_match:
            link_text = link_match.group(1)
            link_url = link_match.group(2)

            # Process bold within link text
            link_clean_text = _strip_bold_simple(link_text, base_offset + clean_offset, directives)

            link_start = base_offset + clean_offset
            link_end = link_start + len(link_clean_text)
            directives.append(FormatDirective(link_start, link_end, 'link', {'url': link_url}))

            result.append(link_clean_text)
            clean_offset += len(link_clean_text)
            i += link_match.end()
            continue

        # Look for **bold** pattern
        if text[i:i+2] == '**':
            end = text.find('**', i + 2)
            if end != -1:
                bold_content = text[i+2:end]
                bold_start = base_offset + clean_offset
                bold_end = bold_start + len(bold_content)
                directives.append(FormatDirective(bold_start, bold_end, 'bold', None))
                result.append(bold_content)
                clean_offset += len(bold_content)
                i = end + 2
                continue

        result.append(text[i])
        clean_offset += 1
        i += 1

    return ''.join(result)


def _strip_bold_simple(text, base_offset, directives):
    """Remove **bold** markers from text, recording bold directives.

    Simplified version for processing bold within link text.
    Returns the clean text with ** removed.
    """
    result = []
    i = 0
    clean_offset = 0

    while i < len(text):
        if text[i:i+2] == '**':
            end = text.find('**', i + 2)
            if end != -1:
                bold_content = text[i+2:end]
                bold_start = base_offset + clean_offset
                bold_end = bold_start + len(bold_content)
                directives.append(FormatDirective(bold_start, bold_end, 'bold', None))
                result.append(bold_content)
                clean_offset += len(bold_content)
                i = end + 2
                continue
        result.append(text[i])
        clean_offset += 1
        i += 1

    return ''.join(result)


def build_formatting_requests(directives, insert_index, text_length=None):
    """Convert formatting directives to Google Docs API request dicts.

    All ranges are offset by insert_index (the doc index where text was inserted).

    Args:
        directives: List of FormatDirective objects
        insert_index: Document index where text was inserted
        text_length: Total length of inserted text (for default formatting reset)

    Returns requests in correct order: default reset, paragraph styles, text styles, then bullets.
    """
    # CRITICAL: Reset ALL inserted text to normal 11pt black font first
    # This prevents inheriting tiny/hidden font from previous content
    reset_requests = []
    if text_length is not None:
        reset_requests.append({
            'updateTextStyle': {
                'range': {'startIndex': insert_index, 'endIndex': insert_index + text_length},
                'textStyle': {
                    'fontSize': {'magnitude': 11, 'unit': 'PT'},
                    'foregroundColor': {'color': {'rgbColor': {'red': 0, 'green': 0, 'blue': 0}}},
                    'bold': False,  # Explicitly reset bold to prevent inherited formatting
                },
                'fields': 'fontSize,foregroundColor,bold',
            }
        })

    para_requests = []
    text_requests = []
    bullet_requests = []

    for d in directives:
        abs_start = d.start + insert_index
        abs_end = d.end + insert_index

        if d.type == 'heading_2':
            # Paragraph style: HEADING_2 (range includes trailing newline)
            para_requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': abs_start, 'endIndex': abs_end + 1},
                    'paragraphStyle': {'namedStyleType': 'HEADING_2'},
                    'fields': 'namedStyleType',
                }
            })
            # Text style: bold + Google Blue
            text_requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': abs_start, 'endIndex': abs_end},
                    'textStyle': {
                        'bold': True,
                        'foregroundColor': {'color': {'rgbColor': GOOGLE_BLUE}},
                    },
                    'fields': 'bold,foregroundColor',
                }
            })

        elif d.type == 'heading_3':
            para_requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': abs_start, 'endIndex': abs_end + 1},
                    'paragraphStyle': {'namedStyleType': 'HEADING_3'},
                    'fields': 'namedStyleType',
                }
            })
            text_requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': abs_start, 'endIndex': abs_end},
                    'textStyle': {'bold': True},
                    'fields': 'bold',
                }
            })

        elif d.type == 'bold':
            text_requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': abs_start, 'endIndex': abs_end},
                    'textStyle': {'bold': True},
                    'fields': 'bold',
                }
            })

        elif d.type == 'link':
            # Apply hyperlink formatting
            text_requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': abs_start, 'endIndex': abs_end},
                    'textStyle': {'link': {'url': d.meta['url']}},
                    'fields': 'link',
                }
            })

        elif d.type == 'bullet':
            bullet_requests.append({
                'createParagraphBullets': {
                    'range': {'startIndex': abs_start, 'endIndex': abs_end + 1},
                    'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE',
                }
            })

        elif d.type == 'hr':
            # Style as a thin paragraph with bottom border
            para_requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': abs_start, 'endIndex': abs_end + 1},
                    'paragraphStyle': {
                        'borderBottom': {
                            'color': {'color': {'rgbColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8}}},
                            'width': {'magnitude': 1, 'unit': 'PT'},
                            'padding': {'magnitude': 6, 'unit': 'PT'},
                            'dashStyle': 'SOLID',
                        },
                    },
                    'fields': 'borderBottom',
                }
            })
            # Make the placeholder character tiny and invisible
            text_requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': abs_start, 'endIndex': abs_end},
                    'textStyle': {
                        'fontSize': {'magnitude': 1, 'unit': 'PT'},
                        'foregroundColor': {'color': {'rgbColor': {'red': 1, 'green': 1, 'blue': 1}}},
                    },
                    'fields': 'fontSize,foregroundColor',
                }
            })

        elif d.type == 'hidden':
            # Section markers: 1pt white text so they're invisible but searchable
            text_requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': abs_start, 'endIndex': abs_end},
                    'textStyle': {
                        'fontSize': {'magnitude': 1, 'unit': 'PT'},
                        'foregroundColor': {'color': {'rgbColor': {'red': 1, 'green': 1, 'blue': 1}}},
                    },
                    'fields': 'fontSize,foregroundColor',
                }
            })

    # Order: reset ALL text first, then paragraph styles, then text styles, then bullets
    return reset_requests + para_requests + text_requests + bullet_requests
