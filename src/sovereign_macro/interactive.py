"""Ask separately before changing installed code or refreshing provider data."""
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import re
import sys
import webbrowser
from . import __version__, updates
from .summary import render_summary_text

@dataclass(frozen=True)
class DataState:
    report: Path | None
    due: bool
    summary: str

def confirm(question,*,interactive=None,input_fn=None):
    if interactive is None: interactive=sys.stdin.isatty() and sys.stdout.isatty()
    if not interactive: return False
    try:
        answer=(input_fn or input)(question+' [y/N]: ').strip().lower()
        return answer in ('y','yes','예','네','ㅇ','ㅇㅇ')
    except (EOFError,KeyboardInterrupt): return False

def data_state(output,as_of,public_output,now=None):
    now=now or datetime.now(timezone.utc)
    root=Path(output)
    try:
        pointer=json.loads((root/'current.json').read_text(encoding='utf-8'))
        relative=pointer['path']
        if not isinstance(relative,str) or not re.fullmatch(r'runs/[A-Za-z0-9_-]+',relative): raise ValueError()
        dest=root/relative
        dest.resolve().relative_to((root/'runs').resolve())
        quality=json.loads((dest/'quality.json').read_text(encoding='utf-8'))
        if quality.get('public_output') is not public_output or quality.get('demo') is not False:
            return DataState(None,True,'현재 실행 모드에 맞는 실제 자료 보고서가 없습니다.')
        report=dest/'index.html'
        if not report.is_file(): raise ValueError()
        generated=datetime.fromisoformat(pointer['generated_at'])
        if generated.tzinfo is None or generated>now+timedelta(minutes=5): raise ValueError()
        due=pointer['as_of']!=as_of.isoformat() or now-generated>=timedelta(hours=24)
        summary=f"마지막 수집 {pointer['generated_at']} · 기준일 {pointer['as_of']} · {quality.get('status','UNKNOWN')} · Baseline {quality.get('baseline_usable',0)}/27"
        return DataState(report,due,summary)
    except (OSError,ValueError,TypeError,KeyError,AttributeError):
        return DataState(None,True,'저장된 실제 자료 보고서를 확인할 수 없습니다.')

def run_app(output,as_of,public_output,run_data,*,interactive=None,input_fn=None,open_browser=True):
    if interactive is None: interactive=sys.stdin.isatty() and sys.stdout.isatty()
    state=data_state(output,as_of,public_output)
    print(f'프로그램 {__version__} · '+state.summary)
    def show_saved_summary():
        if not state.report: return
        try:
            saved=json.loads((state.report.parent/'executive_summary.json').read_text(encoding='utf-8'))
            if saved.get('public_output') is public_output and saved.get('demo') is False:
                print(render_summary_text(saved))
        except (OSError,ValueError,TypeError,KeyError,AttributeError): pass
    if not interactive:
        show_saved_summary()
        print('대화형 입력이 없어 프로그램 설치와 자료 갱신을 건너뜁니다. 자동 수집은 run 명령을 사용하세요.')
        return 0
    print('새 프로그램 버전을 확인합니다…')
    try:
        release=updates.latest_release()
        if release and confirm(f'새 버전 {release.version}이 있습니다. 프로그램을 업데이트할까요?',interactive=True,input_fn=input_fn):
            print('프로그램 다운로드·검증·설치를 진행합니다…')
            try: updates.install_release(release)
            except updates.UpdateError as exc:
                print(str(exc));return 2
            print('프로그램 설치가 끝났습니다. 새 버전으로 다시 실행해 주세요.')
            return 0
        if not release: print('공개된 새 안정 버전이 없습니다.')
    except updates.UpdateError as exc: print(str(exc))
    report=state.report;status=0;refreshed=False
    if state.due:
        if confirm('국채·거시 자료를 새로 수집할까요?',interactive=True,input_fn=input_fn):
            print('자료 수집을 시작합니다. 공급자별 요청은 시간이 걸릴 수 있습니다…')
            try:
                destination,status=run_data();report=destination/'index.html';refreshed=True
                print('자료 갱신 실행이 끝났습니다. 원자료 품질과 부분 순위는 새 보고서에서 확인하세요.')
            except Exception as exc:
                print(f'자료 갱신 실행 실패: {type(exc).__name__}. 기존 결과는 새 자료로 취급하지 않습니다.')
                status=2
        else: print('자료를 갱신하지 않았습니다. 저장된 결과의 수집 시점과 기준일을 확인하세요.')
    if not refreshed: show_saved_summary()
    if report:
        print('보고서: '+str(report.resolve()))
        if open_browser: webbrowser.open(report.resolve().as_uri())
    else: print('열 수 있는 보고서가 없습니다. 다음 실행에서 자료 수집을 승인해 주세요.')
    return status
