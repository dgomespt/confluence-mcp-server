"""HTML to Markdown conversion utilities for RAG/agent consumption."""
from bs4 import BeautifulSoup
import re


def html_to_markdown(html_content: str) -> str:
    """Convert HTML content to clean Markdown format.
    
    This function parses HTML and converts it to Markdown that is
    suitable for LLM/RAG consumption, with proper formatting for
    code blocks, lists, tables, headers, and links.
    
    Args:
        html_content: The HTML content to convert.
    
    Returns:
        Markdown-formatted string.
    """
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style tags
    for tag in soup(['script', 'style', 'noscript']):
        tag.decompose()
    
    def process_element(element):
        """Recursively process an element and its children."""
        if isinstance(element, str):
            text = str(element).strip()
            return text if text else ""
        
        tag_name = element.name
        if tag_name is None:
            # Handle navigable strings
            text = str(element).strip()
            return text if text else ""
        
        # Handle common HTML tags
        if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag_name[1])
            text = get_element_text(element)
            return f"\n{'#' * level} {text}\n"
        
        elif tag_name == 'p':
            parts = []
            for child in element.children:
                child_result = process_element(child)
                if child_result:
                    parts.append(str(child_result))
            text = ''.join(parts).strip()
            return f"{text}\n" if text else ""
        
        elif tag_name in ['b', 'strong']:
            text = get_element_text(element)
            return f"**{text}**"
        
        elif tag_name in ['i', 'em']:
            text = get_element_text(element)
            return f"*{text}*"
        
        elif tag_name == 'code':
            text = get_element_text(element)
            # Check if it's inline or block
            if element.parent and element.parent.name == 'pre':
                return text
            return f"`{text}`"
        
        elif tag_name == 'pre':
            code = element.get_text()
            # Try to detect language from class
            classes = element.get('class', [])
            lang = ''
            for c in classes:
                if c.startswith('language-'):
                    lang = c.replace('language-', '') + ' '
            return f"\n```{lang}{code.strip()}\n```\n"
        
        elif tag_name == 'a':
            text = get_element_text(element)
            href = element.get('href', '')
            if href:
                return f"[{text}]({href})"
            return text
        
        elif tag_name == 'ul':
            items = []
            for li in element.find_all('li', recursive=False):
                item_text = get_element_text(li)
                items.append(f"- {item_text}")
            return '\n'.join(items) + '\n'
        
        elif tag_name == 'ol':
            items = []
            for i, li in enumerate(element.find_all('li', recursive=False), 1):
                item_text = get_element_text(li)
                items.append(f"{i}. {item_text}")
            return '\n'.join(items) + '\n'
        
        elif tag_name == 'li':
            parts = []
            for child in element.children:
                child_result = process_element(child)
                if child_result:
                    parts.append(str(child_result))
            return ''.join(parts).strip()
        
        elif tag_name == 'table':
            return process_table(element)
        
        elif tag_name == 'br':
            return '\n'
        
        elif tag_name == 'hr':
            return '\n---\n'
        
        elif tag_name == 'img':
            alt = element.get('alt', '')
            src = element.get('src', '')
            if src:
                return f"![{alt}]({src})"
            return ""
        
        elif tag_name == 'blockquote':
            text = get_element_text(element)
            lines = text.split('\n')
            quoted = '\n'.join(f"> {line}" for line in lines if line)
            return f"{quoted}\n"
        
        elif tag_name in ['div', 'span', 'section', 'article', 'main', 'body']:
            # Container elements - process children
            parts = []
            for child in element.children:
                result = process_element(child)
                if result:
                    parts.append(str(result))
            return ''.join(parts)
        
        else:
            # For any other tags, just get text content
            return get_element_text(element)
    
    def get_element_text(element):
        """Get text content while preserving inline formatting."""
        parts = []
        for child in element.children:
            if isinstance(child, str):
                parts.append(str(child))
            elif child.name in ['strong', 'b']:
                text = child.get_text(strip=True)
                if text:
                    parts.append(f"**{text}**")
            elif child.name in ['em', 'i']:
                text = child.get_text(strip=True)
                if text:
                    parts.append(f"*{text}*")
            elif child.name == 'code':
                text = child.get_text(strip=True)
                if text:
                    parts.append(f"`{text}`")
            elif child.name == 'a':
                text = child.get_text(strip=True)
                href = child.get('href', '')
                if text and href:
                    parts.append(f"[{text}]({href})")
                elif text:
                    parts.append(text)
            else:
                text = child.get_text(strip=True)
                if text:
                    parts.append(text)
        return ''.join(parts)
    
    def process_table(table):
        """Process an HTML table into Markdown."""
        rows = table.find_all('tr')
        if not rows:
            return ""
        
        markdown_rows = []
        
        for i, row in enumerate(rows):
            cells = row.find_all(['th', 'td'])
            cell_texts = [get_element_text(cell) for cell in cells]
            
            if i == 0 and not markdown_rows:
                # Header row
                markdown_rows.append('| ' + ' | '.join(cell_texts) + ' |')
                markdown_rows.append('| ' + ' | '.join(['---'] * len(cell_texts)) + ' |')
            else:
                markdown_rows.append('| ' + ' | '.join(cell_texts) + ' |')
        
        return '\n'.join(markdown_rows) + '\n'
    
    # Process all children of the body or root element
    markdown_parts = []
    for child in soup.children:
        result = process_element(child)
        if result:
            markdown_parts.append(str(result))
    
    # Join and clean up
    markdown = ''.join(markdown_parts)
    
    # Clean up multiple blank lines
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    
    # Clean up trailing whitespace on lines
    lines = [line.rstrip() for line in markdown.split('\n')]
    markdown = '\n'.join(lines)
    
    return markdown.strip()


