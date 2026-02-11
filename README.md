# Article Publisher

Multi-format article publishing system for LinkedIn, Medium, and Google Docs. Converts markdown articles into multiple formats for maximum flexibility.

## Overview

This project provides a streamlined workflow for publishing technical articles:

1. **Write once in Markdown** - Clean, version-controlled source of truth
2. **Generate HTML** - Ready for LinkedIn article editor or Medium
3. **Publish to Google Docs** - For sharing, review, and collaboration
4. **Visual One-Pager PDF** (optional) - Modern, colorful quick-reference for printing/sharing

The system preserves formatting (headings, bold, links, bullets) across all output formats.

## Quick Start

### Prerequisites

- Python 3.7+
- Google Cloud project with Docs API and Drive API enabled
- OAuth credentials configured (already set up for this project)

### Publishing an Article

**Standard publishing (HTML + Google Doc):**
```bash
cd G:\ai\article-publisher
python publish_article.py articles/claude-rate-limits/source.md "Understanding Claude API Rate Limits"
```

This generates:
- ✅ **HTML**: `articles/claude-rate-limits/article.html` (paste into LinkedIn editor)
- ✅ **Google Doc**: URL saved to `articles/claude-rate-limits/gdoc_url.txt` (for sharing)
- ✅ **Markdown**: `articles/claude-rate-limits/source.md` (source of truth)

**With visual one-pager PDF:**
```bash
python publish_article.py articles/claude-rate-limits/source.md "Understanding Claude API Rate Limits" --visual
```

This adds:
- ✅ **Visual PDF**: `articles/claude-rate-limits/visual_reference.pdf` (printable quick-reference)

## Project Structure

```
article-publisher/
├── publish_article.py             # Main publishing script (CLI)
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── .auth/                         # OAuth tokens
│   └── token.json                # Google API access token
├── lib/                           # Local libraries
│   ├── format_utils.py           # Markdown parser with hyperlink support
│   ├── html_generator.py         # HTML generator with LinkedIn styling
│   └── visual_reference_generator.py  # PDF one-pager generator
├── articles/                      # Published articles
│   └── claude-rate-limits/       # Example article
│       ├── source.md             # Markdown source (canonical)
│       ├── article.html          # HTML output
│       ├── gdoc_url.txt          # Google Doc URL
│       └── visual_reference.pdf  # Visual one-pager (optional)
└── templates/                     # Reusable templates
    ├── linkedin-article.md       # Article template with guidelines
    └── article-styles.css        # CSS template for HTML output
```

## Supported Markdown Features

The formatter supports:

- **Headings**: `## Heading 2`, `### Heading 3`
- **Bold text**: `**bold**`
- **Links**: `[text](url)` - Rendered as clickable hyperlinks
- **Bullet lists**: `- item`
- **Horizontal rules**: `---`
- **Code blocks**: ` ```code``` `

### Hyperlinks

Links are fully supported across all formats:

```markdown
Check the [Claude API docs](https://docs.anthropic.com) for details.
```

This renders as:
- **HTML**: Clickable blue link with hover effects
- **Google Docs**: Clickable hyperlink with standard Docs styling
- **Markdown**: Preserved as-is for version control

## Writing Guidelines

### Article Structure

1. **Title** (H1): Clear, compelling, under 80 characters
2. **Subtitle** (H2): Expands on title, provides context
3. **Attribution**: Required preface with author info
4. **Sections** (H2): Organize content with descriptive headings
5. **Subsections** (H3): Break down complex topics
6. **Key Takeaways**: Bulleted summary near the end
7. **Call to Action**: Next steps for readers

### Style Guidelines

- **Tone**: Professional but conversational (explain to a smart colleague)
- **Length**: 1,500-2,500 words for comprehensive articles
- **Paragraphs**: 3-4 sentences max for scannability
- **Headings**: Frequent (every 200-300 words) for easy navigation
- **Examples**: Concrete code or scenarios preferred over theory
- **Links**: 3-5 strategic links to docs, tools, or resources

### Attribution Template

Every article must include this attribution preface (between subtitle and first section):

```markdown
*This article's content and analytical perspective were crafted by [MODEL_NAME]. The project genesis and direction came from Glenn Highcove. For more information and feedback, connect with Glenn on [LinkedIn](https://www.linkedin.com/in/glennhighcove/).*

---
```

Replace `[MODEL_NAME]` with the actual model (e.g., "Claude Sonnet 4.5").

## Publishing Workflow

### 1. Write Article

Create a new article directory and markdown file:

```bash
mkdir -p articles/my-new-article
# Edit articles/my-new-article/source.md
```

Use `templates/linkedin-article.md` as a starting point.

### 2. Publish All Formats

```bash
python publish_article.py articles/my-new-article/source.md "Article Title"
```

### 3. Review and Share

