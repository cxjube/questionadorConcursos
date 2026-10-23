"""Expose validation and deterministic generation without extraction or servers."""
import argparse
import sys

from tools.build import render, write_artifact
from tools.site import check_site
from tools.source_audit import audit_sources
from tools.review_batch import validate_batch
from tools.validate import ROOT, read_json, validate


def main(argv: list[str] | None = None) -> int:
    """Run the selected operation and preserve validation failures as nonzero exits."""
    parser = argparse.ArgumentParser(description='Questionador Concursos data pipeline')
    parser.add_argument('command', choices=['validate', 'build', 'check-site', 'audit-sources', 'review-batch'])
    parser.add_argument('--check', action='store_true', help='compare generated artifact without writing')
    args = parser.parse_args(argv)
    if args.check and args.command != 'build':
        parser.error('--check is only supported with build')
    try:
        catalog = read_json(ROOT / 'data/catalog.json')
        errors = validate(catalog)
        if not errors and args.command == 'audit-sources':
            source_evidence = read_json(ROOT / 'data/source-verification.json')
            errors.extend(audit_sources(catalog, source_evidence))
        if not errors and args.command == 'review-batch':
            batch = read_json(ROOT / 'data/workbench/first-batch.json')
            errors.extend(validate_batch(batch, catalog))
        if not errors and args.command == 'check-site':
            errors.extend(check_site(ROOT))
        if not errors and args.command in {'build', 'check-site'}:
            content = render(catalog)
            target = ROOT / 'docs/data/catalog.js'
            if args.check or args.command == 'check-site':
                if not target.is_file() or target.read_text(encoding='utf-8') != content:
                    errors.append('published catalog is stale; run python -m tools build')
            else:
                write_artifact(target, content)
        if errors:
            for error in errors:
                print(f'ERROR: {error}', file=sys.stderr)
            return 1
        if args.command == 'audit-sources':
            matched = sum(row['outcome'] == 'byte_match' for row in source_evidence['documents'])
            print(f'audit-sources: OK ({matched} official downloads matched; {len(source_evidence["documents"]) - matched} PDF identities pending)')
        elif args.command == 'review-batch':
            print(f'review-batch: OK ({len(batch["items"])} preparation records validated; workbench excluded from site)')
        else:
            print(f'{args.command}: OK ({len(catalog["questions"])} questions)')
        return 0
    except (OSError, ValueError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
