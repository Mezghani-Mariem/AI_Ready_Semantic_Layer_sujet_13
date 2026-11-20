#!/usr/bin/env python3
"""Idempotent TMDL descriptions injector. Uses only stdlib. Never changes DAX or source M."""
import argparse, pathlib, json, re, shutil
P=re.compile(r"^(\t?)(table|column|measure)\s+('(?:[^']|'')*'|[^\s=]+)(?=\s|$)")
def apply(root,dictionary,check=False):
    root=pathlib.Path(root)
    folder=root/'definition'/'tables'
    if not folder.is_dir():raise SystemExit('ERROR: Expected SemanticModel/definition/tables: '+str(folder))
    data=json.loads(pathlib.Path(dictionary).read_text(encoding='utf-8'))
    targets={(e['table'],e['kind'],e['name']):e['description'] for e in data}
    found=set();modified=0
    for f in sorted(folder.glob('*.tmdl')):
        before=f.read_text(encoding='utf-8-sig')
        lines=before.splitlines(keepends=True)
        newline='\r\n' if '\r\n' in before else '\n'
        result=[]
        for line in lines:
            m=P.match(line.rstrip('\r\n'))
            if not m:
                result.append(line);continue
            raw=m.group(3);name=raw[1:-1].replace("''", "'") if raw.startswith("'") else raw
            key=(f.stem,m.group(2),name)
            if key not in targets:
                result.append(line);continue
            found.add(key)
            desc=targets[key].replace('\n',' ').strip()
            if '///' in desc:raise SystemExit('Invalid description: '+repr(key))
            # remove an adjacent existing /// description block (not other TMDL properties)
            while result and result[-1].strip().startswith('///'):
                result.pop()
            prefix=m.group(1)
            result.append(prefix+'/// '+desc+newline)
            result.append(line)
        after=''.join(result)
        if after != before:
            modified+=1
            if not check:f.write_text(after,encoding='utf-8',newline='')
    missing=sorted(set(targets)-found)
    print(f'Found {len(found)}/{len(targets)} metadata targets. Files differing: {modified}. Check mode: {check}.')
    if missing:raise SystemExit('ERROR: missing targets: '+repr(missing))
    if check and modified:raise SystemExit('ERROR: model descriptions do not match dictionary')
    print('OK: all targets matched')
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('semantic_model_dir',help='Folder with definition/tables');a.add_argument('--dictionary',default=str(pathlib.Path(__file__).resolve().parent.parent/'metadata'/'semantic_dictionary.json'));a.add_argument('--check',action='store_true');args=a.parse_args()
    apply(args.semantic_model_dir,args.dictionary,args.check)
