"""
Visual One-Pager Reference Generator
Generates a modern, colorful PDF one-pager from markdown articles.
"""

import re
from pathlib import Path as FilePath
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepTogether, PageBreak, Flowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Circle, Rect, Line, Path, Polygon, String, Group, Wedge
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
import math

from lib.format_utils import parse_markdown


# Modern color scheme
COLORS = {
    'primary_blue': HexColor('#1a73e8'),
    'accent_purple': HexColor('#8e44ad'),
    'success_green': HexColor('#27ae60'),
    'warning_orange': HexColor('#f39c12'),
    'bg_light': HexColor('#f8f9fa'),
    'text_dark': HexColor('#2c3e50'),
    'text_light': HexColor('#7f8c8d'),
}


# ============================================================
# INFOGRAPHIC ELEMENTS: Icons, Charts, Progress Indicators
# ============================================================

def _create_checkmark_icon(size=16, color=None):
    """Create checkmark icon using Path."""
    if color is None:
        color = COLORS['success_green']

    d = Drawing(size, size)
    # Draw circle background
    d.add(Circle(size/2, size/2, size/2, fillColor=color, strokeColor=None))

    # Draw checkmark path
    path = Path(strokeColor=white, fillColor=None, strokeWidth=2)
    path.moveTo(size * 0.25, size * 0.5)
    path.lineTo(size * 0.45, size * 0.7)
    path.lineTo(size * 0.75, size * 0.35)
    d.add(path)

    return d


def _create_star_icon(size=16, color=None):
    """Create 5-pointed star using Polygon."""
    if color is None:
        color = COLORS['warning_orange']

    d = Drawing(size, size)

    # Calculate star points (5-pointed star)
    cx, cy = size/2, size/2
    outer_r = size * 0.45
    inner_r = size * 0.2

    points = []
    for i in range(10):
        angle = (i * 36 - 90) * math.pi / 180  # -90 to start at top
        r = outer_r if i % 2 == 0 else inner_r
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.extend([x, y])

    star = Polygon(points, fillColor=color, strokeColor=None)
    d.add(star)

    return d


def _create_numbered_circle(number, size=20, color=None):
    """Create circle with number inside."""
    if color is None:
        color = COLORS['primary_blue']

    d = Drawing(size, size)
    d.add(Circle(size/2, size/2, size/2, fillColor=color, strokeColor=None))
    d.add(String(size/2, size/2.8, str(number),
                 fontSize=10, fillColor=white, textAnchor='middle'))
    return d


def _create_progress_bar(percentage, label, width=2*inch, height=0.25*inch):
    """Create horizontal progress bar with label."""
    d = Drawing(width, height + 15)

    # Background rect (light gray)
    bg = Rect(0, 10, width, height, fillColor=COLORS['bg_light'],
              strokeColor=COLORS['text_light'], strokeWidth=0.5)
    d.add(bg)

    # Progress rect (colored based on percentage)
    progress_width = width * (min(percentage, 100) / 100)
    color = COLORS['success_green'] if percentage < 80 else COLORS['warning_orange']
    progress = Rect(0, 10, progress_width, height, fillColor=color, strokeColor=None)
    d.add(progress)

    # Label below
    label_text = String(width/2, 0, f"{label}: {percentage}%",
                        fontSize=8, fillColor=COLORS['text_dark'], textAnchor='middle')
    d.add(label_text)

    return d


def _create_gauge(value, max_value, label, size=1.2*inch):
    """Create circular gauge showing value/max_value."""
    d = Drawing(size, size + 15)

    # Calculate percentage
    percentage = (value / max_value * 100) if max_value > 0 else 0

    # Background arc (gray)
    bg_arc = Wedge(size/2, 15 + size/2, size/2 - 5, 0, 180,
                   fillColor=COLORS['bg_light'], strokeColor=COLORS['text_light'], strokeWidth=1)
    d.add(bg_arc)

    # Progress arc (colored)
    angle = 180 * (percentage / 100)
    color = COLORS['success_green'] if percentage < 80 else COLORS['warning_orange']
    progress_arc = Wedge(size/2, 15 + size/2, size/2 - 5, 0, angle,
                         fillColor=color, strokeColor=None)
    d.add(progress_arc)

    # Value text in center
    value_str = String(size/2, 15 + size/2 - 10, f"{int(percentage)}%",
                       fontSize=14, fillColor=COLORS['text_dark'], textAnchor='middle',
                       fontName='Helvetica-Bold')
    d.add(value_str)

    # Label below
    label_text = String(size/2, 0, label,
                        fontSize=8, fillColor=COLORS['text_dark'], textAnchor='middle')
    d.add(label_text)

    return d


