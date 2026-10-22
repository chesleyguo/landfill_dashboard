"""Extract energy-project details (LMOP, September 2024) and airborne methane observations (Cusworth et al. 2024).

Download:
  https://www.epa.gov/system/files/documents/2024-09/lmopdata.xlsx
  https://pasteur.epa.gov/uploads/10.23719/1531980/science.adi7735_data_s1.xlsx  (EPA ORD, doi:10.23719/1531980)
then:
  python scripts/extract_project_and_airborne_data.py path/to/lmopdata.xlsx path/to/science.adi7735_data_s1.xlsx
Both file hashes are checked before reading. Outputs (standard library only):
  public_reference/landfill_projects.csv            Operational, Construction, Planned and Shutdown project rows
  public_reference/airborne_methane_cusworth2024.csv one row per observed landfill, joined to LMOP by GHGRP ID
The airborne values are copied as published; sheet inconsistencies are counted, not corrected.
"""
from pathlib import Path
import csv,datetime,hashlib,re,sys,zipfile,xml.etree.ElementTree as ET
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
PROJECTS_SHA256='a5c8bea26e7b5f6ecef247b762bde89b999915504814825a1eac7a1cd9f4ddd3'
AIRBORNE_SHA256='a0e78827cb0fe3f045b767dbaad93c0e66883c480ca17bb3bc498c6b324ff30b'
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def col(ref):
 n=0
 for ch in re.match(r'[A-Z]+',ref).group(0):n=n*26+ord(ch)-64
 return n-1
def workbook(path,sha):
 path=Path(path);assert hashlib.sha256(path.read_bytes()).hexdigest()==sha,f'Unexpected file: {path.name}'
 z=zipfile.ZipFile(path);strings=[''.join(t.text or '' for t in si.iter('{%s}t'%NS['m'])) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS)] if 'xl/sharedStrings.xml' in z.namelist() else []
 names=re.findall(r'<sheet [^>]*name="([^"]+)"',z.read('xl/workbook.xml').decode());sheets={}
 for i,name in enumerate(names,start=1):
  rows=[]
  for r in ET.fromstring(z.read(f'xl/worksheets/sheet{i}.xml')).iter('{%s}row'%NS['m']):
   vals={}
   for c in r.findall('m:c',NS):
    v=c.find('m:v',NS);t=c.get('t')
    vals[col(c.get('r'))]=''.join(x.text or '' for x in c.iter('{%s}t'%NS['m'])) if t=='inlineStr' else None if v is None else strings[int(v.text)] if t=='s' else v.text
   rows.append([vals.get(k) for k in range(max(vals)+1)] if vals else [])
  sheets[name]=rows
 return sheets
def records(rows):
 h=rows[0];return [(n,dict(zip(h,r+[None]*(len(h)-len(r))))) for n,r in enumerate(rows[1:],start=2) if any(x not in (None,'') for x in r)]
num=lambda v:'' if v in (None,'') else f'{float(v):.6g}'
excel_date=lambda v:'' if v in (None,'') else (datetime.date(1899,12,30)+datetime.timedelta(days=int(float(v)))).isoformat()
def write(name,rows):
 dest=ROOT/'public_reference'/name
 with dest.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 return dest.relative_to(ROOT)
def main():
 proj=workbook(sys.argv[1],PROJECTS_SHA256);sheet=next(r for r in proj.values() if r and 'Project ID' in r[0])
 out=[];ghgrp_to_landfill=defaultdict(set)
 for n,r in records(sheet):
  if r['GHGRP ID']:ghgrp_to_landfill[r['GHGRP ID']].add(int(r['Landfill ID']))
  if r['Current Project Status'] not in ('Operational','Construction','Planned','Shutdown') or not r['Project ID']:continue
  out.append({'landfill_id':int(r['Landfill ID']),'project_id':r['Project ID'],'parent_project_id':r['Project ID'].split('-')[0],'project_status':r['Current Project Status'],'project_name':r['Project Name'] or '','start_date':excel_date(r['Project Start Date']),'shutdown_date':excel_date(r['Project Shutdown Date']),'type_category':r['Project Type Category'] or '','project_type':r['LFG Energy Project Type'] or '','rng_delivery':r['RNG Delivery Method'] or '','actual_mw':num(r['Actual MW Generation']),'rated_mw':num(r['Rated MW Capacity']),'lfg_flow_mmscfd':num(r['LFG Flow to Project (mmscfd)']),'epa_est_reduction_direct_mmtco2e':num(r['Current Year Emission Reductions (MMTCO2e/yr) - Direct']),'epa_est_reduction_avoided_mmtco2e':num(r['Current Year Emission Reductions (MMTCO2e/yr) - Avoided']),'source_excel_row':n})
 op=[o for o in out if o['project_status']=='Operational'];assert len({o['landfill_id'] for o in op})==488 and len({o['parent_project_id'] for o in op})==542
 print(f'{len(out)} project rows ({len(op)} Operational at 488 landfills, 542 parent projects) -> {write("landfill_projects.csv",out)}')
 air=workbook(sys.argv[2],AIRBORNE_SHA256);plumes=defaultdict(list);bad_plumes=0
 for n,r in records(air['Unique plume detections']):
  m=re.search(r'(20\d{2})(\d{2})(\d{2})',r['Plume Candidate ID (UTC time of detection)'] or '')
  if m:plumes[r['GHGRP ID']].append('-'.join(m.groups()))
  else:bad_plumes+=1
 rows=[];listed=set()
 for n,r in records(air['Time-Averaged Source List']):
  gid=r['GHGRP ID'];listed.add(gid);ids=ghgrp_to_landfill.get(gid,set());assert len(ids)==1,f'GHGRP ID {gid} maps to {len(ids)} LMOP landfills'
  dates=sorted(plumes.get(gid,[]))
  rows.append({'landfill_id':ids.pop(),'ghgrp_id':gid,'avg_emission_kg_h':num(r['Average Emission Rate over all overpasses (kg/h)']),'avg_uncertainty_kg_h':num(r['Average Uncertainty Rate over all overpasses (kg/h)']),'avg_reported_ghgrp_tco2e':num(r['Average reported GHGRP emissions (METRIC TONS CO2e)']),'days_flown':r['Number of days landfill was flown'],'days_detected':r['Number of days where point sources were detected '],'plume_detections':len(dates),'first_plume_date':dates[0] if dates else '','last_plume_date':dates[-1] if dates else '','source_excel_row':n})
 orphan={g for g in plumes if g not in listed}
 print(f'{len(rows)} observed landfills, {sum(1 for r in rows if not r["avg_emission_kg_h"])} without a published average rate; {sum(len(plumes[g]) for g in orphan)} plumes under {len(orphan)} GHGRP IDs absent from the source list; {bad_plumes} plumes without a parsable date -> {write("airborne_methane_cusworth2024.csv",rows)}')
if __name__=='__main__':main()
