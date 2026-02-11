#!/usr/bin/env python3
"""
Multi-format article publisher.

Converts markdown article to:
1. HTML (for LinkedIn/Medium direct paste)
2. Google Doc (for sharing/review)
3. Markdown source (canonical, version-controlled)
4. Visual one-pager PDF (optional, with --visual flag)

Usage:
    python publish_article.py <article_path> <title> [--visual]

Example:
    python publish_article.py articles/claude-rate-limits/source.md "Understanding Claude API Rate Limits" --visual
"""

import sys
import os
import argparse
from pathlib import Path

# Add lib directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from html_generator import save_html
from format_utils import parse_markdown, build_formatting_requests
from visual_reference_generator import create_visual_reference

# Import GoogleDocsClient from whiteboard project
sys.path.insert(0, r'C:\ai\whiteboard\lib')
from google_docs_client import GoogleDocsClient

import re


# Paths for OAuth credentials
CREDENTIALS_PATH = r'C:\ai\whiteboard\.whiteboard\sync\credentials.json'
TOKEN_PATH = Path(__file__).parent / '.auth' / 'token.json'


def generate_meta_description(markdown_text, title, max_length=200):
    """Generate a concise meta description from article content.

    Args:
        markdown_text: Full markdown article text
        title: Article title
        max_length: Maximum character length (default 200)

    Returns:
        Meta description string ≤ max_length characters
    """
    # Extract subtitle (first H2 after title)
    subtitle_match = re.search(r'^##\s+(.+)$', markdown_text, re.MULTILINE)
    subtitle = subtitle_match.group(1).strip() if subtitle_match else ""

    # Try to find key findings or key data points
    key_findings = []

    # Look for bold statements or key findings bullets
    bold_statements = re.findall(r'\*\*(.+?)\*\*', markdown_text)
    for statement in bold_statements[:3]:  # Take first 3
        # Skip very long statements or ones with links
        if len(statement) < 100 and '[' not in statement:
            key_findings.append(statement)

    # Look for numbered percentages or data points (common in articles)
    data_points = re.findall(r'(\d+(?:-\d+)?%)', markdown_text)

    # Build description intelligently
    # Priority: subtitle + key data point if available
    if subtitle and data_points:
        # Try to create: "Subtitle. Key insight with data."
        main_data = data_points[0] if data_points else ""
        base = f"{subtitle}. "

        # Add most relevant key finding with data if it fits
        for finding in key_findings:
            if main_data in finding:
                candidate = base + finding + "."
                if len(candidate) <= max_length:
                    return candidate
                break

        # Fallback: just subtitle + mention of data
        if len(base) < max_length - 50:
            candidate = base + f"Learn optimization strategies and monitoring routines."
            if len(candidate) <= max_length:
                return candidate

    # Fallback: Use subtitle if it's descriptive enough
    if subtitle and len(subtitle) < max_length - 20:
        return f"{subtitle}"

    # Last resort: Extract first sentence after intro
    sentences = re.split(r'[.!?]+\s+', markdown_text)
    for sentence in sentences[1:10]:  # Skip title, check next few sentences
        clean = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', sentence)  # Remove links
        clean = re.sub(r'[#*`]', '', clean).strip()  # Remove markdown
        if 40 < len(clean) < max_length and clean:
            return clean[:max_length]

    # Ultimate fallback
    return f"{title} - A comprehensive guide."[:max_length]


def publish_to_google_docs(markdown_text, title):
    """Publish markdown content to Google Docs with formatting.

    Args:
        markdown_text: Markdown source text
        title: Document title

    Returns:
        Google Docs URL
    """
    # Initialize and authenticate client
    client = GoogleDocsClient(CREDENTIALS_PATH, str(TOKEN_PATH))
    client.authenticate()

    # Create new document
    doc_id = client.create_doc(title)
    print(f"[OK] Created Google Doc: {doc_id}")

    # Parse markdown into clean text and formatting directives
    clean_text, directives = parse_markdown(markdown_text)

    # Insert text at the beginning (index 1)
    insert_index = 1
    client.docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={
            'requests': [
                {
                    'insertText': {
                        'location': {'index': insert_index},
                        'text': clean_text,
                    }
                }
            ]
        }
    ).execute()
    print(f"[OK] Inserted {len(clean_text)} characters of text")

    # Build and apply formatting requests
    formatting_requests = build_formatting_requests(
        directives,
        insert_index,
        text_length=len(clean_text)
    )

    if formatting_requests:
        client.docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': formatting_requests}
        ).execute()
        print(f"[OK] Applied {len(formatting_requests)} formatting operations")

    # Return shareable URL
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return doc_url