def _create_bar_chart(data_dict, title="", width=3.5*inch, height=2*inch):
    """Generate bar chart from data dictionary."""
    if not data_dict or len(data_dict) < 2:
        return None

    d = Drawing(width, height)

    chart = VerticalBarChart()
    chart.x = 40
    chart.y = 30
    chart.width = width - 80
    chart.height = height - 60

    # Set data
    chart.data = [list(data_dict.values())]
    chart.categoryAxis.categoryNames = list(data_dict.keys())

    # Style bars
    chart.bars[0].fillColor = COLORS['primary_blue']
    chart.bars[0].strokeColor = None

    # Style axes
    chart.categoryAxis.labels.fontSize = 8
    chart.categoryAxis.labels.angle = 0
    chart.valueAxis.labels.fontSize = 8

    d.add(chart)

    # Add title if provided
    if title:
        title_text = String(width/2, height - 15, title,
                           fontSize=10, fillColor=COLORS['text_dark'],
                           textAnchor='middle', fontName='Helvetica-Bold')
        d.add(title_text)

    return d


def _create_pie_chart(data_dict, title="", width=2.5*inch, height=2.5*inch):
    """Generate pie chart from proportions."""
    if not data_dict or len(data_dict) < 2:
        return None

    d = Drawing(width, height)

    pie = Pie()
    pie.x = width * 0.15
    pie.y = height * 0.25
    pie.width = width * 0.5
    pie.height = height * 0.5

    # Set data
    pie.data = list(data_dict.values())
    pie.labels = [f"{k}\n{v}%" if isinstance(v, (int, float)) else k
                  for k, v in data_dict.items()]

    # Style slices
    colors = [COLORS['primary_blue'], COLORS['success_green'],
              COLORS['warning_orange'], COLORS['accent_purple']]
    for i in range(len(data_dict)):
        pie.slices[i].fillColor = colors[i % len(colors)]
        pie.slices[i].strokeColor = white
        pie.slices[i].strokeWidth = 1

    pie.slices.fontSize = 8
    pie.slices.fontColor = COLORS['text_dark']

    d.add(pie)

    # Add title if provided
    if title:
        title_text = String(width/2, height - 15, title,
                           fontSize=10, fillColor=COLORS['text_dark'],
                           textAnchor='middle', fontName='Helvetica-Bold')
        d.add(title_text)

    return d


def _create_divider_line(width=7.5*inch):
    """Create decorative divider line."""
    d = Drawing(width, 10)
    line = Line(0, 5, width, 5, strokeColor=COLORS['primary_blue'], strokeWidth=2)
    d.add(line)
    return d


