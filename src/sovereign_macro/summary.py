"""Presentation of evaluated, already redacted results; never scores or fills data."""
import html
import math

METRICS=('iso3','name','baseline_rank','baseline','currency','yield_5y','real_yield',
         'net_debt_current','net_debt_future','balance_trajectory','fx_vol_1y','fx_drawdown',
         'fiscal_trend','real_yield_regime','fx_risk','carry','discount_rate')


def build_executive_summary(result):
    q=result['quality'];rows=result['rows'];demo=q.get('demo',False)
    mode=('SYNTHETIC DEMO' if demo else 'FULL COMPARISON' if q['safe_to_use'] else
          'PARTIAL BASELINE' if q['baseline_usable']>0 else 'DATA HOLD')
    ranking=[] if demo else sorted(
        [r for r in rows if r.get('usable_baseline') is True and r.get('baseline_rank') is not None],
        key=lambda r:r['baseline_rank'])
    metrics=[{k:r.get(k) for k in METRICS} for r in ranking]
    system=list(q.get('system_errors',[]));holds=[]
    for r in rows:
        reasons=list(r.get('errors',[]))
        if not demo and r in ranking:
            reasons=[e for e in reasons if e!='MARKET_QUALITY_UNAVAILABLE']
        reasons.extend(e for e in system if e.startswith(r['iso3']+':'))
        if not demo and r.get('usable_baseline') and r.get('baseline_rank') is None:
            reasons.append('BASELINE_RANK_UNAVAILABLE')
        if not reasons:
            if not demo and r in ranking: continue
            reasons.append('BASELINE_UNAVAILABLE')
        holds.append(dict(iso3=r['iso3'],name=r.get('name',r['iso3']),reasons=list(dict.fromkeys(reasons))))
    adjusted=not demo and q.get('safe_to_use_adjusted',False)
    decision={'PARTIAL BASELINE':'AVAILABLE' if ranking else 'DATA_HOLD',
              'FULL COMPARISON':'AVAILABLE' if q['safe_to_use'] else 'DATA_HOLD',
              'ADJUSTED MODEL':'AVAILABLE' if adjusted else 'DATA_HOLD'}
    if demo: decision={k:'SYNTHETIC DEMO' for k in decision}
    coverage=result.get('coverage',{})
    return dict(global_status=q['status'],safe_to_use=q['safe_to_use'],usage_mode=mode,
                demo=demo,public_output=q.get('public_output',False),as_of=result['as_of'],
                model_version=result['model_version'],coverage=dict(
                    universe=q.get('country_count',len(rows)),baseline_usable=q['baseline_usable'],
                    adjusted_usable=q.get('adjusted_usable',0),
                    yield5_routes_registered=coverage.get('yield5_routes_registered'),
                    yield5_observations_parsed=None if demo else coverage.get('yield5_observations_parsed')),
                baseline_ranking=metrics,top_country_metrics=metrics,holds=holds,
                system_holds=[e for e in system if not any(e.startswith(r['iso3']+':') for r in rows)],
                adjusted_status='AVAILABLE' if adjusted else 'NOT AVAILABLE',decision=decision)


def value(v):
    if v is None or (isinstance(v,float) and not math.isfinite(v)): return '—'
    return f'{v:.3f}' if isinstance(v,float) else str(v)


