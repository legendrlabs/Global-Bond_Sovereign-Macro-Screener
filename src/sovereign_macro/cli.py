import argparse
from datetime import datetime, date
from zoneinfo import ZoneInfo
from .config import load_config
from .http import HttpClient
from .collect import collect
from .pipeline import evaluate, demo_bundle
from .report import publish
from .summary import build_executive_summary, render_summary_text
from .interactive import run_app

def main(argv=None):
    parser=argparse.ArgumentParser(description='Keyless sovereign-macro research pipeline')
    parser.add_argument('command',choices=['run','demo','app'],nargs='?',default='app')
    parser.add_argument('--output',default='results')
    parser.add_argument('--cache',default='data/cache')
    parser.add_argument('--config',help='Directory containing the three YAML contracts')
    parser.add_argument('--as-of',type=date.fromisoformat,default=datetime.now(ZoneInfo('Asia/Seoul')).date())
    parser.add_argument('--public-output',action='store_true',help='Suppress numbers with pending redistribution rights')
    parser.add_argument('--require-complete',action='store_true',help='Exit 2 on DATA_HOLD after writing diagnostics')
    parser.add_argument('--no-open',action='store_true',help='Do not open the report browser in app mode')
    args=parser.parse_args(argv)
    if args.command=='app':
        def refresh():
            return run_pipeline(args,False)
        return run_app(args.output,args.as_of,args.public_output,refresh,open_browser=not args.no_open)
    return run_pipeline(args,args.command=='demo')[1]

def run_pipeline(args,synthetic):
    config=load_config(args.config)
    bundle=demo_bundle(config,args.as_of) if synthetic else collect(config,HttpClient(args.cache),args.as_of)
    result=evaluate(config,bundle,args.as_of,public_output=args.public_output,demo=synthetic)
    destination=publish(result,args.output)
    q=result['quality']
    print(render_summary_text(build_executive_summary(result)))
    print(f'Report: {destination / "index.html"}')
    print(f'Current pointer: {args.output}/current.json')
    return destination,2 if args.require_complete and not q['safe_to_use'] else 0
