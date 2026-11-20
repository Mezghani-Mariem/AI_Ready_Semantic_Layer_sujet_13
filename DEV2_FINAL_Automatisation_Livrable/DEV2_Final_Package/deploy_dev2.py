#!/usr/bin/env python3
"""Deploy DEV2 semantic metadata to an isolated COPY of a Power BI PBIP project.
Only Python standard library required. Never modifies source project.
"""
import argparse
import json
from pathlib import Path
import shutil
import sys
from inject_descriptions import apply as inject_descriptions
from inject_synonyms import transform, SYNONYMS

BASE = Path(__file__).resolve().parent

def semantic_dir(project):
    candidates = [x for x in project.iterdir() if x.is_dir() and x.name.endswith('.SemanticModel')]
    if len(candidates) != 1:
        raise ValueError(f'Expected exactly one .SemanticModel directory; found {len(candidates)}')
    return candidates[0]

def verify_compatibility(model):
    table_files = model / 'definition' / 'tables'
    data = json.loads((BASE / 'semantic_dictionary.json').read_text(encoding='utf-8'))
    for table in {e['table'] for e in data}:
        if not (table_files / (table + '.tmdl')).is_file():
            raise ValueError(f'Missing required TMDL table: {table}')
    # Validate the entire 21-object mapping against the model's TMDL declarations.
    import re
    for table, field in SYNONYMS:
        content = (table_files / (table + '.tmdl')).read_text(encoding='utf-8-sig')
        field_quoted = "'" + field.replace("'", "''") + "'"
        if not re.search(r'(?m)^\s*(?:column|measure)\s+(?:' + re.escape(field) + '|' + re.escape(field_quoted) + r')(?=\s|$)', content):
            raise ValueError(f'Missing synonym target in schema: {table}.{field}')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source_project', type=Path, help='Directory with F1.pbip and F1.SemanticModel')
    p.add_argument('output_project', type=Path, help='New project directory to create; must not exist')
    a = p.parse_args()
    source = a.source_project.resolve()
    target = a.output_project.resolve()
    if not source.is_dir() or not any(source.glob('*.pbip')):
        p.error('source_project must contain an existing .pbip file')
    if target.exists():
        p.error('output_project already exists; refusing to overwrite')
    if source == target or source in target.parents:
        p.error('output_project must be outside source_project')
    try:
        model = semantic_dir(source)
        verify_compatibility(model)
        culture = model / 'definition' / 'cultures' / 'fr-FR.tmdl'
        if not culture.is_file():
            raise ValueError('Missing fr-FR.tmdl culture file')
        current = culture.read_text(encoding='utf-8-sig').strip()
        # Do not overwrite an existing independently enriched semantic schema.
        if current != 'cultureInfo fr-FR':
            raise ValueError('Baseline culture is not minimal; refusing to overwrite. Use a clean F1 baseline.')
        template = BASE / 'fr-FR.enriched.template.tmdl'
        # Confirm the template's structured synonyms map exactly to all 21 objects.
        rendered, changes, count, _ = transform(template)
        if changes or count != len(SYNONYMS):
            raise ValueError('Linguistic template does not contain all expected approved synonyms')
        shutil.copytree(source, target, ignore=shutil.ignore_patterns('.pbi'))
        new_model = semantic_dir(target)
        inject_descriptions(new_model, BASE / 'semantic_dictionary.json', check=False)
        inject_descriptions(new_model, BASE / 'semantic_dictionary.json', check=True)
        new_culture = new_model / 'definition' / 'cultures' / 'fr-FR.tmdl'
        new_culture.write_text(rendered, encoding='utf-8')
        verify_content, new_terms, n, _ = transform(new_culture)
        if new_terms or verify_content != new_culture.read_text(encoding='utf-8'):
            raise ValueError('Unexpected linguistic template mismatch after installation')
        report = {
            'result': 'PASS', 'source': str(source), 'output': str(target),
            'description_targets': len(json.loads((BASE / 'semantic_dictionary.json').read_text(encoding='utf-8'))),
            'synonym_targets': n, 'linguistic_schema': 'fr-FR.tmdl (internal en-US)',
            'source_modified': False,
            'limitations': 'Power BI UI and data refresh must be validated separately; YAML is a saved export, not auto-imported.'
        }
        (target / 'DEV2_DEPLOYMENT_RESULT.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
        print('SUCCESS: isolated PBIP copy enriched:', target)
        print('Descriptions: 36 matched and checked; synonyms: 21 matched; source untouched.')
        print('NEXT: open copied PBIP in Power BI Desktop; check Margin and other fields.')
    except Exception as exc:
        if target.exists():
            shutil.rmtree(target)
        print('ERROR:', exc, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