- **HTML**: Open `article.html` in browser to preview
- **Google Doc**: Click URL from console output to review formatting
- **LinkedIn**: Copy HTML or Google Doc content into LinkedIn article editor

### 4. Iterate

Edit `source.md` and re-run `publish_article.py` to regenerate all formats.

## Technical Details

### OAuth Authentication

The system uses OAuth 2.0 for Google API access:

- **Credentials**: Stored at `C:\ai\whiteboard\.whiteboard\sync\credentials.json`
- **Token**: Cached at `.auth/token.json` (auto-refreshed)
- **Scopes**: `docs.documents`, `drive.file`

On first run, you'll be prompted to authorize via browser. Subsequent runs use the cached token.

### Format Conversion Pipeline

**Markdown → Google Docs:**

1. Parse markdown into clean text + formatting directives (`format_utils.py`)
2. Insert clean text into new Google Doc
3. Apply formatting via Docs API batch requests (headings, bold, links, bullets)

**Markdown → HTML:**

1. Convert markdown to HTML with `markdown2` library
2. Wrap in template with embedded LinkedIn-optimized CSS
3. Save as standalone HTML file

### HTML Styling

HTML output uses LinkedIn-inspired styling:

- Clean, professional typography
- 740px max width (optimal for readability)
- LinkedIn blue (`#0a66c2`) for links
- Responsive to browser width
- Print-friendly layout

### Visual One-Pager PDF

The optional visual reference feature (enabled with `--visual` flag) generates a modern, colorful single-page PDF:

**Content extraction:**
- Title and subtitle from article
- Key findings section (or bold statements from intro)
- Major sections with condensed bullet points
- Data points and metrics highlighted
- Attribution footer with LinkedIn link

**Design features:**
- Modern color scheme (blues, purples, greens, oranges)
- Rounded corners and professional typography
- Optimized for single-page printing
- Flexible layout adapts to article content

**Use cases:**
- Quick reference for desk/wall posting
- Printable handout for meetings/presentations
- Visual complement to text-heavy formats
- Social sharing (more engaging than plain text)

**Technical stack:**
- ReportLab 3.6.13 for PDF generation (Python 3.8 compatible)
- Intelligent content extraction from markdown
- Dynamic layout based on article length

## Extending the System

### Adding Table Support

To support markdown tables, extend `format_utils.py`:

1. Parse table syntax in `parse_markdown()`
2. Generate table formatting requests in `build_formatting_requests()`
3. Update HTML generator to style tables (already supported by `markdown2`)

### Creating a Skill

For one-command publishing, create a Claude Code skill:

```bash
/publish-article articles/my-article/source.md "Title"
```

This would wrap the Python script as a reusable skill.

### Medium Publishing

To add Medium support:

1. Use Medium API for programmatic publishing
2. Convert HTML to Medium's JSON format
3. Extend `publish_article.py` with `--medium` flag

## Troubleshooting

### "Invalid grant" Error

OAuth token expired. Delete `.auth/token.json` and re-run to trigger re-authentication.

### Links Not Rendering

Ensure link syntax is correct: `[text](url)` with no spaces. Check console output for parsing errors.

### Formatting Issues in Google Docs

The formatter resets all text to 11pt black font first to prevent inherited formatting. If issues persist, check directive generation in `parse_markdown()`.

### Python Import Errors

Ensure required packages are installed:

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client markdown2
```

For visual PDF generation:
```bash
pip install reportlab==3.6.13
```

**Note**: ReportLab 3.6.13 is required for Python 3.8 compatibility. ReportLab 4.x requires Python 3.9+ due to `hashlib.md5(usedforsecurity=False)` parameter.

### Visual PDF Generation Errors

If you see `'usedforsecurity' is an invalid keyword argument` error:
```bash
pip install reportlab==3.6.13
```

## Examples

### Published Articles

- **Claude Rate Limits Guide**: `articles/claude-rate-limits/`
  - Comprehensive explanation of per-model rate limits and optimization strategies
  - Demonstrates all supported markdown features
  - ~2,600 words with multiple sections and examples

## Future Enhancements

- [x] SEO metadata generation (✅ implemented)
- [x] Visual one-pager PDF reference (✅ implemented)
- [x] Enhanced visual PDF: charts, diagrams, iconography (✅ implemented)
- [ ] Advanced visual PDF v2: line charts, custom templates, user customization options
- [ ] Table support in Google Docs
- [ ] Image upload and embedding
- [ ] Medium API integration
- [ ] Article analytics tracking
- [ ] Create `/publish-article` skill
- [ ] Automated LinkedIn posting via API
- [ ] A/B testing for headline optimization

## Contact

Project created by Glenn Highcove. Connect on [LinkedIn](https://www.linkedin.com/in/glennhighcove/) for questions or feedback.
