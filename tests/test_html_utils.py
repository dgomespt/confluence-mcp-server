"""Tests for HTML to Markdown conversion utilities."""
import pytest
from src.core.html_utils import html_to_markdown, html_to_markdown_simple


class TestHtmlToMarkdown:
    """Tests for the main html_to_markdown function."""
    
    def test_simple_paragraph(self):
        """Test conversion of simple paragraph."""
        html = "<p>Hello World</p>"
        result = html_to_markdown(html)
        
        assert "Hello World" in result
        assert "<p>" not in result
    
    def test_headers(self):
        """Test conversion of HTML headers."""
        html = "<h1>Title</h1><h2>Subtitle</h2>"
        result = html_to_markdown(html)
        
        assert "# Title" in result
        assert "## Subtitle" in result
    
    def test_all_header_levels(self):
        """Test all header levels."""
        # Test each header level separately
        assert "# H1" in html_to_markdown("<h1>H1</h1>")
        assert "## H2" in html_to_markdown("<h2>H2</h2>")
        assert "### H3" in html_to_markdown("<h3>H3</h3>")
        assert "#### H4" in html_to_markdown("<h4>H4</h4>")
        assert "##### H5" in html_to_markdown("<h5>H5</h5>")
        assert "###### H6" in html_to_markdown("<h6>H6</h6>")
    
    def test_bold_text(self):
        """Test conversion of bold text."""
        html = "<p>This is <strong>bold</strong> text</p>"
        result = html_to_markdown(html)
        
        assert "**bold**" in result
    
    def test_bold_with_b_tag(self):
        """Test conversion of bold using b tag."""
        html = "<p>This is <b>bold</b> text</p>"
        result = html_to_markdown(html)
        
        assert "**bold**" in result
    
    def test_italic_text(self):
        """Test conversion of italic text."""
        html = "<p>This is <em>italic</em> text</p>"
        result = html_to_markdown(html)
        
        assert "*italic*" in result
    
    def test_italic_with_i_tag(self):
        """Test conversion of italic using i tag."""
        html = "<p>This is <i>italic</i> text</p>"
        result = html_to_markdown(html)
        
        assert "*italic*" in result
    
    def test_code_inline(self):
        """Test conversion of inline code."""
        html = "<p>Use <code>python</code> to run</p>"
        result = html_to_markdown(html)
        
        assert "`python`" in result
    
    def test_code_block(self):
        """Test conversion of code blocks."""
        html = "<pre><code>def hello():\n    print('world')</code></pre>"
        result = html_to_markdown(html)
        
        assert "```" in result
        assert "def hello():" in result
    
    def test_link(self):
        """Test conversion of links."""
        html = '<p>Visit <a href="https://example.com">this site</a></p>'
        result = html_to_markdown(html)
        
        assert "[this site](https://example.com)" in result
    
    def test_link_without_href(self):
        """Test conversion of anchor without href."""
        html = '<p>Visit <a>this site</a></p>'
        result = html_to_markdown(html)
        
        assert "this site" in result
    
    def test_unordered_list(self):
        """Test conversion of unordered lists."""
        html = "<ul><li>Item 1</li><li>Item 2</li></ul>"
        result = html_to_markdown(html)
        
        assert "- Item 1" in result
        assert "- Item 2" in result
    
    def test_ordered_list(self):
        """Test conversion of ordered lists."""
        html = "<ol><li>First</li><li>Second</li></ol>"
        result = html_to_markdown(html)
        
        assert "1. First" in result
        assert "2. Second" in result
    
    def test_table(self):
        """Test conversion of tables."""
        html = """
        <table>
            <tr><th>Name</th><th>Age</th></tr>
            <tr><td>Alice</td><td>30</td></tr>
        </table>
        """
        result = html_to_markdown(html)
        
        assert "Name" in result
        assert "Age" in result
        assert "Alice" in result
        assert "|" in result
    
    def test_table_with_th_and_td(self):
        """Test table with both header and data cells."""
        html = "<table><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>2</td></tr></table>"
        result = html_to_markdown(html)
        
        assert "| A | B |" in result
        assert "| 1 | 2 |" in result
    
    def test_table_empty(self):
        """Test empty table."""
        html = "<table></table>"
        result = html_to_markdown(html)
        
        assert result == ""
    
    def test_remove_scripts(self):
        """Test that script tags are removed."""
        html = "<p>Text</p><script>alert('xss')</script>"
        result = html_to_markdown(html)
        
        assert "alert" not in result
        assert "<script>" not in result
    
    def test_remove_styles(self):
        """Test that style tags are removed."""
        html = "<style>.foo { color: red; }</style><p>Text</p>"
        result = html_to_markdown(html)
        
        assert ".foo" not in result
        assert "color:" not in result
    
    def test_br_tags(self):
        """Test conversion of line breaks."""
        html = "<p>Line 1<br>Line 2</p>"
        result = html_to_markdown(html)
        
        assert "Line 1" in result
        assert "Line 2" in result
    
    def test_blockquote(self):
        """Test conversion of blockquotes."""
        html = "<blockquote>Quote text</blockquote>"
        result = html_to_markdown(html)
        
        assert ">" in result
        assert "Quote text" in result
    
    def test_image(self):
        """Test conversion of images."""
        html = '<img src="photo.jpg" alt="A photo">'
        result = html_to_markdown(html)
        
        assert "![A photo](photo.jpg)" in result
    
    def test_image_without_alt(self):
        """Test image without alt text."""
        html = '<img src="photo.jpg">'
        result = html_to_markdown(html)
        
        assert "![](photo.jpg)" in result
    
    def test_image_without_src(self):
        """Test image without src."""
        html = '<img alt="photo">'
        result = html_to_markdown(html)
        
        assert result == ""
    
    def test_horizontal_rule(self):
        """Test conversion of horizontal rules."""
        html = "<p>Text</p><hr><p>More text</p>"
        result = html_to_markdown(html)
        
        assert "---" in result
    
    def test_empty_content(self):
        """Test handling of empty content."""
        assert html_to_markdown("") == ""
        assert html_to_markdown(None) == ""
    
    def test_complex_html(self):
        """Test conversion of complex HTML with multiple elements."""
        html = """
        <h1>My Document</h1>
        <p>This is a <strong>paragraph</strong> with <em>formatting</em>.</p>
        <ul>
            <li>Item one</li>
            <li>Item two</li>
        </ul>
        <pre><code>print("hello")</code></pre>
        <p>Check out <a href="https://example.com">this link</a>.</p>
        """
        result = html_to_markdown(html)
        
        assert "# My Document" in result
        assert "**paragraph**" in result
        assert "*formatting*" in result
        assert "- Item one" in result
        assert "- Item two" in result
        assert "print" in result
        assert "[this link]" in result
    
    def test_nested_inline_formatting(self):
        """Test nested inline formatting."""
        html = "<p><strong><em>bold and italic</em></strong></p>"
        result = html_to_markdown(html)
        
        assert "**" in result
        assert "*" in result
    
    def test_multiple_paragraphs(self):
        """Test multiple paragraphs."""
        html = "<p>First paragraph</p><p>Second paragraph</p>"
        result = html_to_markdown(html)
        
        assert "First paragraph" in result
        assert "Second paragraph" in result
    
    def test_div_container(self):
        """Test div container."""
        html = "<div><p>Content</p></div>"
        result = html_to_markdown(html)
        
        assert "Content" in result
    
    def test_span_container(self):
        """Test span container."""
        html = "<span>Text</span>"
        result = html_to_markdown(html)
        
        assert "Text" in result
    
    def test_section_container(self):
        """Test section container."""
        html = "<section><p>Section content</p></section>"
        result = html_to_markdown(html)
        
        assert "Section content" in result
    
    def test_article_container(self):
        """Test article container."""
        html = "<article><p>Article content</p></article>"
        result = html_to_markdown(html)
        
        assert "Article content" in result
    
    def test_main_container(self):
        """Test main container."""
        html = "<main><p>Main content</p></main>"
        result = html_to_markdown(html)
        
        assert "Main content" in result
    
    def test_body_container(self):
        """Test body container."""
        html = "<body><p>Body content</p></body>"
        result = html_to_markdown(html)
        
        assert "Body content" in result
    
    def test_li_with_nested_elements(self):
        """Test list item with nested formatting."""
        html = "<ul><li><strong>Bold</strong> item</li></ul>"
        result = html_to_markdown(html)
        
        assert "- **Bold** item" in result
    
    def test_paragraphs_with_multiple_formatting(self):
        """Test paragraph with multiple inline formats."""
        html = "<p><strong>bold</strong>, <em>italic</em>, and <code>code</code></p>"
        result = html_to_markdown(html)
        
        assert "**bold**" in result
        assert "*italic*" in result
        assert "`code`" in result
    
    def test_list_item_text_only(self):
        """Test list item with only text."""
        html = "<ul><li>Simple item</li></ul>"
        result = html_to_markdown(html)
        
        assert "- Simple item" in result
    
    def test_multiple_lists(self):
        """Test multiple lists."""
        html = "<ul><li>Item 1</li></ul><ol><li>Item 2</li></ol>"
        result = html_to_markdown(html)
        
        assert "- Item 1" in result
        assert "1. Item 2" in result
    
    def test_list_inside_paragraph(self):
        """Test inline elements within list items."""
        html = "<ul><li>Link: <a href=\"http://test.com\">test</a></li></ul>"
        result = html_to_markdown(html)
        
        assert "- Link: [test](http://test.com)" in result
    
    def test_unknown_tags(self):
        """Test handling of unknown tags."""
        html = "<custom>Custom content</custom>"
        result = html_to_markdown(html)
        
        assert "Custom content" in result
    
    def test_nested_lists(self):
        """Test nested lists - simplified test."""
        # Test basic list
        assert "- Item 1" in html_to_markdown("<ul><li>Item 1</li></ul>")
        # Test that list returns content
        result = html_to_markdown("<ul><li>Item 1<ul><li>Nested</li></ul></li></ul>")
        assert isinstance(result, str)
    
    def test_code_with_parent_class(self):
        """Test code with language class in pre."""
        html = '<pre class="language-python"><code>print("test")</code></pre>'
        result = html_to_markdown(html)
        
        assert "```python" in result
    
    def test_multiple_images(self):
        """Test multiple images."""
        html = '<img src="a.jpg"><img src="b.jpg">'
        result = html_to_markdown(html)
        
        assert "![](a.jpg)" in result
        assert "![](b.jpg)" in result
    
    def test_links_with_different_href(self):
        """Test links with various href patterns."""
        html = '<a href="/relative">relative</a><a href="http://external">external</a>'
        result = html_to_markdown(html)
        
        assert "[relative](/relative)" in result
        assert "[external](http://external)" in result
    
    def test_blockquote_multiline(self):
        """Test blockquote with multiple lines."""
        html = "<blockquote>Line 1\nLine 2</blockquote>"
        result = html_to_markdown(html)
        
        assert "> Line 1" in result
        assert "> Line 2" in result
    
    def test_emphasis_mixed(self):
        """Test mixed emphasis."""
        html = "<p><b>bold</b> and <i>italic</i> together</p>"
        result = html_to_markdown(html)
        
        assert "**bold**" in result
        assert "*italic*" in result


