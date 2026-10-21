"""Extract landfill coordinates, city and GHGRP ID from the official September 2024 LMOP landfill file.

Download https://www.epa.gov/system/files/documents/2024-09/landfilllmopdata.xlsx, then:
  python scripts/extract_landfill_locations.py path/to/landfilllmopdata.xlsx
The file hash is checked before reading. Output: public_reference/landfill_locations.csv
(one row per Landfill ID; blank latitude/longitude where the source has none). Standard library only.
"""
from pathlib import Path
import csv,hashlib,re,sys,zipfile,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA256='2fc1d72ca9c022fb3ce9225f3b4ae5466b0b9c28b7d7efe7a10d2ac1415a0aa6'
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
FIELDS=['Landfill ID','Latitude','Longitude','City','GHGRP ID']
def col(ref):
 n=0
 for ch in re.match(r'[A-Z]+',ref).group(0):n=n*26+ord(ch)-64
 return n-1
def sheet_rows(z,name,strings):
 for r in ET.fromstring(z.read(name)).iter('{%s}row'%NS['m']):
  vals={}
  for c in r.findall('m:c',NS):
   v=c.find('m:v',NS);t=c.get('t')
   vals[col(c.get('r'))]=''.join(x.text or '' for x in c.iter('{%s}t'%NS['m'])) if t=='inlineStr' else None if v is None else strings[int(v.text)] if t=='s' else v.text
  yield [vals.get(i) for i in range(max(vals)+1)] if vals else []
def main():
 src=Path(sys.argv[1]);assert hashlib.sha256(src.read_bytes()).hexdigest()==SOURCE_SHA256,'Not the September 2024 landfilllmopdata.xlsx'
 z=zipfile.ZipFile(src);strings=[''.join(t.text or '' for t in si.iter('{%s}t'%NS['m'])) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS)]
 for name in sorted(n for n in z.namelist() if re.match(r'xl/worksheets/sheet\d+\.xml',n)):
  rows=list(sheet_rows(z,name,strings))
  if rows and rows[0][:2]==['GHGRP ID','Landfill ID']:break
 else:raise SystemExit('Landfill sheet not found')
 header=rows[0];idx={f:header.index(f) for f in FIELDS};out=[]
 for excel_row,r in enumerate(rows[1:],start=2):
  r=r+[None]*(len(header)-len(r));lat,lon=r[idx['Latitude']],r[idx['Longitude']]
  ok=lat not in (None,'') and lon not in (None,'') and -90<=float(lat)<=90 and -180<=float(lon)<=180 and (float(lat),float(lon))!=(0.0,0.0)
  out.append({'landfill_id':int(r[idx['Landfill ID']]),'latitude':f'{float(lat):.6f}' if ok else '','longitude':f'{float(lon):.6f}' if ok else '','city':r[idx['City']] or '','ghgrp_id':r[idx['GHGRP ID']] or '','source_excel_row':excel_row})
 assert len({o['landfill_id'] for o in out})==len(out)==2641
 dest=ROOT/'public_reference/landfill_locations.csv'
 with dest.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
 print(f'{len(out)} landfills, {sum(1 for o in out if o["latitude"])} with coordinates, {sum(1 for o in out if o["ghgrp_id"])} with a GHGRP ID -> {dest.relative_to(ROOT)}')
if __name__=='__main__':main()
