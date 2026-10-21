"""Retrospective LMOP geographic stress, feature ablation and training-only threshold audit."""
from pathlib import Path
import json, hashlib, datetime as dt, time, sys, platform, importlib.metadata, warnings, argparse
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, confusion_matrix
from sklearn.exceptions import ConvergenceWarning

ROOT=Path(__file__).resolve().parents[1]
SPECS={
 'waste_only':(['log10_waste'],[],False),
 'status_owner':([],['operating_status','ownership'],False),
 'waste_status':(['log10_waste'],['operating_status'],False),
 'waste_owner':(['log10_waste'],['ownership'],False),
 'site_attributes':(['log10_waste'],['operating_status','ownership'],False),
 'attributes_missingness':(['log10_waste'],['operating_status','ownership'],True),
 'attributes_record_coverage':(['log10_waste','waste_record_year'],['operating_status','ownership'],True)}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def score(y,p):
 y=np.asarray(y);p=np.asarray(p);tn,fp,fn,tp=confusion_matrix(y,p>=.5,labels=[0,1]).ravel()
 return dict(n=len(y),positive_n=int(y.sum()),prevalence=float(y.mean()),roc_auc=None if len(set(y))<2 else float(roc_auc_score(y,p)),average_precision=None if len(set(y))<2 else float(average_precision_score(y,p)),brier=float(brier_score_loss(y,p)),recall=None if tp+fn==0 else float(tp/(tp+fn)),precision=None if tp+fp==0 else float(tp/(tp+fp)),tn=int(tn),fp=int(fp),fn=int(fn),tp=int(tp))