def sections(s):
    """One ordered content contract shared by all three renderers."""
    c=s['coverage'];n=c['universe'];metric=s['top_country_metrics']
    coverage=[['Universe',str(n)+' countries'],
              ['5Y routes registered', 'UNKNOWN' if c['yield5_routes_registered'] is None else str(c['yield5_routes_registered'])],
              ['5Y observations parsed','UNKNOWN' if c['yield5_observations_parsed'] is None else str(c['yield5_observations_parsed'])],
              ['Baseline usable',f"{c['baseline_usable']} / {n}"],
              ['Adjusted usable',f"{c['adjusted_usable']} / {n}"]]
    ranking=[[r['baseline_rank'],r['name']+' ('+r['iso3']+')',r['baseline']] for r in s['baseline_ranking']]
    holds=[[r['name']+' ('+r['iso3']+')','; '.join(r['reasons'])] for r in s['holds']]
    holds += [['GLOBAL',e] for e in s['system_holds']]
    if s['adjusted_status']!='AVAILABLE': holds.append(['Adjusted ranking','NOT AVAILABLE; MARKET_QUALITY_UNAVAILABLE'])
    macro_keys=['iso3','currency','yield_5y','real_yield','net_debt_current','net_debt_future','balance_trajectory','fiscal_trend','real_yield_regime']
    krw_keys=['iso3','fx_vol_1y','fx_drawdown','fx_risk','carry','discount_rate']
    return [
        ('Executive Summary',['Field','Value'],[['Model',s['model_version']],['As-of',s['as_of']],
            ['GLOBAL STATUS',s['global_status']],['SAFE_TO_USE',str(s['safe_to_use']).upper()],['USAGE MODE',s['usage_mode']]]),
        ('Data Coverage',['Field','Value'],coverage),
        ('Baseline Partial Ranking',['Rank','Country','Baseline'],ranking),
        ('Data / Quality Holds',['Country / Scope','Reason'],holds),
        ('Top Country Metrics',macro_keys,[[r.get(k) for k in macro_keys] for r in metric]),
        ('KRW Investor View',krw_keys,[[r.get(k) for k in krw_keys] for r in metric]),
        ('Decision',['Data use','Status'],list(map(list,s['decision'].items())))
    ]


def notice(s):
    if s['demo']: return 'SYNTHETIC DEMO — 실제 자료 및 실사용 랭킹이 아닙니다.'
    return ('전체 판정과 부분 Baseline을 구분하세요. 부분 순위는 현재 사용 가능한 국가 내 비교입니다. '
            '관측·정의·단위·최신성 검증을 통과한 값만 사용하며, 결측은 —입니다. '
            '실질금리는 기존 yield_5y−inflation_mean 계산값입니다. FX 변동성과 drawdown은 KRW 기준 소수 비율입니다. '
            '순부채는 GDP 대비 %, 수지 변화는 %p입니다. 숫자와 분류는 기존 계산 결과이며 매매 추천이 아닙니다.')


def render_summary_text(s):
    lines=['Global Bond · Sovereign Macro Screener']
    for title,headers,rows in sections(s):
        lines += ['',title]
        if rows:
            lines.append(' | '.join(headers))
            lines.extend(' | '.join(value(v) for v in row) for row in rows)
        else: lines.append('SYNTHETIC DEMO' if s['demo'] else 'NOT AVAILABLE')
    return '\n'.join(lines+['',notice(s)])


def render_summary_markdown(s):
    esc=lambda v:html.escape(value(v)).replace('|','\\|').replace('\n',' ')
    lines=['# Global Bond · Sovereign Macro Screener']
    for title,headers,rows in sections(s):
        lines += ['', '## '+title,'']
        if rows:
            lines += ['| '+' | '.join(map(esc,headers))+' |','| '+' | '.join(['---']*len(headers))+' |']
            lines.extend('| '+' | '.join(map(esc,row))+' |' for row in rows)
        else: lines.append('SYNTHETIC DEMO' if s['demo'] else 'NOT AVAILABLE')
    return '\n'.join(lines+['',notice(s)])+'\n'


def render_summary_html(s):
    esc=lambda v:html.escape(value(v),quote=True)
    blocks=['<section id="executive-summary"><h2>Executive Summary</h2>']
    for title,headers,rows in sections(s):
        blocks.append('<h3>'+esc(title)+'</h3>')
        if rows:
            blocks.append('<div class="scroll"><table><thead><tr>'+''.join('<th>'+esc(v)+'</th>' for v in headers)+'</tr></thead><tbody>')
            blocks.extend('<tr>'+''.join('<td>'+esc(v)+'</td>' for v in row)+'</tr>' for row in rows)
            blocks.append('</tbody></table></div>')
        else: blocks.append('<p>'+('SYNTHETIC DEMO' if s['demo'] else 'NOT AVAILABLE')+'</p>')
    return ''.join(blocks)+'<p>'+esc(notice(s))+'</p></section>'
