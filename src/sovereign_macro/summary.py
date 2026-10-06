"""Presentation of evaluated, already redacted results; never scores or fills data."""
import html
import math
from .models import finite

METRICS=('iso3','name','baseline_rank','baseline','currency','yield_5y','real_yield',
         'yield_5y_provider','yield_5y_date','yield_5y_age_days','yield_5y_fallback',
         'net_debt_current','net_debt_future','balance_trajectory','fx_vol_1y','fx_drawdown',
         'fiscal_trend','real_yield_regime','fx_risk','carry','discount_rate',
         'yield_type','baseline_definition_note')


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
                quality_scopes=quality_scopes(rows,demo),
                market_inputs=[dict(iso3=r['iso3'],**r['market_inputs']) for r in rows if r.get('market_inputs')],
                system_holds=[e for e in system if not any(e.startswith(r['iso3']+':') for r in rows)],
                adjusted_status='AVAILABLE' if adjusted else 'NOT AVAILABLE',decision=decision,
                source_notices=result.get('source_notices',[]),
                fiscal_source=result.get('fiscal_source',{}),
                yield_sources=[dict(iso3=r['iso3'],name=r.get('name',r['iso3']),
                    provider=r.get('yield_5y_provider'),observation_date=r.get('yield_5y_date'),
                    age_days=r.get('yield_5y_age_days'),fallback=r.get('yield_5y_fallback',False),
                    definition=r.get('yield_type',''),definition_note=r.get('baseline_definition_note',''),
                    selection_reason=r.get('yield_5y_selection_reason',''),warnings=r.get('warnings',[])) for r in rows])


