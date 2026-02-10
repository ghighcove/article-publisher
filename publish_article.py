#!/usr/bin/env python3
"""
Multi-format article publisher.

Converts markdown article to:
1. HTML (for LinkedIn/Medium direct paste)
2. Google Doc (for sharing/review)
3. Markdown source (canonical, version-controlled)

Usage:
    python publish_article.py <article_path> <title>

Example:
    python publish_article.py articles/claude-rate-limits/source.md "Understanding Claude API Rate Limits"
"""

import sys
import os
from pathlib import Path

# Add lib directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from html_generator import save_html
from format_utils import parse_markdown, build_formatting_requests

# Import GoogleDocsClient from whiteboard project
sys.path.insert(0, r'C:\ai\whiteboard\lib')
from google_docs_client import GoogleDocsClient


# Paths for OAuth credentials
CREDENTIALS_PATH = r'C:\ai\whiteboard\.whiteboard\sync\credentials.json'
TOKEN_PATH = Path(__file__).parent / '.auth' / 'token.json'


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


def publish_article(article_path, title):
    """Publish article in all formats.

    Args:
        article_path: Path to markdown source file
        title: Article title

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

    # Summary
    results = {
        'markdown': str(article_path),
        'html': str(html_path),
        'google_doc_url': doc_url,
        'url_file': str(url_file),
    }

    print("=" * 60)
    print("PUBLICATION COMPLETE")
    print("=" * 60)
    print(f"\nOutputs:")
    print(f"  - Markdown: {results['markdown']}")
    print(f"  - HTML: {results['html']}")
    print(f"  - Google Doc: {results['google_doc_url']}")
    print(f"\nNext steps:")
    print(f"  1. Review Google Doc formatting")
    print(f"  2. Open HTML in browser to preview")
    print(f"  3. Copy content for LinkedIn article editor")
    print()

    return results


def main():
    if len(sys.argv) < 3:
        print("Usage: python publish_article.py <article_path> <title>")
        print()
        print("Example:")
        print('  python publish_article.py articles/claude-rate-limits/source.md "Understanding Claude API Rate Limits"')
        sys.exit(1)

    article_path = sys.argv[1]
    title = sys.argv[2]

    try:
        publish_article(article_path, title)
    except Exception as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
