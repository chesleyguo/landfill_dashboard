"""Independent metric reconciliation, three refits, paired cluster comparisons."""
from pathlib import Path
import json, hashlib, datetime as dt, sys, argparse, time, importlib.metadata
import pandas as pd
import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score, brier_score_loss, confusion_matrix
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,default=ROOT/'outputs/2026-10-06_geographic_robustness/run_001');a.add_argument('--original',type=Path,default=ROOT/'outputs/2026-10-06_dashboard_research/run_001');a.add_argument('--attempt-name',default='validation_attempt_001');args=a.parse_args();out=args.output;vout=out/args.attempt_name;vout.mkdir(exist_ok=False);start=time.monotonic()
 pred=pd.read_csv(out/'geographic_predictions.csv');abl=pd.read_csv(out/'original_holdout_ablation_predictions.csv');s=pd.read_csv(out/'analysis_input.csv');allmetrics=pd.read_csv(out/'model_comparisons.csv');fold=pd.read_csv(out/'state_fold_metrics.csv');checks={};errors=[]
 def metriccheck(yy,pp,row):
  if len(set(yy))==2:
   errors.extend([abs(average_precision_score(yy,pp)-row['average_precision']),abs(roc_auc_score(yy,pp)-row['roc_auc'])])
  errors.append(abs(brier_score_loss(yy,pp)-row['brier']))
 for _,row in allmetrics.loc[~allmetrics['experiment'].eq('original_training_oof')].iterrows():
  frame=pred if row['experiment']=='pooled_leave_state_component_out' else abl;col='constant_prior_probability' if row['model']=='constant_training_prevalence' else row['model']+'_probability';metriccheck(frame['observed_operational_record'].values,frame[col].values,row)
 for _,row in fold.iterrows():
  frame=pred.loc[pred['state_component'].eq(row['state_component'])];col='constant_prior_probability' if row['model']=='constant_training_prevalence' else row['model']+'_probability';metriccheck(frame['observed_operational_record'].values,frame[col].values,row)
 checks['all_pooled_and_state_metrics_reconcile']=max(errors)<1e-12
 checks['all_2325_ids_predicted_once']=pred['Landfill ID'].is_unique and set(pred['Landfill ID'])==set(s['Landfill ID'])
 checks['observed_labels_match_audited_analysis_input']=np.array_equal(pred.set_index('Landfill ID').sort_index()['observed_operational_record'].values,s.set_index('Landfill ID').sort_index()['recorded_operational_energy_project'].astype(int).values)
 checks['whole_states_withheld']=all(s.groupby('State')['state_component'].nunique()==1)
 # Independent implementation, refitting three selected diagnostic folds only.
 diffs=[]
 for state in ['CA','NJ','MT']:
  tr=s.loc[~s['State'].eq(state)];te=s.loc[s['State'].eq(state)]
  def xx(frame):return pd.DataFrame({'log_waste':np.log10(frame['Waste in Place (tons)'].to_numpy()),'status':frame['Current Landfill Status'].to_numpy(),'owner':frame['Ownership Type'].to_numpy()})
  preprocess=ColumnTransformer([('num',Pipeline([('imputer',SimpleImputer(strategy='median')),('scaler',StandardScaler())]),['log_waste']),('cat',Pipeline([('imputer',SimpleImputer(strategy='constant',fill_value='Unknown')),('encoding',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),['status','owner'])])
  model=Pipeline([('features',preprocess),('model',LogisticRegression(C=1,solver='lbfgs',max_iter=1000,tol=1e-7,random_state=153))]);model.fit(xx(tr),tr['recorded_operational_energy_project'].astype(int));p=model.predict_proba(xx(te))[:,1]
  expected=pred.set_index('Landfill ID').loc[te['Landfill ID'],'site_attributes_probability'].values;diffs.append(dict(state=state,max_absolute_probability_difference=float(np.max(np.abs(p-expected))),test_n=len(te)))
 checks['three_independent_state_refits_match']=max(r['max_absolute_probability_difference'] for r in diffs)<1e-12
 # Independently reconstruct the training-only threshold: descend sorted positive scores.
 oof=pd.read_csv(args.original/'training_oof_predictions.csv');positive=np.sort(oof.loc[oof['observed_operational_record'].eq(1),'site_attributes_probability'].values)[::-1];threshold=float(positive[int(np.ceil(.7*len(positive)))-1]);reported=pd.read_csv(out/'training_selected_threshold.csv');checks['training_threshold_independently_reproduced']=abs(reported.loc[reported['rule'].eq('training_oof_recall_70pct'),'threshold'].iloc[0]-threshold)<1e-12
 orig=pd.read_csv(args.original/'holdout_predictions.csv');checks['threshold_training_holdout_ids_disjoint']=set(oof['Landfill ID']).isdisjoint(orig['Landfill ID'])
 for _,row in reported.iterrows():
  frame=oof if row['partition']=='training_oof' else orig;yy=frame['observed_operational_record'].values;pp=frame['site_attributes_probability'].values;tn,fp,fn,tp=confusion_matrix(yy,pp>=row['threshold'],labels=[0,1]).ravel();assert [tn,fp,fn,tp]==[row['tn'],row['fp'],row['fn'],row['tp']]
 checks['threshold_confusion_matrices_reconcile']=True
 groups=abl['geographic_project_group'].unique();indices=[np.where(abl['geographic_project_group'].values==g)[0] for g in groups];rng=np.random.default_rng(20261007)
 pairs=[('full_minus_waste_only','site_attributes','waste_only'),('full_minus_waste_status','site_attributes','waste_status'),('coverage_minus_full','attributes_record_coverage','site_attributes'),('missingness_minus_full','attributes_missingness','site_attributes')];draws=[]
 yy=abl['observed_operational_record'].values
 for rep in range(500):
  ix=np.concatenate([indices[int(i)] for i in rng.integers(0,len(indices),len(indices))]);y=yy[ix]
  if len(set(y))<2:continue
  record=dict(replicate=rep,n=len(ix))
  for name,left,right in pairs:record[name]=float(average_precision_score(y,abl[left+'_probability'].values[ix])-average_precision_score(y,abl[right+'_probability'].values[ix]))
  draws.append(record)
 draws=pd.DataFrame(draws);draws.to_csv(vout/'paired_cluster_bootstrap_draws.csv',index=False);intervals=[]
 for name,left,right in pairs:
  values=draws[name].values;intervals.append(dict(comparison=name,point_difference=float(average_precision_score(yy,abl[left+'_probability'])-average_precision_score(yy,abl[right+'_probability'])),lower_95=float(np.quantile(values,.025)),upper_95=float(np.quantile(values,.975)),valid_replicates=len(values),includes_zero=bool(np.quantile(values,.025)<=0<=np.quantile(values,.975))))
 pd.DataFrame(intervals).to_csv(vout/'paired_ap_intervals.csv',index=False)
 checks['500_paired_resamples']=len(draws)==500;checks['source_hashes_still_match']=all(sha(Path(p))==h for p,h in json.loads((out/'run_manifest.json').read_text())['input_sha256'].items())
 assert all(checks.values()),checks
 obj=dict(created_utc=dt.datetime.now(dt.timezone.utc).isoformat(),command=[sys.executable,*sys.argv],duration_seconds=time.monotonic()-start,script_sha256=sha(__file__),versions={p:importlib.metadata.version(p) for p in ['numpy','pandas','scikit-learn']},max_metric_difference=max(errors),independent_refits=diffs,threshold_reconstructed=threshold,bootstrap_seed=20261007,intervals=intervals,interpretation='Secondary conditional paired holdout comparisons; no model selection, national representativeness or refitting uncertainty.',checks=checks)
 obj['checks']={key:bool(value) for key,value in checks.items()};obj['max_metric_difference']=float(obj['max_metric_difference']);(vout/'independent_validation.json').write_text(json.dumps(obj,indent=2),encoding='utf-8');print(json.dumps(obj,indent=2))
if __name__=='__main__':main()