def html_to_markdown_simple(html_content: str) -> str:
    """Simple HTML to Markdown conversion without full parsing.
    
    This is a fallback for when BeautifulSoup isn't available or
    for very simple HTML content.
    
    Args:
        html_content: The HTML content to convert.
    
    Returns:
        Markdown-formatted string.
    """
    if not html_content:
        return ""
    
    # Simple replacements
    md = html_content
    
    # Headers
    md = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1\n', md, flags=re.DOTALL)
    md = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1\n', md, flags=re.DOTALL)
    md = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1\n', md, flags=re.DOTALL)
    md = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1\n', md, flags=re.DOTALL)
    md = re.sub(r'<h5[^>]*>(.*?)</h5>', r'##### \1\n', md, flags=re.DOTALL)
    md = re.sub(r'<h6[^>]*>(.*?)</h6>', r'###### \1\n', md, flags=re.DOTALL)
    
    # Bold and italic
    md = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', md, flags=re.DOTALL)
    md = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', md, flags=re.DOTALL)
    md = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', md, flags=re.DOTALL)
    md = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', md, flags=re.DOTALL)
    
    # Code blocks
    md = re.sub(r'<pre[^>]*><code[^>]*>(.*?)</code></pre>', r'```\n\1\n```', md, flags=re.DOTALL)
    md = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', md, flags=re.DOTALL)
    
    # Links
    md = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', md, flags=re.DOTALL)
    
    # Lists
    md = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', md, flags=re.DOTALL)
    md = re.sub(r'<ul[^>]*>(.*?)</ul>', r'\1', md, flags=re.DOTALL)
    md = re.sub(r'<ol[^>]*>(.*?)</ol>', r'\1', md, flags=re.DOTALL)
    
    # Paragraphs and breaks
    md = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', md, flags=re.DOTALL)
    md = re.sub(r'<br[^>]*>', r'\n', md)
    md = re.sub(r'<br/>', r'\n', md)
    
    # Remove remaining HTML tags
    md = re.sub(r'<[^>]+>', '', md)
    
    # Decode HTML entities
    md = md.replace('&nbsp;', ' ')
    md = md.replace('&amp;', '&')
    md = md.replace('&lt;', '<')
    md = md.replace('&gt;', '>')
    md = md.replace('&quot;', '"')
    md = md.replace('&#39;', "'")
    
    # Clean up
    md = re.sub(r'\n{3,}', '\n\n', md)
    
    return md.strip()
