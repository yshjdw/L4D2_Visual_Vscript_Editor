"""Headless .l4vp -> .nut exporter; does not require PySide6."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from l4visual.storage import load_project
from l4visual.codegen import SquirrelGenerator
from l4visual.catalog import Catalog
from l4visual.validation import Validator


def main():
    parser=argparse.ArgumentParser(description='Export L4D2 Visual VScript project to .nut files')
    parser.add_argument('project',type=Path,help='Input .l4vp project')
    parser.add_argument('--output','-o',type=Path,required=True,help='Output folder')
    args=parser.parse_args()
    project=load_project(args.project)
    catalog=Catalog()
    results={}
    failures=0
    for document in project.documents:
        name=document.name
        if Path(name).name != name or not name.lower().endswith('.nut'):
            print('ERROR: unsafe or non-.nut filename:',name,file=sys.stderr)
            failures+=1;continue
        issues=Validator(catalog).check(project,document)
        for item in issues:
            print(f'{name} [{item.level}] {item.section}: {item.text}')
        if any(i.level=='错误' for i in issues):
            failures+=1;continue
        generator=SquirrelGenerator()
        content=generator.compile(project,document)
        if generator.errors:
            failures+=1
            print('ERROR',name,generator.errors,file=sys.stderr)
        else:results[name]=content
    catalog.close()
    if failures:
        print(f'{failures} file(s) failed validation; nothing exported.',file=sys.stderr)
        return 1
    args.output.mkdir(parents=True,exist_ok=True)
    for filename,content in results.items():
        (args.output/filename).write_text(content,encoding='utf-8')
        print('Exported:',args.output/filename)
    return 0

if __name__=='__main__':sys.exit(main())
