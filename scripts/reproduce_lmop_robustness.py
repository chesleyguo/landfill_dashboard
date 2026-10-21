"""Reproduce the supplemental public-derived geographic experiment offline."""
from pathlib import Path
import subprocess,sys,json,hashlib
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 manifest=json.loads((ROOT/'PACKAGE_MANIFEST.json').read_text());assert manifest['public_derived_inputs_only']
 for name,record in manifest['files'].items():
  p=(ROOT/name).resolve();assert p.is_relative_to(ROOT.resolve()) and p.is_file() and not p.is_symlink();assert sha(p)==record['sha256'],name
 out=ROOT/'reproduction_run';assert not out.exists(),'Use a fresh package extraction for each run.'
 cmds=[[sys.executable,str(ROOT/'scripts/lmop_geographic_robustness.py'),'--inputs',str(ROOT/'public_reference'),'--reference',str(ROOT/'public_reference'),'--output',str(out)],[sys.executable,str(ROOT/'scripts/validate_lmop_robustness.py'),'--output',str(out),'--original',str(ROOT/'public_reference')]]
 for j,cmd in enumerate(cmds):
  result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');(ROOT/f'reproduction_step_{j+1}.log').write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0,f'Reproduction step {j+1} failed; see preserved log.'
 ref=pd.read_csv(ROOT/'reference_results/geographic_predictions.csv').sort_values('Landfill ID');actual=pd.read_csv(out/'geographic_predictions.csv').sort_values('Landfill ID');assert np.array_equal(ref['Landfill ID'].values,actual['Landfill ID'].values)
 cols=[c for c in ref if c.endswith('_probability')];diff=float(np.max(np.abs(ref[cols].values-actual[cols].values)));assert diff<1e-12
 refth=pd.read_csv(ROOT/'reference_results/training_selected_threshold.csv');th=pd.read_csv(out/'training_selected_threshold.csv');pd.testing.assert_frame_equal(refth,th,check_exact=False,rtol=1e-12,atol=1e-12)
 ci=pd.read_csv(out/'validation_attempt_001/paired_ap_intervals.csv');refci=pd.read_csv(ROOT/'reference_results/paired_ap_intervals.csv');pd.testing.assert_frame_equal(ci,refci,check_exact=False,rtol=1e-12,atol=1e-12)
 result=dict(status='PASSED',public_reference_hashes_verified=True,all_2325_geographic_predictions_reproduced=True,max_probability_difference=diff,training_threshold_reproduced=True,paired_intervals_reproduced=True,raw_downloads_in_this_supplement=False,interpretation='This offline run verifies public-derived inputs and exact results. Fresh official XLSX source download/audit was verified separately in the first research package.');(ROOT/'REPRODUCTION_CHECK.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