def extract_onepager_content(markdown_text):
    """
    Extract key content from markdown article for one-pager.

    Returns:
        dict with keys: title, subtitle, key_findings, sections, data_points
    """
    lines = markdown_text.split('\n')

    content = {
        'title': '',
        'subtitle': '',
        'key_findings': [],
        'sections': [],
        'data_points': [],
        'charts': [],
        'progress_indicators': []
    }

    # Extract title (first H1)
    for line in lines:
        h1_match = re.match(r'^#\s+(.+)$', line)
        if h1_match and not line.startswith('##'):
            content['title'] = h1_match.group(1).strip()
            break

    # Extract subtitle (first H2)
    for line in lines:
        h2_match = re.match(r'^##\s+(.+)$', line)
        if h2_match and not line.startswith('###'):
            content['subtitle'] = h2_match.group(1).strip()
            break

    # Extract key findings section if it exists
    h2_indices = []
    for i, line in enumerate(lines):
        h2_match = re.match(r'^##\s+(.+)$', line)
        if h2_match and not line.startswith('###'):
            h2_indices.append(i)

    for i, h2_idx in enumerate(h2_indices):
        section_name = lines[h2_idx].lstrip('#').strip().lower()
        if 'key' in section_name and ('finding' in section_name or 'insight' in section_name or 'takeaway' in section_name):
            # Get bullets from this section
            section_end = h2_indices[i + 1] if i + 1 < len(h2_indices) else len(lines)
            section_text = '\n'.join(lines[h2_idx:section_end])

            # Extract bullet points
            bullet_pattern = r'^[\s]*[-*•]\s+(.+)$'
            findings = re.findall(bullet_pattern, section_text, re.MULTILINE)
            content['key_findings'] = findings[:5]  # Max 5 findings
            break

    # If no dedicated key findings section, look for bold "Key Findings:" anywhere in early sections
    if not content['key_findings']:
        # Search in text up to third H2 (to catch findings in intro or early sections)
        search_end = h2_indices[2] if len(h2_indices) > 2 else len(lines)
        search_text = '\n'.join(lines[:search_end])

        # Look for "**Key Findings:**" or "**Key Insights:**" followed by bullets
        key_section_pattern = r'\*\*Key\s+(Findings?|Insights?|Takeaways?):\*\*\s*\n((?:[-*•]\s+.+\n?)+)'
        key_match = re.search(key_section_pattern, search_text, re.IGNORECASE | re.MULTILINE)

        if key_match:
            bullets_text = key_match.group(2)
            # Extract bullet points
            bullet_pattern = r'^[\s]*[-*•]\s+(.+)$'
            findings = re.findall(bullet_pattern, bullets_text, re.MULTILINE)
            content['key_findings'] = findings[:5]  # Max 5 findings
        else:
            # Fallback: Extract bold statements from intro
            if h2_indices:
                intro_end = h2_indices[0]
                intro_text = '\n'.join(lines[:intro_end])
                bold_pattern = r'\*\*(.+?)\*\*'
                bold_statements = re.findall(bold_pattern, intro_text)
                content['key_findings'] = [s for s in bold_statements if len(s) > 20][:5]

    # Extract major sections (H2 headings with bullets)
    sections_extracted = 0
    for i, h2_idx in enumerate(h2_indices[1:], start=1):  # Skip first (subtitle)
        if sections_extracted >= 5:  # Max 5 sections
            break

        section_name = lines[h2_idx].lstrip('#').strip()

        # Skip key findings section (already extracted)
        if 'key' in section_name.lower() and ('finding' in section_name.lower() or 'insight' in section_name.lower()):
            continue

        # Get section content
        section_end = h2_indices[i + 1] if i + 1 < len(h2_indices) else len(lines)
        section_text = '\n'.join(lines[h2_idx:section_end])

        # Extract bullets (limit to 3 per section)
        bullet_pattern = r'^[\s]*[-*•]\s+(.+)$'
        bullets = re.findall(bullet_pattern, section_text, re.MULTILINE)[:3]

        if bullets:
            content['sections'].append({
                'heading': section_name,
                'bullets': bullets
            })
            sections_extracted += 1

    # Extract data points (numbers, percentages, metrics)
    data_pattern = r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(%|tokens?|requests?|hours?|days?|minutes?|seconds?|USD|\$|GB|MB|KB)'
    data_matches = re.findall(data_pattern, markdown_text, re.IGNORECASE)

    # Deduplicate and format
    seen = set()
    for number, unit in data_matches[:6]:  # Max 6 data points
        key = f"{number}{unit}"
        if key not in seen:
            seen.add(key)
            content['data_points'].append({
                'value': number,
                'unit': unit.lower()
            })

    # Detect chart opportunities
    content['charts'] = _detect_chart_data(markdown_text)

    # Detect progress indicators
    content['progress_indicators'] = _detect_progress_metrics(markdown_text)

    return content


# ============================================================
# AUTO-DETECTION: Smart visualization selection
# ============================================================

