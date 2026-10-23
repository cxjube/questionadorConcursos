"""Offline reading of retained legal HTML, excluding struck historical wording."""
from html.parser import HTMLParser
import re


class _VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.parts = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        hidden = tag in {'script', 'style', 's', 'strike', 'del'} or 'line-through' in attributes.get('style', '').lower()
        if tag not in {'br', 'meta', 'link', 'img', 'hr', 'input', 'wbr'}:
            self.stack.append((tag, hidden))
        if tag in {'p', 'div', 'br'}:
            self.parts.append(' ')

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                self.stack = self.stack[:index]
                break
        if tag in {'p', 'div'}:
            self.parts.append(' ')

    def handle_data(self, value):
        if not any(hidden for _, hidden in self.stack):
            self.parts.append(value)


def reference_text(raw: bytes) -> str:
    """Use the declared source encoding and normalize layout whitespace only."""
    charset = re.search(br'charset\s*=\s*["\']?([a-zA-Z0-9_-]+)', raw[:10000], re.I)
    if charset:
        source = raw.decode(charset.group(1).decode('ascii'))
    else:
        try:
            source = raw.decode('utf-8')
        except UnicodeDecodeError:
            source = raw.decode('windows-1252')
    parser = _VisibleText()
    parser.feed(source)
    return ' '.join(''.join(parser.parts).split())