def quality_scopes(rows,demo=False):
    """Summarize displayed inputs independently of the global readiness gate."""
    checks=[
        ('BASELINE',lambda r:r.get('usable_baseline') is True and r.get('baseline_rank') is not None),
        ('REAL_YIELD',lambda r:finite(r.get('real_yield'))),
        ('FX_1Y',lambda r:finite(r.get('fx_vol_1y'))),
        ('MARKET_QUALITY',lambda r:finite(r.get('market_quality_norm'))),
        ('ADJUSTED',lambda r:r.get('usable_adjusted') is True and r.get('adjusted_rank') is not None),
    ]
    result=[]
    for scope,check in checks:
        available=[r['iso3'] for r in rows if check(r) and not demo]
        missing=[] if demo else [r['iso3'] for r in rows if r['iso3'] not in available]
        status=('SYNTHETIC DEMO' if demo else 'AVAILABLE' if not missing else
                'PARTIAL' if available else 'UNAVAILABLE')
        result.append(dict(scope=scope,status=status,available=len(available),total=len(rows),
                           unavailable_countries=missing))
    return result


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
    krw_keys=['iso3','yield_5y','real_yield','fx_vol_1y','fx_drawdown','fx_risk','carry','discount_rate']
    content=[
        ('Executive Summary',['Field','Value'],[['Model',s['model_version']],['As-of',s['as_of']],
            ['USAGE MODE',s['usage_mode']],['GLOBAL STATUS',s['global_status']],['SAFE_TO_USE',str(s['safe_to_use']).upper()]]),
        ('Data Coverage',['Field','Value'],coverage),
        ('Quality by Scope',['Scope','Status','Available','Unavailable countries'],
            [[r['scope'],r['status'],str(r['available'])+' / '+str(r['total']),
              ', '.join(r['unavailable_countries']) or '—'] for r in s['quality_scopes']]),
        ('Baseline Partial Ranking',['Rank','Country','Baseline'],ranking),
        ('Data / Quality Holds',['Country / Scope','Reason'],holds),
        ('Top Country Metrics',macro_keys,[[r.get(k) for k in macro_keys] for r in metric]),
        ('KRW Investor View',krw_keys,[[r.get(k) for k in krw_keys] for r in metric]),
    ]
    if s.get('yield_sources'):
        content.append(('Yield Sources / Observation Dates',
            ['Country','5Y provider','Observation date','Age (calendar days)','WGB fallback','Definition','Selection / warnings'],
            [[r['iso3'],r['provider'],r['observation_date'],r['age_days'],r['fallback'],
              '; '.join([r['definition'],r['definition_note']]).strip('; '),
              '; '.join([r['selection_reason']]+r['warnings']).strip('; ')] for r in s['yield_sources']]))
    if s.get('fiscal_source'):
        f=s['fiscal_source']
        content.append(('IMF Fiscal / Inflation Edition',['Field','Value'],[
            ['Edition',f.get('edition')],['Saved snapshot used',f.get('used',False)],
            ['Original retrieval (UTC)',f.get('original_retrieved_at')],
            ['Retrieval age (calendar days)',f.get('age_days')],
            ['Latest release checked successfully',f.get('latest_release_verified')],
            ['Refresh failure',f.get('refresh_failure','')]]))
    if s.get('market_inputs'):
        content.append(('Market Quality Input Gaps',['Scope','Reason'],[
            [axis,'; '.join(dict.fromkeys(r[axis].get('reason','') for r in s['market_inputs']))]
            for axis in ('liquidity','credit','accessibility')]))
        content.append(('Market Quality Inputs',
            ['Country','Size (USD bn)','Period / scope','Size status / reason','Liquidity','Credit','Accessibility','Composite'],
            [[r['iso3'],r['size'].get('value'),
              '; '.join([r['size'].get('period',''),r['size'].get('definition','')]).strip('; '),
              '; '.join([r['size']['status'],r['size'].get('reason','')]).strip('; '),
              r['liquidity']['status'],r['credit']['status'],r['accessibility']['status'],r['composite_status']]
             for r in s['market_inputs']]))
        content.append(('Reported Credit Ratings',
            ['Country','Agency','Reported rating','Outlook','Rating kind','Assessment / action date','Date basis','Status / reason','Source'],
            [[r['iso3'],r['credit'].get('agency'),r['credit'].get('rating'),r['credit'].get('outlook'),
              r['credit'].get('rating_kind','unverified'),
              r['credit'].get('assessment_date') or r['credit'].get('last_action_date'),
              r['credit'].get('assessment_date_type') or r['credit'].get('date_type','unverified'),
              '; '.join(filter(None,[r['credit']['status'],r['credit'].get('reason',''),
                  r['credit'].get('basis_verification_error',''),r['credit'].get('issuer_failure',{}).get('reason','')])).strip('; '),
              r['credit'].get('url')] for r in s['market_inputs']]))
        content.append(('Source-specific Liquidity Diagnostics — not a cross-country score',
            ['Country','Provider','Value','Unit','Period / observation date','Status / limitation','Source'],
            [[r['iso3'],r['liquidity'].get('provider'),r['liquidity'].get('value'),
              r['liquidity'].get('unit'),
              '; '.join([r['liquidity'].get('period',''),r['liquidity'].get('observation_date','')]).strip('; '),
              '; '.join([r['liquidity']['status'],r['liquidity'].get('definition',''),
                         r['liquidity'].get('reason','')]).strip('; '),r['liquidity'].get('url')]
             for r in s['market_inputs']]))
        turnover=[r for r in s['market_inputs'] if r.get('turnover',{}).get('provider')=='adb']
        if turnover:
            content.append(('ADB Government Bond Turnover — diagnostics only',
                ['Country','Ratio (turns / quarter)','Period / observation date','Traded value (LCY bn)',
                 'Average outstanding (LCY bn)','Status / scope','Source'],
                [[r['iso3'],f"{r['turnover']['value']:.2f}" if r['turnover'].get('value') is not None else None,
                  '; '.join([r['turnover'].get('period',''),r['turnover'].get('observation_date','')]).strip('; '),
                  r['turnover'].get('traded_value'),r['turnover'].get('average_outstanding'),
                  '; '.join([r['turnover']['status'],r['turnover'].get('definition',''),
                             r['turnover'].get('reason','')]).strip('; '),r['turnover'].get('url')]
                 for r in turnover]))
        candidates={}
        for row in s['market_inputs']:
            for axis in ('liquidity','accessibility','credit'):
                for source in row[axis].get('candidate_sources',[]):
                    key=(axis,source['url'])
                    if key not in candidates: candidates[key]=dict(source,axis=axis,countries=[])
                    candidates[key]['countries'].append(row['iso3'])
        if candidates:
            content.append(('Market Quality Research Links — candidates only',
                ['Scope','Countries to review','Provider','Definition','Outstanding limitation','Source'],
                [[r['axis'],', '.join(r['countries']),r['provider'],r['scope'],r['limitation'],r['url']]
                 for r in candidates.values()]))
    if s.get('source_notices'):
        content.append(('Source / Reuse Notices',['Attribution and conditions'],[[n] for n in s['source_notices']]))
    content.append(('Decision',['Data use','Status'],list(map(list,s['decision'].items()))))
    return content


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
