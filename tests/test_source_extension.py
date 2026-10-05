"""Synthetic fixtures: catch wrong maturity, scale and observation frequency."""
import unittest
from datetime import datetime, date
from io import BytesIO
import openpyxl
from sovereign_macro import sources
from sovereign_macro.models import DataError


def workbook(sheet, rows, percent_cells=()):
    w=openpyxl.Workbook(); s=w.active; s.title=sheet
    for row in rows: s.append(row)
    for cell in percent_cells: s[cell].number_format='0.00%'
    b=BytesIO(); w.save(b); w.close(); return b.getvalue()


def spain(description='Bonos y obligaciones del Estado no segregados. 5 Años', unit='Porcentaje', freq='DIARIA'):
    return ('"CÓDIGO DE LA SERIE",D_G0B1F0ZE,D_G0B1F0ZO\n'
            '"NÚMERO SECUENCIAL",1,2\n"ALIAS DE LA SERIE",other,TI_1_3.10\n'
            f'"DESCRIPCIÓN DE LA SERIE",Más de 2 años,{description}\n'
            f'"DESCRIPCIÓN DE LAS UNIDADES",Porcentaje,{unit}\n"FRECUENCIA",DIARIA,{freq}\n'
            '"30 SEP 2026",99,3.645\n"01 OCT 2026",99,_\n"02 ENE 2026",99,0\n').encode('cp1252')


def israel(**changes):
    attrs=dict(SERIES_CODE='ZC_TSB_ZND_05Y_MA',FREQ='M',NOMINAL_REAL='N',
               DATA_TYPE='ZC_YTM',TIME_TO_MATURITY='Y05T05',TIME_COLLECT='A',
               DATA_SOURCE='BOI_IS',UNIT_MULT='0',UNIT_MEASURE='PT')
    attrs.update(changes)
    return ('<Data><Series '+ ' '.join(f'{k}="{v}"' for k,v in attrs.items())+
            '><Obs TIME_PERIOD="2026-08" OBS_VALUE="0"/>'
            '<Obs TIME_PERIOD="2026-09" OBS_VALUE="3.716"/>'
            '<Obs TIME_PERIOD="2026-10" OBS_VALUE="4"/></Series></Data>').encode()