def publish_article(article_path, title, generate_visual=False):
    """Publish article in all formats.

    Args:
        article_path: Path to markdown source file
        title: Article title
        generate_visual: Whether to generate visual one-pager PDF (default: False)

    Returns:
        dict with paths/URLs for all formats
    """
    article_path = Path(article_path)

    if not article_path.exists():
        raise FileNotFoundError(f"Article not found: {article_path}")

    # Read markdown source
    with open(article_path, 'r', encoding='utf-8') as f:
        markdown_text = f.read()

    print(f"\n[*] Publishing: {article_path.name}")
    print(f"    Title: {title}")
    print(f"    Length: {len(markdown_text)} characters\n")

    # Determine output directory (same directory as source)
    output_dir = article_path.parent

    # 1. HTML output
    print("[HTML] Generating HTML...")
    html_path = output_dir / 'article.html'
    save_html(markdown_text, html_path, title)
    print(f"[OK] HTML saved: {html_path}\n")

    # 2. Google Docs output
    print("[GDOC] Publishing to Google Docs...")
    doc_url = publish_to_google_docs(markdown_text, title)
    print(f"[OK] Google Doc published: {doc_url}\n")

    # Save Google Doc URL for reference
    url_file = output_dir / 'gdoc_url.txt'
    with open(url_file, 'w', encoding='utf-8') as f:
        f.write(doc_url)
    print(f"[OK] URL saved: {url_file}\n")

    # 3. Markdown source (already exists, just confirm)
    print(f"[OK] Markdown source: {article_path}\n")

    # 4. Visual Reference (optional)
    visual_path = None
    if generate_visual:
        print("[VISUAL] Generating one-pager reference...")
        visual_path = output_dir / 'visual_reference.pdf'
        create_visual_reference(markdown_text, visual_path, title)
        print(f"[OK] Visual reference saved: {visual_path}\n")

    # Generate meta description
    meta_description = generate_meta_description(markdown_text, title)

    # Summary
    results = {
        'markdown': str(article_path),
        'html': str(html_path),
        'google_doc_url': doc_url,
        'url_file': str(url_file),
        'meta_description': meta_description,
    }

    if visual_path:
        results['visual_reference'] = str(visual_path)

    print("=" * 60)
    print("PUBLICATION COMPLETE")
    print("=" * 60)
    print(f"\nOutputs:")
    print(f"  - Markdown: {results['markdown']}")
    print(f"  - HTML: {results['html']}")
    print(f"  - Google Doc: {results['google_doc_url']}")
    if 'visual_reference' in results:
        print(f"  - Visual Reference: {results['visual_reference']}")
    print(f"\nNext steps:")
    print(f"  1. Review Google Doc formatting")
    print(f"  2. Open HTML in browser to preview")
    print(f"  3. Copy content for LinkedIn article editor")
    if 'visual_reference' in results:
        print(f"  4. Open visual PDF for quick reference/sharing")
    print(f"\n" + "=" * 60)
    print("SEO META DESCRIPTION")
    print("=" * 60)
    print(f"\n{meta_description}")
    print(f"\nCharacter count: {len(meta_description)}/200")
    print(f"\nCopy this for Medium/LinkedIn SEO settings, CMS meta description,")
    print(f"or social sharing. Optimized for AI discoverability and human appeal.")
    print()

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Multi-format article publisher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Generate HTML and Google Doc only
  python publish_article.py articles/claude-rate-limits/source.md "Understanding Claude API Rate Limits"

  # Generate all formats including visual one-pager PDF
  python publish_article.py articles/claude-rate-limits/source.md "Understanding Claude API Rate Limits" --visual
        '''
    )
    parser.add_argument('article_path', help='Path to markdown source file')
    parser.add_argument('title', help='Article title')
    parser.add_argument('--visual', action='store_true',
                       help='Generate visual one-pager PDF reference')

    args = parser.parse_args()

    try:
        publish_article(args.article_path, args.title, generate_visual=args.visual)
    except Exception as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