def _detect_chart_data(markdown_text):
    """
    Find numeric comparisons suitable for charts.
    Returns list of detected chart opportunities with type and data.
    """
    charts = []

    # Pattern 1: Table comparisons (e.g., "Max 5x vs Max 20x")
    # Look for markdown tables with numeric data
    table_pattern = r'\|[^|]+\|[^|]+\|(?:[^|]+\|)*\n\|[-:\s|]+\|\n((?:\|[^|]+\|[^|]+\|(?:[^|]+\|)*\n)+)'
    table_matches = re.finditer(table_pattern, markdown_text, re.MULTILINE)

    for match in table_matches:
        table_content = match.group(0)
        # Extract rows with numbers
        rows = table_content.split('\n')[2:]  # Skip header and separator
        data = {}
        for row in rows:
            if not row.strip():
                continue
            cells = [c.strip() for c in row.split('|')[1:-1]]
            if len(cells) >= 2:
                # Look for label and number
                label = cells[0]
                for cell in cells[1:]:
                    # Extract number
                    num_match = re.search(r'(\d+(?:,\d{3})*(?:\.\d+)?)', cell)
                    if num_match:
                        try:
                            value = float(num_match.group(1).replace(',', ''))
                            data[label[:20]] = value  # Limit label length
                            break
                        except:
                            pass

        if len(data) >= 2:
            charts.append({'type': 'bar', 'data': data, 'title': 'Comparison'})

    # Pattern 2: Percentage distributions (e.g., "45% A, 35% B, 20% C")
    percent_pattern = r'(\d+)%\s+([a-zA-Z][\w\s]{2,30})'
    percent_matches = re.findall(percent_pattern, markdown_text)

    if len(percent_matches) >= 2:
        # Group consecutive percentage mentions
        data = {}
        total = 0
        for pct, label in percent_matches[:5]:  # Max 5 slices
            pct_val = int(pct)
            total += pct_val
            data[label.strip()[:20]] = pct_val

        # If percentages sum to ~100, it's a distribution
        if 85 <= total <= 115 and len(data) >= 2:
            charts.append({'type': 'pie', 'data': data, 'title': 'Distribution'})

    # Pattern 3: Numbered comparisons in text (e.g., "Tier 1: 225 messages, Tier 2: 900 messages")
    comparison_pattern = r'([A-Z][\w\s]{2,30}):\s*(\d+(?:,\d{3})*)\s*(messages?|tokens?|requests?|users?|items?)?'
    comp_matches = re.findall(comparison_pattern, markdown_text)

    if len(comp_matches) >= 2:
        data = {}
        for label, number, unit in comp_matches[:5]:  # Max 5 items
            try:
                value = float(number.replace(',', ''))
                data[label.strip()[:20]] = value
            except:
                pass

        if len(data) >= 2 and not any(c['type'] == 'bar' for c in charts):  # Avoid duplicates
            charts.append({'type': 'bar', 'data': data, 'title': 'Metrics'})

    return charts


def _detect_progress_metrics(markdown_text):
    """
    Detect single-value metrics suitable for progress bars/gauges.
    Returns list of progress indicators.
    """
    indicators = []

    # Pattern: "X of Y" (e.g., "187 of 225") - More specific, cleaner labels
    ratio_pattern = r'(\d+(?:,\d{3})*)\s+of\s+(\d+(?:,\d{3})*)\s+(messages?|tokens?|requests?|sessions?|users?)'
    ratio_matches = re.findall(ratio_pattern, markdown_text, re.IGNORECASE)

    for used, total, label in ratio_matches[:3]:  # Max 3 gauges
        try:
            used_val = float(used.replace(',', ''))
            total_val = float(total.replace(',', ''))
            if total_val > 0 and used_val <= total_val:
                indicators.append({
                    'type': 'gauge',
                    'value': used_val,
                    'max_value': total_val,
                    'label': label.strip().capitalize()
                })
        except:
            pass

    # Pattern: "X%" followed by context (more selective)
    # Only match if percentage is followed by meaningful context
    progress_pattern = r'(\d+)[-–](\d+)%\s+(more\s+\w+|increase|decrease|improvement|reduction|of\s+\w+)'
    matches = re.findall(progress_pattern, markdown_text, re.IGNORECASE)

    for min_pct, max_pct, context in matches[:2]:  # Max 2 progress bars
        try:
            avg_pct = (int(min_pct) + int(max_pct)) // 2
            if 0 <= avg_pct <= 100:
                # Clean up context label
                context_clean = context.replace('of ', '').strip()[:25]
                indicators.append({
                    'type': 'progress_bar',
                    'percentage': avg_pct,
                    'label': context_clean.capitalize()
                })
        except:
            pass

    return indicators


def _classify_section_icon(heading):
    """
    Determine icon for section heading based on keywords.
    Returns icon type: 'star', 'checkmark', 'numbered', or None
    """
    heading_lower = heading.lower()

    # Important/Featured sections get star
    if any(word in heading_lower for word in ['important', 'key', 'critical', 'essential', 'featured']):
        return 'star'

    # Success/Completion sections get checkmark
    if any(word in heading_lower for word in ['success', 'completed', 'achieved', 'done', 'tips']):
        return 'checkmark'

    # Step-by-step or numbered sections
    if any(word in heading_lower for word in ['step', 'phase', 'stage', 'guide']):
        return 'numbered'

    return None