class ExtensionTests(unittest.TestCase):
    def parser(self,name):
        parser=getattr(sources,name,None)
        self.assertIsNotNone(parser, name+' is not implemented')
        return parser

    def test_spain_exact_sovereign_five_year_percent_and_missing(self):
        rows=self.parser('parse_spain')(spain(),'D_G0B1F0ZO')
        self.assertEqual(rows,[('2026-09-30',3.645),('2026-01-02',0.)])

    def test_spain_rejects_wrong_maturity_units_frequency_or_sector(self):
        p=self.parser('parse_spain')
        for body in (spain(description='Bonos del Estado. 10 Años'),spain(unit='Basis points'),
                     spain(freq='MENSUAL'),spain(description='Renta fija privada. 5 Años')):
            with self.assertRaises(DataError): p(body,'D_G0B1F0ZO')

    def test_spain_source_notes_footer_is_metadata_not_observation(self):
        self.assertEqual(self.parser('parse_spain')(spain()+b'FUENTE,,\nNOTAS,,\n','D_G0B1F0ZO'),
                         [('2026-09-30',3.645),('2026-01-02',0.)])

    def test_iceland_explanatory_paragraph_does_not_override_correction_column(self):
        b=workbook('FLV',[['corrected calculation explanation','Par-yield, nominal','corrected calculation','Athugasemd'],
          ['Dagsetning (Date)',5,None,None],[datetime(2026,10,1),.0751,'N',None]],['B3'])
        rows,notes=self.parser('parse_iceland')(b)
        self.assertEqual(notes['2026-10-01'],'correction=N')

    def test_slovakia_split_date_zero_missing_and_exact_tenor(self):
        b=workbook('Yields_SK',[['Date',None,None,'Estimated Zero-Coupon Yield Curve'],
          ['YYYY','MM','DD','ZCY1Y','ZCY5Y','ZCY10Y'],[2026,9,25,9,3.86,99],
          [2026,9,28,9,None,99],[2026,9,29,9,0,99]])
        self.assertEqual(self.parser('parse_slovakia')(b,'ZCY5Y'),[('2026-09-25',3.86),('2026-09-29',0.)])

    def test_slovakia_schema_drift_or_percentage_scaling_rejected(self):
        p=self.parser('parse_slovakia')
        for b in (workbook('Wrong',[['YYYY','MM','DD','ZCY5Y'],[2026,9,25,3.86]]),
                  workbook('Yields_SK',[['YYYY','MM','DD','ZCY10Y'],[2026,9,25,3.86]]),
                  workbook('Yields_SK',[['YYYY','MM','DD','ZCY5Y'],[2026,9,25,.0386]],['D2'])):
            with self.assertRaises(DataError): p(b,'ZCY5Y')

    def test_iceland_nominal_par_not_indexed_or_zero_and_correction_note(self):
        b=workbook('FLV',[['Constant Maturity Rates'],
          [None,'Par-yield, inflation indexed',None,'Par-yield, nominal',None,'Zero-coupon yield, nominal','corrected calculation','Athugasemd'],
          ['Dagsetning (Date)',3,5,3,5,5,None,None],
          [datetime(2026,10,1),.03,.04,.08,.0751,.07,'L',2]],['E4'])
        rows,notes=self.parser('parse_iceland')(b)
        self.assertAlmostEqual(rows[0][1],7.51)
        self.assertEqual(rows[0][0],'2026-10-01')
        self.assertIn('L',notes['2026-10-01']);self.assertIn('2',notes['2026-10-01'])

    def test_iceland_missing_percent_format_or_nominal_header_rejected(self):
        p=self.parser('parse_iceland')
        for label,formats in [('Par-yield, nominal',()),('Par-yield, inflation indexed',('B3',))]:
            b=workbook('FLV',[[None,label],['Dagsetning (Date)',5],[datetime(2026,10,1),.0751]],formats)
            with self.assertRaises(DataError): p(b)

    def test_iceland_literal_percent_sign_does_not_authorize_times_hundred(self):
        # Quoted/escaped % is displayed literally; Excel does not scale the value.
        p=self.parser('parse_iceland')
        for number_format in ('0.00"%"',r'0.00\%'):
            b=workbook('FLV',[[None,'Par-yield, nominal'],['Dagsetning (Date)',5],
                             [datetime(2026,10,1),7.51]])
            w=openpyxl.load_workbook(BytesIO(b));w['FLV']['B3'].number_format=number_format
            out=BytesIO();w.save(out);w.close()
            with self.assertRaisesRegex(DataError,'PERCENT_FORMAT'):p(out.getvalue())

    def test_israel_exact_dimensions_and_monthly_period_preserved(self):
        self.assertEqual(self.parser('parse_israel')(israel(),'ZC_TSB_ZND_05Y_MA'),
                         [('2026-08',0.),('2026-09',3.716),('2026-10',4.)])

    def test_israel_rejects_real_wrong_tenor_scale_or_frequency(self):
        p=self.parser('parse_israel')
        for changes in ({'NOMINAL_REAL':'R'},{'TIME_TO_MATURITY':'Y10T10'},
                        {'UNIT_MULT':'2'},{'UNIT_MEASURE':'BP'},{'FREQ':'D'},{'TIME_COLLECT':'E'}):
            with self.assertRaises(DataError): p(israel(**changes),'ZC_TSB_ZND_05Y_MA')

    def test_monthly_selection_no_future_partial_month_or_daily_conversion(self):
        p=self.parser('select_latest_month')
        self.assertEqual(p([('2026-08',0),('2026-09',3.716),('2026-10',4)],date(2026,10,4)),('2026-09',3.716))
        self.assertEqual(p([('2026-08',0),('2026-09',3.716)],date(2026,9,15)),('2026-08',0))
        with self.assertRaises(DataError):p([('2026-08',0),('2026-08',1)],date(2026,10,4))

    def test_collect_four_routes_provenance_and_daily_gate(self):
        from sovereign_macro.config import load_config
        from sovereign_macro.http import Payload
        countries={c['iso3']:c for c in load_config()['countries']['countries']}
        fixtures={
          'https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/ti_1_3.csv':spain(),
          'https://nbs.sk/dokument/b912f986-f5ab-4a02-9033-97976d6dc849/stiahnut?force=false':
            workbook('Yields_SK',[['YYYY','MM','DD','ZCY5Y'],[2026,9,25,3.86]]),
          'https://sedlabanki.is/library?itemid=4b7a7e67-a647-4e98-9190-0c1ca772179f':
            workbook('FLV',[[None,'Par-yield, nominal','corrected calculation','Athugasemd'],
              ['Dagsetning (Date)',5,None,None],[datetime(2026,10,1),.0751,'L',2]],['B3']),
          'https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS/ZCM/1.0/ZC_TSB_ZND_05Y_MA?startPeriod=2026-07-01':israel()}
        class Client:
            def fetch(self,url,method='GET',body=None):
                return Payload(fixtures[url],url,'2026-10-04T00:00:00Z','fixture-sha','2026-10-02')
        wanted={'ESP':('2026-09-30',3.645,'secondary_market_bucket'),
                'SVK':('2026-09-25',3.86,'estimated_zero_coupon'),
                'ISL':('2026-10-01',7.51,'par_constant_maturity'),
                'ISR':('2026-09',3.716,'monthly_zero_coupon')}
        for iso,(period,value,kind) in wanted.items():
            c=countries[iso]
            self.assertNotEqual(c['yield']['adapter'],'unavailable',iso+' route missing')
            obs=sources.collect_yield(Client(),c,date(2026,10,4))
            self.assertEqual(obs.period,period);self.assertAlmostEqual(obs.value,value)
            self.assertEqual(obs.yield_type,kind);self.assertEqual(obs.raw_sha256,'fixture-sha')
            self.assertEqual(obs.unit,'percent');self.assertEqual(obs.redistribution,'pending')
            if iso=='ISL':self.assertIn('correction=L',obs.notes)
            if iso=='ISR':
                self.assertEqual(obs.frequency,'monthly')
                with self.assertRaisesRegex(DataError,'FREQUENCY_OR_DATE'):obs.valid_on(date(2026,10,4))
            if iso=='SVK':
                with self.assertRaisesRegex(DataError,'STALE'):obs.valid_on(date(2026,10,4))
            with self.assertRaisesRegex(DataError,'TENOR_NOT_IMPLEMENTED'):
                sources.collect_yield(None,c,date(2026,10,4),tenor=10)