def pipeline(spec):
 nums,cats,indicator=spec;trs=[]
 if nums:trs.append(('numeric',Pipeline([('impute',SimpleImputer(strategy='median',add_indicator=indicator)),('scale',StandardScaler())]),nums))
 if cats:trs.append(('categories',Pipeline([('impute',SimpleImputer(strategy='constant',fill_value='Unknown')),('onehot',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),cats))
 return Pipeline([('preprocess',ColumnTransformer(trs)),('logistic',LogisticRegression(C=1,penalty='l2',solver='lbfgs',max_iter=1000,tol=1e-7,random_state=153))])
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--inputs',type=Path,default=ROOT/'outputs/2026-10-06_weekly_research/run_001');parser.add_argument('--reference',type=Path,default=ROOT/'outputs/2026-10-06_dashboard_research/run_001');parser.add_argument('--output',type=Path,default=ROOT/'outputs/2026-10-06_geographic_robustness/run_001');args=parser.parse_args()
 out=args.output;out.mkdir(parents=True,exist_ok=False);start=time.monotonic();began=dt.datetime.now(dt.timezone.utc).isoformat()
 def dump(name,obj):(out/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
 def csv(name,frame):frame.to_csv(out/name,index=False,encoding='utf-8-sig')
 inputs=[args.inputs/'landfill_energy_labels.csv',args.inputs/'operational_project_site_links.csv',args.reference/'split_manifest.csv',args.reference/'holdout_predictions.csv',args.reference/'training_oof_predictions.csv'];hashes={str(p):sha(p) for p in inputs}
 labels=pd.read_csv(inputs[0]);links=pd.read_csv(inputs[1]);splits=pd.read_csv(inputs[2]);original=pd.read_csv(inputs[3]);train_oof=pd.read_csv(inputs[4])
 s=labels.loc[~labels['energy_record_class'].eq('Unknown only')].sort_values('Landfill ID').reset_index(drop=True).merge(splits[['Landfill ID','geographic_project_group','partition','cv_fold']],on='Landfill ID',validate='one_to_one').sort_values('Landfill ID').reset_index(drop=True)
 assert len(s)==2325 and s['recorded_operational_energy_project'].sum()==488 and s['Landfill ID'].is_unique
 x=pd.DataFrame(dict(log10_waste=np.log10(s['Waste in Place (tons)']),waste_record_year=s['Waste in Place Year'],operating_status=s['Current Landfill Status'],ownership=s['Ownership Type']))
 y=s['recorded_operational_energy_project'].to_numpy(dtype=int);train=np.where(s['partition'].eq('train'))[0];hold=np.where(s['partition'].eq('holdout'))[0]
 states=sorted(s['State'].unique());parent={v:v for v in states}
 def find(g):
  while parent[g]!=g:parent[g]=parent[parent[g]];g=parent[g]
  return g
 def union(a,b):
  aa,bb=find(a),find(b)
  if aa!=bb:parent[max(aa,bb)]=min(aa,bb)
 state_by_id=labels.set_index('Landfill ID')['State'].to_dict()
 for _,part in links.groupby('parent_project_id'):
  values=sorted(set(state_by_id[int(lid)] for lid in part['landfill_id']))
  for state in values[1:]:union(values[0],state)
 components={root:sorted(v for v in states if find(v)==root) for root in sorted(set(find(v) for v in states))}
 s['state_component']=s['State'].map(find);csv('analysis_input.csv',s)
 global_rows=[];fold_rows=[];pre=[];holdpred=s.loc[hold,['Landfill ID','State','geographic_project_group']].copy();holdpred['observed_operational_record']=y[hold]
 statepred=s[['Landfill ID','State','state_component','geographic_project_group']].copy();statepred['observed_operational_record']=y
 statepred['constant_prior_probability']=np.nan
 def fit_predict(name,tr,te,fold):
  if time.monotonic()-start>300:raise RuntimeError('Five-minute run limit reached')
  model=pipeline(SPECS[name]);model.fit(x.iloc[tr],y[tr]);p=model.predict_proba(x.iloc[te])[:,1]
  assert np.isfinite(p).all() and np.all((p>=0)&(p<=1))
  nums=SPECS[name][0]
  if nums:
   expected=np.nanmedian(x.iloc[tr][nums].to_numpy(dtype=float),axis=0);actual=model['preprocess'].named_transformers_['numeric']['impute'].statistics_
   assert np.allclose(expected,actual)
   pre.append(dict(model=name,fold=fold,train_n=len(tr),test_n=len(te),numeric_training_medians=actual.tolist()))
  return p
 with warnings.catch_warnings():
  warnings.simplefilter('error',ConvergenceWarning)
  for name in SPECS:
   oof=np.full(len(s),np.nan)
   for fold in range(5):
    tr=train[s.loc[train,'cv_fold'].to_numpy()!=fold];te=train[s.loc[train,'cv_fold'].to_numpy()==fold]
    assert set(s.loc[tr,'geographic_project_group']).isdisjoint(s.loc[te,'geographic_project_group'])
    oof[te]=fit_predict(name,tr,te,'original_cv_'+str(fold))
   p=fit_predict(name,train,hold,'original_holdout');holdpred[name+'_probability']=p
   global_rows.extend([dict(experiment='original_training_oof',model=name,**score(y[train],oof[train])),dict(experiment='original_holdout_posthoc_ablation',model=name,**score(y[hold],p))])
   statepred[name+'_probability']=np.nan
  for fi,(root,memberstates) in enumerate(components.items()):
   te=np.where(s['state_component'].eq(root))[0];tr=np.where(~s['state_component'].eq(root))[0]
   assert set(s.loc[tr,'State']).isdisjoint(s.loc[te,'State']) and set(s.loc[tr,'geographic_project_group']).isdisjoint(s.loc[te,'geographic_project_group'])
   assert len(set(y[tr]))==2
   prior=np.repeat(y[tr].mean(),len(te));statepred.loc[te,'constant_prior_probability']=prior
   base=score(y[te],prior);fold_rows.append(dict(state_component=root,states=';'.join(memberstates),model='constant_training_prevalence',train_n=len(tr),**base))
   for name in SPECS:
    p=fit_predict(name,tr,te,'state_'+root);statepred.loc[te,name+'_probability']=p;fold_rows.append(dict(state_component=root,states=';'.join(memberstates),model=name,train_n=len(tr),**score(y[te],p)))
   if fi%10==0:print(f'Completed geographic fold {fi+1}/{len(components)}',flush=True)
  for name in ['constant_training_prevalence',*SPECS]:
   col='constant_prior_probability' if name=='constant_training_prevalence' else name+'_probability';assert statepred[col].notna().all();global_rows.append(dict(experiment='pooled_leave_state_component_out',model=name,**score(y,statepred[col])))
 csv('geographic_predictions.csv',statepred);csv('original_holdout_ablation_predictions.csv',holdpred);csv('model_comparisons.csv',pd.DataFrame(global_rows));csv('state_fold_metrics.csv',pd.DataFrame(fold_rows));dump('preprocessing_audit.json',pre)
 # A hypothetical 70% recall threshold is selected from training OOF only.
 oy=train_oof['observed_operational_record'].to_numpy(dtype=int);op=train_oof['site_attributes_probability'].to_numpy();thresholds=np.unique(op);eligible=thresholds[np.array([(op[oy==1]>=t).mean()>=.7 for t in thresholds])];threshold=float(eligible.max());hp=original['site_attributes_probability'].to_numpy();hy=original['observed_operational_record'].to_numpy(dtype=int)
 threshold_rows=[]
 for label,t in [('fixed_0_5',.5),('training_oof_recall_70pct',threshold)]:
  for partition,yy,pp in [('training_oof',oy,op),('unchanged_original_holdout',hy,hp)]:
   tn,fp,fn,tp=confusion_matrix(yy,pp>=t,labels=[0,1]).ravel();threshold_rows.append(dict(rule=label,threshold=t,partition=partition,n=len(yy),positive_n=int(yy.sum()),flagged_n=int(tp+fp),precision=float(tp/(tp+fp)) if tp+fp else None,recall=float(tp/(tp+fn)),tn=int(tn),fp=int(fp),fn=int(fn),tp=int(tp)))
 csv('training_selected_threshold.csv',pd.DataFrame(threshold_rows))
 # Coverage includes Unknown, which are never used as model negatives.
 cover=[]
 for state,part in labels.groupby('State'):
  known=part.loc[~part['energy_record_class'].eq('Unknown only')];cover.append(dict(state=state,all_n=len(part),known_n=len(known),unknown_n=int(part['energy_record_class'].eq('Unknown only').sum()),unknown_fraction=float(part['energy_record_class'].eq('Unknown only').mean()),operational_n=int(part['recorded_operational_energy_project'].sum()),missing_waste_n=int(part['Waste in Place (tons)'].isna().sum()),waste2022_n=int(part['Waste in Place Year'].eq(2022).sum())))
 csv('state_record_coverage.csv',pd.DataFrame(cover))
 fm=pd.DataFrame(fold_rows);eligible=fm.loc[fm['model'].eq('site_attributes')&fm['n'].ge(20)&fm['positive_n'].ge(5)&(fm['n']-fm['positive_n']).ge(5)].copy();eligible['ap_minus_prevalence']=eligible['average_precision']-eligible['prevalence'];csv('eligible_state_fold_metrics.csv',eligible)
 origmap=original.set_index('Landfill ID');d=holdpred.set_index('Landfill ID');maxdiff=float(np.max(np.abs(d.loc[origmap.index,'site_attributes_probability']-origmap['site_attributes_probability'])))
 checks=dict(all_known_sites_predicted_once=statepred['Landfill ID'].is_unique and len(statepred)==2325,unknown_never_negative=len(labels)-len(s)==316,all_states_withheld_as_whole=True,shared_county_components_do_not_cross_state_folds=all(s.groupby('geographic_project_group')['state_component'].nunique()==1),shared_projects_do_not_cross_state_folds=all(len({find(state_by_id[int(i)]) for i in part['landfill_id']})==1 for _,part in links.groupby('parent_project_id')),original_holdout_model_reproduced=maxdiff<1e-12,threshold_selected_from_training_only=True,finite_predictions=bool(np.isfinite(statepred.select_dtypes('number')).all().all()),training_only_medians_checked=len(pre)>0,converged_without_warnings=True,inputs_unchanged=all(sha(Path(p))==h for p,h in hashes.items()),all_seven_models_reported=len(global_rows)==22)
 assert all(checks.values()),checks
 summary=dict(created_utc=dt.datetime.now(dt.timezone.utc).isoformat(),target='recorded Operational status, not verified adoption or emissions',retrospective_stress_not_external_validation=True,state_count=len(states),state_component_count=len(components),components=components,models=global_rows,training_selected_threshold=threshold_rows,eligible_state_folds=len(eligible),eligible_median_ap_minus_prevalence=float(eligible['ap_minus_prevalence'].median()),eligible_min_ap_minus_prevalence=float(eligible['ap_minus_prevalence'].min()),eligible_max_ap_minus_prevalence=float(eligible['ap_minus_prevalence'].max()),original_prediction_max_abs_difference=maxdiff,checks=checks)
 dump('summary.json',summary);dump('run_manifest.json',dict(started_utc=began,finished_utc=dt.datetime.now(dt.timezone.utc).isoformat(),duration_seconds=time.monotonic()-start,command=[sys.executable,*sys.argv],python=sys.version,platform=platform.platform(),versions={p:importlib.metadata.version(p) for p in ['numpy','pandas','scipy','scikit-learn']},input_sha256=hashes,script_sha256=sha(__file__),seed=153,state_folds='deterministic leave-state-component-out; no seed search',specifications=SPECS,threshold_rule='highest training-only OOF threshold achieving recall >=0.70',not_a_git_repository=True,synthetic_environmental_data=False,output_hashes={p.name:sha(p) for p in out.iterdir() if p.is_file()},checks=checks))
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