def _create_styles():
    """Create custom paragraph styles for the PDF."""
    styles = getSampleStyleSheet()

    # Title style
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=white,
        alignment=TA_CENTER,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    ))

    # Subtitle style
    styles.add(ParagraphStyle(
        name='CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=white,
        alignment=TA_CENTER,
        spaceAfter=12,
        fontName='Helvetica'
    ))

    # Section heading style
    styles.add(ParagraphStyle(
        name='SectionHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=COLORS['primary_blue'],
        spaceAfter=6,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    ))

    # Body text style
    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=COLORS['text_dark'],
        spaceAfter=4,
        leading=12,
        fontName='Helvetica'
    ))

    # Key insights style
    styles.add(ParagraphStyle(
        name='KeyInsight',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=COLORS['text_dark'],
        spaceAfter=4,
        leftIndent=12,
        bulletIndent=0,
        leading=14,
        fontName='Helvetica'
    ))

    # Data callout style
    styles.add(ParagraphStyle(
        name='DataValue',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=white,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='DataLabel',
        parent=styles['BodyText'],
        fontSize=9,
        textColor=white,
        alignment=TA_CENTER,
        fontName='Helvetica'
    ))

    # Footer style
    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['BodyText'],
        fontSize=8,
        textColor=COLORS['text_light'],
        alignment=TA_CENTER,
        fontName='Helvetica'
    ))

    return styles


def _create_header_banner(title, subtitle, styles):
    """Create colored gradient header with title and subtitle."""
    # Create table for colored background
    header_content = []

    if title:
        header_content.append(Paragraph(title, styles['CustomTitle']))
    if subtitle:
        header_content.append(Paragraph(subtitle, styles['CustomSubtitle']))

    # Wrap in table for background color
    header_table = Table([[c] for c in header_content], colWidths=[7.5 * inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['primary_blue']),
        ('ROUNDEDCORNERS', [5, 5, 5, 5]),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
    ]))

    return header_table


def _create_key_insights_box(findings, styles):
    """Create light blue box with key findings bullets with checkmark icons."""
    if not findings:
        return None

    # Create table rows with icons and text
    rows = []

    # Header row
    header = Paragraph("<b>Key Insights</b>", styles['SectionHeading'])
    rows.append([header])

    # Finding rows with checkmark icons
    for finding in findings:
        # Clean up finding text
        clean_finding = finding.replace('**', '').strip()

        # Create icon and text as a row
        icon = _create_checkmark_icon(size=14, color=COLORS['success_green'])
        text = Paragraph(clean_finding, styles['KeyInsight'])

        # Create inner table for icon + text alignment
        finding_row = Table([[icon, text]], colWidths=[20, 7.1 * inch])
        finding_row.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))

        rows.append([finding_row])

    # Wrap in table for background
    insights_table = Table(rows, colWidths=[7.5 * inch])
    insights_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['bg_light']),
        ('ROUNDEDCORNERS', [5, 5, 5, 5]),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
    ]))

    return insights_table


def _create_section(heading, bullets, styles):
    """Create section with heading (with optional icon) and bullet list."""
    content = []

    # Determine if section should have an icon
    icon_type = _classify_section_icon(heading)

    if icon_type:
        # Create heading with icon
        if icon_type == 'star':
            icon = _create_star_icon(size=14, color=COLORS['warning_orange'])
        elif icon_type == 'checkmark':
            icon = _create_checkmark_icon(size=14, color=COLORS['success_green'])
        else:  # numbered - use first number
            icon = _create_numbered_circle(1, size=16, color=COLORS['primary_blue'])

        heading_para = Paragraph(heading, styles['SectionHeading'])

        # Create table for icon + heading
        heading_table = Table([[icon, heading_para]], colWidths=[20, 7.1 * inch])
        heading_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        content.append(heading_table)
    else:
        # Plain heading without icon
        content.append(Paragraph(heading, styles['SectionHeading']))

    # Add bullets
    for bullet in bullets:
        # Clean up bullet text
        clean_bullet = bullet.replace('**', '').strip()
        # Truncate if too long
        if len(clean_bullet) > 150:
            clean_bullet = clean_bullet[:147] + '...'
        content.append(Paragraph(f"• {clean_bullet}", styles['CustomBody']))

    return KeepTogether(content)


