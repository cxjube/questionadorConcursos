"""Expose validation and deterministic generation without extraction or servers."""
import argparse
import sys

from tools.build import render, render_logistics, write_artifact
from tools.logistics import validate_logistics
from tools.coverage import CURRENT_REVIEW_PATH, current_artifacts, role_artifacts
from tools.site import check_site
from tools.source_audit import audit_sources
from tools.review_batch import validate_batch
from tools.validate import ROOT, read_json, validate


def main(argv: list[str] | None = None) -> int:
    """Run the selected operation and preserve validation failures as nonzero exits."""
    parser = argparse.ArgumentParser(description='Questionador Concursos data pipeline')
    parser.add_argument('command', choices=['validate', 'build', 'check-site', 'audit-sources', 'review-batch', 'coverage'])
    parser.add_argument('--check', action='store_true', help='compare generated artifact without writing')
    parser.add_argument('--role', help='generate a separate role coverage report')
    args = parser.parse_args(argv)
    if args.role and args.command != 'coverage':
        parser.error('--role is only supported with coverage')
    if args.check and args.command not in {'build', 'coverage'}:
        parser.error('--check is only supported with build or coverage')
    try:
        catalog = read_json(ROOT / 'data/catalog.json')
        errors = validate(catalog)
        if not errors:
            logistics = read_json(ROOT / 'data/contest-logistics.json')
            errors.extend(validate_logistics(logistics, catalog))
        if not errors and args.command == 'coverage':
            if args.role and args.role not in {'abdi-comunicacao-marketing', 'cgu-auditoria'}:
                parser.error('unsupported coverage role')
            review = read_json(ROOT / CURRENT_REVIEW_PATH)
            artifacts = role_artifacts(catalog, review, args.role) if args.role else current_artifacts(catalog, review)
            for filename, content in artifacts.items():
                target = ROOT / filename
                if args.check:
                    if not target.is_file() or target.read_text(encoding='utf-8') != content:
                        errors.append(f'{filename} is stale; run python -m tools coverage')
                else:
                    target.write_text(content, encoding='utf-8')
        if not errors and args.command == 'audit-sources':
            source_evidence = read_json(ROOT / 'data/source-verification.json')
            errors.extend(audit_sources(catalog, source_evidence))
        if not errors and args.command == 'review-batch':
            batch = read_json(ROOT / 'data/workbench/first-batch.json')
            errors.extend(validate_batch(batch, catalog))
        if not errors and args.command == 'check-site':
            errors.extend(check_site(ROOT))
        if not errors and args.command in {'build', 'check-site'}:
            logistics_content = render_logistics(logistics)
            logistics_target = ROOT / 'docs/data/logistics.js'
            if args.check or args.command == 'check-site':
                if not logistics_target.is_file() or logistics_target.read_text(encoding='utf-8') != logistics_content:
                    errors.append('published logistics is stale; run python -m tools build')
            else:
                write_artifact(logistics_target, logistics_content)
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
            print(f'audit-sources: OK ({matched} official downloads matched; {len(source_evidence["documents"]) - matched} document identities pending)')
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
