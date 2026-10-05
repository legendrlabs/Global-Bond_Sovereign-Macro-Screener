"""Immutable run directories plus an atomic current pointer; no cached-success fallback."""
import csv
from datetime import datetime, timezone
import hashlib
import html
import json
import os
from pathlib import Path
import tempfile
import uuid
from .summary import build_executive_summary, render_summary_markdown, render_summary_html

SCORE_FIELDS=['iso3','name','currency','baseline','baseline_rank','adjusted','adjusted_rank','usable_baseline','usable_adjusted','redistribution_status']
REGIME_FIELDS=['iso3','name','fiscal_trend','balance_trajectory','real_yield_regime','fx_risk','carry','discount_rate']

def dump(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')

def write_csv(path,rows,fields):
    with path.open('w',encoding='utf-8-sig',newline='') as file:
        writer=csv.DictWriter(file,fields,extrasaction='ignore')
        writer.writeheader()
        for row in rows:
            writer.writerow({k:json.dumps(row.get(k),ensure_ascii=False) if isinstance(row.get(k),(list,dict)) else row.get(k) for k in fields})

def format_value(value):
    return '—' if value is None else f'{value:.3f}' if isinstance(value,float) else str(value)

def build_html(result,run_id):
    esc=lambda x:html.escape(str(x),quote=True)
    rows=result['rows'];quality=result['quality']
    body=[]
    for r in rows:
        source=r.get('yield_5y_provider','—')+(' · 보완' if r.get('yield_5y_fallback') else '')
        observed=r.get('yield_5y_date','—')
        if r.get('yield_5y_age_days') is not None: observed+=f" · {r['yield_5y_age_days']}일 전"
        fields=[r['name']+' · '+r['iso3'],r['currency'],r['yield_5y'],source,observed,r['baseline'],r['baseline_rank'],r['adjusted'],r['fx_vol_1y'],r['carry'],r['redistribution_status']]
        cells=''.join('<td>'+esc(format_value(v))+'</td>' for v in fields)
        details=esc(json.dumps({'errors':r['errors'],'warnings':r.get('warnings',[]),'provenance':r['provenance']},ensure_ascii=False,indent=2))
        body.append('<tr>'+cells+'<td><details><summary>근거·상태</summary><pre>'+details+'</pre></details></td></tr>')
    title='SYNTHETIC DEMO' if quality['demo'] else quality['status']
    return '''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sovereign Macro Screener</title>
<style>:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#0c1421;color:#edf2f8;font:15px system-ui,sans-serif}main{max-width:1500px;margin:auto;padding:40px 24px}h1{font-size:32px;margin:12px 0}p{color:#aabbd0;line-height:1.7}.eyebrow{letter-spacing:.15em;color:#79e3b0;font-size:12px}.badge{display:inline-block;border:1px solid #ba8b32;color:#ffd07d;border-radius:20px;padding:7px 14px}.cards{display:flex;gap:16px;flex-wrap:wrap;margin:24px 0}.card{background:#172235;border:1px solid #2b3b50;border-radius:12px;padding:18px;min-width:180px}.card strong{font-size:28px;display:block}.card span{color:#aabbd0}input{background:#172235;border:1px solid #3b4b60;border-radius:8px;color:white;padding:12px;width:min(100%,380px);margin:10px 0 20px}.scroll{overflow:auto;border:1px solid #2b3b50;border-radius:12px}#executive-summary table{min-width:0}#executive-summary h3{margin-top:28px}table{border-collapse:collapse;width:100%;min-width:1100px}th,td{padding:14px 12px;text-align:left;border-bottom:1px solid #2b3b50}th{color:#8eabc9;background:#172235;font-size:12px;white-space:nowrap}td{font-size:13px}pre{white-space:pre-wrap;min-width:300px;max-width:600px;font-size:11px}summary{cursor:pointer;color:#79e3b0}a{color:#8abfff}footer{margin-top:24px;color:#aabbd0;font-size:12px}</style><main><div class="eyebrow">GLOBAL BOND / SOVEREIGN MACRO</div><h1>국채·거시 스크리너</h1><span class="badge">'''+esc(title)+'''</span><p>기준일 '''+esc(result['as_of'])+''' · 결측은 —로 표시합니다. 부분 수집 결과와 발행판·만기·관측일을 함께 확인하세요.<br>Adjusted는 Market Quality 검증 전까지 산출하지 않습니다. 공개 모드에서 재배포 조건 미확인 자료의 수치와 파생 분류를 숨깁니다.</p><div class="cards"><div class="card"><strong>'''+str(len(rows))+'''</strong><span>대상 국가</span></div><div class="card"><strong>'''+str(quality['baseline_usable'])+''' / '''+str(len(rows))+'''</strong><span>Baseline 사용 가능</span></div><div class="card"><strong>'''+str(quality['adjusted_usable'])+''' / '''+str(len(rows))+'''</strong><span>Adjusted 사용 가능</span></div><div class="card"><strong>'''+('가능' if quality['safe_to_use'] else '보류')+'''</strong><span>전체 데이터 사용 상태</span></div></div>'''+render_summary_html(build_executive_summary(result))+'''<label for="search">국가 / 통화 / 상태 검색</label><br><input id="search" placeholder="예: 한국, CAN, EUR"><div class="scroll"><table><thead><tr>'''+''.join('<th>'+x+'</th>' for x in ['국가','통화','5Y %','출처','관측일','Baseline','순위','Adjusted','FX 변동성','Carry','재배포','상세'])+'''</tr></thead><tbody id="country-rows">'''+''.join(body)+'''</tbody></table></div><p><a href="latest.md">요약</a> · <a href="sovereign_scores.csv">점수 CSV</a> · <a href="country_details.csv">국가 상세 CSV</a> · <a href="quality.json">품질 상태</a> · <a href="run_manifest.json">실행 근거</a></p><footer>모델 '''+esc(result['model_version'])+''' · 실행 '''+esc(run_id)+'''<br>연구용 비교 결과이며 거래를 실행하지 않습니다.</footer></main><script>document.getElementById('search').addEventListener('input',function(){const q=this.value.toLowerCase();document.querySelectorAll('#country-rows tr').forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(q));});</script></html>'''

def atomic_json(path,value):
    temp=path.with_name(path.name+'.tmp-'+uuid.uuid4().hex)
    try:
        dump(temp,value)
        os.replace(temp,path)
    finally:
        temp.unlink(missing_ok=True)

def publish(result,output):
    root=Path(output);root.mkdir(parents=True,exist_ok=True)
    runs=root/'runs';runs.mkdir(exist_ok=True)
    now=datetime.now(timezone.utc).isoformat()
    run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8]
    quality={**result['quality'],'run_id':run_id,'as_of':result['as_of'],'generated_at':now}
    with tempfile.TemporaryDirectory(prefix='.staging-',dir=root) as tmp:
        stage=Path(tmp)
        scored=[dict(r,run_id=run_id,as_of=result['as_of']) for r in result['rows']]
        write_csv(stage/'sovereign_scores.csv',scored,['run_id','as_of']+SCORE_FIELDS)
        write_csv(stage/'country_details.csv',scored,['run_id','as_of']+sorted(set().union(*(r.keys() for r in result['rows']))))
        write_csv(stage/'macro_regime.csv',scored,['run_id','as_of']+REGIME_FIELDS)
        dump(stage/'quality.json',quality)
        executive=build_executive_summary(result)
        dump(stage/'executive_summary.json',executive)
        summary=['## Full Diagnostic Table','',f'실행: {run_id}','','| 국가 | Baseline | 순위 | 상태 |','|---|---:|---:|---|']
        for r in scored:
            summary.append(f"| {r['name']} ({r['iso3']}) | {format_value(r['baseline'])} | {format_value(r['baseline_rank'])} | {', '.join(r['errors'])} |")
        (stage/'latest.md').write_text(render_summary_markdown(executive)+'\n'+'\n'.join(summary)+'\n',encoding='utf8')
        (stage/'index.html').write_text(build_html(result,run_id),encoding='utf8')
        hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in stage.iterdir()}
        manifest={'run_id':run_id,'as_of':result['as_of'],'generated_at':now,'model_version':result['model_version'],
                  'demo':quality['demo'],'public_output':quality['public_output'],'files':hashes,
                  'http_records':result.get('http_records',[]),'source_provenance':{r['iso3']:r['provenance'] for r in scored}}
        dump(stage/'run_manifest.json',manifest)
        destination=runs/run_id
        os.replace(stage,destination)
    pointer={'run_id':run_id,'path':'runs/'+run_id,'as_of':result['as_of'],'generated_at':now,'status':quality['status']}
    # Consumers use current.json, never combine files from mutable convenience paths.
    if quality['safe_to_use']: atomic_json(root/'last_success.json',pointer)
    atomic_json(root/'current.json',pointer)
    return destination
