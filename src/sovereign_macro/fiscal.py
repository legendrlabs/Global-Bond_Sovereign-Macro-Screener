"""IMF vintage contracts and a same-edition net-debt PDF fallback."""
import re
from io import BytesIO
from pypdf import PdfReader
from .models import DataError, finite

METRICS={'net_debt':'GGXWDN_G01_GDP_PT','overall_balance':'GGXCNL_G01_GDP_PT',
         'gross_debt':'G_XWDG_G01_GDP_PT','inflation':'PCPIPCH'}

def parse_fiscal(metadata,payloads,as_of_year):
    editions=[]
    starts=[]
    values={}
    for metric,key in METRICS.items():
        source=metadata.get(key,{}).get('source','')
        match=re.search(r'\((April|October) (\d{4})\)',source)
        if not match: raise DataError('FISCAL_EDITION_UNVERIFIED')
        if metric!='inflation' and 'Fiscal Monitor' not in source:
            raise DataError('FISCAL_DATASET_MISMATCH')
        if metric=='inflation' and 'World Economic Outlook' not in source:
            raise DataError('INFLATION_DATASET_MISMATCH')
        editions.append(' '.join(match.groups()))
        start=metadata[key].get('projection-year')
        if not isinstance(start,int): raise DataError('FORECAST_START_UNVERIFIED')
        starts.append(start)
        expected_unit='Annual percent change' if metric=='inflation' else '% of GDP'
        if metadata[key].get('unit')!=expected_unit: raise DataError('FISCAL_UNIT_MISMATCH')
        raw=payloads[key].get('values',{}).get(key,{})
        values[metric]={iso:{int(y):v for y,v in row.items() if str(y).isdigit() and finite(v)}
                        for iso,row in raw.items() if len(iso)==3 and iso.isupper()}
    if len(set(starts))!=1: raise DataError('MIXED_FORECAST_STARTS')
    if len(set(editions))!=1: raise DataError('MIXED_FISCAL_VINTAGES')
    years=[y for row in values['overall_balance'].values() for y in row if y>=as_of_year]
    if not years or max(years)<as_of_year+5: raise DataError('FORECAST_HORIZON_UNAVAILABLE')
    return {'edition':editions[0],'values':values,'horizon_start':starts[0],'horizon_end':max(years),
            'cpi_years':list(range(as_of_year+1,as_of_year+6)),'pdf_fills':[]}

def parse_net_debt_pdf(text,countries):
    if 'Table A8.' not in text: raise DataError('PDF_TABLE_MISMATCH')
    year_rows=[[int(y) for y in re.findall(r'\b(?:19|20)\d{2}\b',line)] for line in text.splitlines()]
    candidates=[ys for ys in year_rows if len(ys)==15 and ys==list(range(ys[0],ys[0]+15))]
    if len(candidates)!=1: raise DataError('PDF_YEAR_COLUMNS')
    years=candidates[0]
    result={}
    for country in countries:
        label=country['pdf_label']
        pattern=r'^\s*'+re.escape(label)+r'\d*\s+'
        lines=[line for line in text.splitlines() if re.match(pattern,line)]
        if len(lines)!=1: continue
        tokens=re.sub(pattern,'',lines[0]).split()
        if len(tokens)!=15: raise DataError('PDF_COLUMN_COUNT:'+country['iso3'])
        row={}
        for y,token in zip(years,tokens):
            if token in ('...','…','—','–','-'): continue
            try: value=float(token.replace(',','').replace('–','-').replace('−','-'))
            except ValueError as exc: raise DataError('PDF_NUMERIC_TOKEN') from exc
            if not finite(value): raise DataError('PDF_NONFINITE')
            row[y]=value
        result[country['iso3']]=row
    return result

def merge_pdf(api, pdf):
    overlap=0
    for iso,row in pdf.items():
        for year,value in row.items():
            existing=api.get(iso,{}).get(year)
            if existing is not None:
                overlap+=1
                if abs(existing-value)>.051: raise DataError('PDF_API_MISMATCH')
    if not overlap: raise DataError('PDF_NO_COMPARABLE_OVERLAP')
    fills=[]
    for iso,row in pdf.items():
        for year,value in row.items():
            if year not in api.get(iso,{}):
                api.setdefault(iso,{})[year]=value
                fills.append({'iso3':iso,'year':year})
    return fills

def validate_pdf_edition(text,edition):
    pattern=r'\s+'.join(re.escape(part) for part in edition.split())
    if not re.search(pattern,text,re.IGNORECASE): raise DataError('PDF_EDITION_MISMATCH')


def collect_fiscal(client,config,countries,as_of):
    base=config['api']
    metadata=client.fetch(base+'indicators').json()['indicators']
    payloads={}
    provenance={}
    for metric,key in METRICS.items():
        p=client.fetch(base+key)
        payloads[key]=p.json()
        provenance[metric]={'url':p.url,'raw_sha256':p.sha256,'retrieved_at':p.retrieved_at,
                            'source_date':p.source_date,'series':key,'metadata':metadata[key],'redistribution':config['redistribution']}
    data=parse_fiscal(metadata,payloads,as_of.year)
    data['provenance']=provenance
    data['errors']=[]
    pdf_config=config.get('pdf_editions',{}).get(data['edition'])
    if pdf_config and any(not data['values']['net_debt'].get(c['iso3']) for c in countries):
        try:
            p=client.fetch(pdf_config['url'])
            text=PdfReader(BytesIO(p.body)).pages[pdf_config['page']-1].extract_text(extraction_mode='layout')
            validate_pdf_edition(text,data['edition'])
            pdf=parse_net_debt_pdf(text,countries)
            fills=merge_pdf(data['values']['net_debt'],pdf)
            data['pdf_fills']=fills
            data['pdf_provenance']={'url':p.url,'raw_sha256':p.sha256,'retrieved_at':p.retrieved_at,
                                   'edition':data['edition'],'table':pdf_config['table'],'page':pdf_config['page'],
                                   'precision':0.1,'redistribution':config['redistribution']}
        except (DataError,ValueError,IndexError) as exc:
            data['errors'].append('PDF_FALLBACK_FAILED:'+str(exc))
    return data
