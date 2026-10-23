"""Guard the small public artifact against source PDFs and unexpected files."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit

PUBLIC_FILES = {
    '.nojekyll', 'index.html', 'assets/css/styles.css', 'assets/js/types.js',
    'assets/js/storage.js', 'assets/js/theme.js', 'assets/js/catalog.js',
    'assets/js/main.js', 'assets/js/study.js', 'assets/js/progress.js',
    'assets/js/study-ui.js', 'data/catalog.js',
}


class AssetParser(HTMLParser):
    """Collect runtime asset destinations without treating credit links as assets."""

    def __init__(self) -> None:
        """Initialize the runtime asset collection."""
        super().__init__()
        self.assets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Collect script, image, frame and stylesheet dependencies."""
        attributes = dict(attrs)
        if tag in {'script', 'img', 'iframe', 'source'} and attributes.get('src'):
            self.assets.append(attributes['src'])
        if tag == 'link' and attributes.get('href'):
            self.assets.append(attributes['href'])


def check_site(root: Path) -> list[str]:
    """Require the reviewed static file set and existing relative runtime assets."""
    docs = root / 'docs'
    errors = []
    actual = {str(p.relative_to(docs)) for p in docs.rglob('*') if p.is_file()}
    if actual != PUBLIC_FILES:
        errors.append(f'public files mismatch: missing={sorted(PUBLIC_FILES - actual)}, unexpected={sorted(actual - PUBLIC_FILES)}')
    for p in docs.rglob('*'):
        if p.is_symlink():
            errors.append(f'public symlink forbidden: {p.name}')
    parser = AssetParser()
    parser.feed((docs / 'index.html').read_text(encoding='utf-8'))
    for asset in parser.assets:
        parsed = urlsplit(asset)
        path = (docs / parsed.path).resolve()
        if parsed.scheme or parsed.netloc or asset.startswith('/') or not path.is_relative_to(docs.resolve()) or not path.is_file():
            errors.append(f'invalid runtime asset: {asset}')
    return errors