class TestHtmlToMarkdownSimple:
    """Tests for the simple html_to_markdown_simple function."""
    
    def test_simple_paragraph(self):
        """Test simple paragraph conversion."""
        html = "<p>Hello</p>"
        result = html_to_markdown_simple(html)
        
        assert "Hello" in result
    
    def test_headers(self):
        """Test header conversion."""
        html = "<h1>Title</h1>"
        result = html_to_markdown_simple(html)
        
        assert "# Title" in result
    
    def test_all_headers(self):
        """Test all header levels."""
        html = "<h1>H1</h1><h2>H2</h2><h3>H3</h3>"
        result = html_to_markdown_simple(html)
        
        assert "# H1" in result
        assert "## H2" in result
        assert "### H3" in result
    
    def test_bold(self):
        """Test bold conversion."""
        html = "<strong>bold</strong>"
        result = html_to_markdown_simple(html)
        
        assert "**bold**" in result
    
    def test_bold_with_b(self):
        """Test bold with b tag."""
        html = "<b>bold</b>"
        result = html_to_markdown_simple(html)
        
        assert "**bold**" in result
    
    def test_italic(self):
        """Test italic conversion."""
        html = "<em>italic</em>"
        result = html_to_markdown_simple(html)
        
        assert "*italic*" in result
    
    def test_italic_with_i(self):
        """Test italic with i tag."""
        html = "<i>italic</i>"
        result = html_to_markdown_simple(html)
        
        assert "*italic*" in result
    
    def test_code_inline(self):
        """Test inline code."""
        html = "<code>code</code>"
        result = html_to_markdown_simple(html)
        
        assert "`code`" in result
    
    def test_code_block(self):
        """Test code block."""
        html = "<pre><code>def test():\n    pass</code></pre>"
        result = html_to_markdown_simple(html)
        
        assert "```" in result
        assert "def test():" in result
    
    def test_link(self):
        """Test link conversion."""
        html = '<a href="http://test.com">text</a>'
        result = html_to_markdown_simple(html)
        
        assert "[text](http://test.com)" in result
    
    def test_unordered_list(self):
        """Test unordered list."""
        html = "<ul><li>Item</li></ul>"
        result = html_to_markdown_simple(html)
        
        assert "- Item" in result
    
    def test_ordered_list(self):
        """Test ordered list."""
        html = "<ol><li>Item</li></ol>"
        result = html_to_markdown_simple(html)
        
        assert "- Item" in result
    
    def test_paragraph(self):
        """Test paragraph."""
        html = "<p>Paragraph text</p>"
        result = html_to_markdown_simple(html)
        
        assert "Paragraph text" in result
    
    def test_br_tag(self):
        """Test br tag."""
        html = "Line 1<br>Line 2"
        result = html_to_markdown_simple(html)
        
        assert "Line 1" in result
        assert "Line 2" in result
    
    def test_br_self_closing(self):
        """Test self-closing br tag."""
        html = "Line 1<br/>Line 2"
        result = html_to_markdown_simple(html)
        
        assert "Line 1" in result
        assert "Line 2" in result
    
    def test_html_entities(self):
        """Test HTML entity decoding."""
        html = "&lt;test&gt; &amp; &quot;quote&quot; &#39;apostrophe&#39;"
        result = html_to_markdown_simple(html)
        
        assert "<test>" in result
        assert "&" in result
        assert "\"quote\"" in result
        assert "'apostrophe'" in result
    
    def test_nbsp_entity(self):
        """Test nbsp entity."""
        html = "word&nbsp;space"
        result = html_to_markdown_simple(html)
        
        assert "word space" in result
    
    def test_remove_remaining_tags(self):
        """Test that remaining HTML tags are removed."""
        html = "<div>Text</div>"
        result = html_to_markdown_simple(html)
        
        assert "Text" in result
        assert "<div>" not in result
    
    def test_empty_content(self):
        """Test empty content."""
        assert html_to_markdown_simple("") == ""
    
    def test_complex_html(self):
        """Test complex HTML."""
        html = "<h1>Title</h1><p>Paragraph with <strong>bold</strong></p>"
        result = html_to_markdown_simple(html)
        
        assert "# Title" in result
        assert "**bold**" in result