def _create_data_callouts(data_points, styles):
    """Create side-by-side colored metric boxes."""
    if not data_points:
        return None

    # Limit to 4 callouts for space
    data_points = data_points[:4]

    colors = [COLORS['success_green'], COLORS['warning_orange'],
              COLORS['accent_purple'], COLORS['primary_blue']]

    # Create callout boxes
    callouts = []
    for i, data in enumerate(data_points):
        value_text = f"{data['value']}{data['unit']}"
        value_para = Paragraph(value_text, styles['DataValue'])

        # Create box
        box = Table([[value_para]], colWidths=[1.7 * inch])
        box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors[i % len(colors)]),
            ('ROUNDEDCORNERS', [5, 5, 5, 5]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        callouts.append(box)

    # Arrange in grid (2x2 or 1x4)
    if len(callouts) <= 2:
        # Single row
        callout_table = Table([callouts], colWidths=[1.8 * inch] * len(callouts))
    else:
        # Two rows
        row1 = callouts[:2]
        row2 = callouts[2:4] if len(callouts) > 2 else []
        if row2:
            callout_table = Table([row1, row2], colWidths=[1.8 * inch] * 2)
        else:
            callout_table = Table([row1], colWidths=[1.8 * inch] * 2)

    callout_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))

    return callout_table


def _create_attribution_footer(styles):
    """Create footer with Claude attribution and LinkedIn link."""
    footer_text = (
        'Generated by Claude Sonnet 4.5 | '
        'Connect with Glenn Highcove on '
        '<link href="https://www.linkedin.com/in/glennhighcove/" color="blue">LinkedIn</link>'
    )
    return Paragraph(footer_text, styles['Footer'])


def create_visual_reference(markdown_text, output_path, title):
    """
    Generate visual one-pager PDF from markdown article.

    Args:
        markdown_text: Source markdown content
        output_path: Path to save PDF file
        title: Article title (used in metadata)
    """
    # Extract content
    content = extract_onepager_content(markdown_text)

    # Create PDF
    output_path = FilePath(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create document with letter size and margins
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        title=title,
        author="Claude Sonnet 4.5 & Glenn Highcove"
    )

    # Get styles
    styles = _create_styles()

    # Build content flowables
    story = []

    # 1. Header banner
    header = _create_header_banner(content['title'], content['subtitle'], styles)
    story.append(header)
    story.append(Spacer(1, 0.12 * inch))

    # 2. Key insights box (with checkmark icons)
    if content['key_findings']:
        insights = _create_key_insights_box(content['key_findings'], styles)
        if insights:
            story.append(insights)
            story.append(Spacer(1, 0.12 * inch))

    # 3. Charts (if detected)
    if content['charts']:
        # Add decorative divider before charts
        divider = _create_divider_line(width=7.5 * inch)
        story.append(divider)
        story.append(Spacer(1, 0.08 * inch))

        # Add first chart only (to save space)
        chart_info = content['charts'][0]
        if chart_info['type'] == 'bar':
            chart = _create_bar_chart(chart_info['data'], title=chart_info.get('title', ''))
        elif chart_info['type'] == 'pie':
            chart = _create_pie_chart(chart_info['data'], title=chart_info.get('title', ''))
        else:
            chart = None

        if chart:
            story.append(chart)
            story.append(Spacer(1, 0.1 * inch))

    # 4. Progress indicators (if detected)
    if content['progress_indicators']:
        # Show up to 3 progress indicators
        progress_items = []
        for indicator in content['progress_indicators'][:3]:
            if indicator['type'] == 'progress_bar':
                prog = _create_progress_bar(indicator['percentage'], indicator['label'])
                progress_items.append(prog)
            elif indicator['type'] == 'gauge':
                gauge = _create_gauge(indicator['value'], indicator['max_value'], indicator['label'])
                progress_items.append(gauge)

        if progress_items:
            # Arrange progress items in a row (max 3)
            if len(progress_items) == 1:
                story.append(progress_items[0])
            else:
                # Create table for side-by-side layout
                num_items = min(len(progress_items), 3)
                col_width = 7.5 * inch / num_items
                prog_table = Table([progress_items[:num_items]], colWidths=[col_width] * num_items)
                prog_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(prog_table)
            story.append(Spacer(1, 0.1 * inch))

    # 5. Data callouts (if available and no progress indicators shown)
    if content['data_points'] and not content['progress_indicators']:
        callouts = _create_data_callouts(content['data_points'], styles)
        if callouts:
            story.append(callouts)
            story.append(Spacer(1, 0.1 * inch))

    # 6. Main sections (with icons)
    for section in content['sections'][:5]:  # Max 5 sections
        section_elem = _create_section(section['heading'], section['bullets'], styles)
        story.append(section_elem)
        story.append(Spacer(1, 0.08 * inch))

    # 7. Attribution footer
    story.append(Spacer(1, 0.1 * inch))
    footer = _create_attribution_footer(styles)
    story.append(footer)

    # Build PDF
    doc.build(story)

    return output_path
