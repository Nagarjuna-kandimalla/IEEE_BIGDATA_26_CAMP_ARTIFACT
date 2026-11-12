"""Generate camera-ready live tables/figure from packaged Warm-Transfer/Direct-Transfer records."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--repo-root',type=Path,default=HERE.parents[3]);root=parser.parse_args().repo_root.resolve();source=root/'RESULTS/RQ5/transfer_studies';out=HERE/'result_assets';metrics={};shares=[];hashes={}
for key in ['warm_transfer_cold','warm_transfer_warm','warm_transfer_new_input','direct_transfer_new_input']:
 path=source/key/'task_instances.tsv.gz';hashes[str(path.relative_to(root))]=hashlib.sha256(path.read_bytes()).hexdigest();d=pd.read_csv(path,sep='\t');assert len(d)==6000 and d.final_success.all() and not d.duplicated(['process','task_instance']).any();s=json.loads((source/key/'summary.json').read_text());h=json.loads((source/key/'handoff.json').read_text());assert h['status']=='PASS' and h['duplicate_success_observations']==0
 req=d.first_applied_allocation_mib;peak=d.final_peak_mib;assert (peak>0).all();ratio=req/peak
 assert np.isclose(100*np.median(abs(d.a_plus_p_plus_c_point_q50_mib-peak)/peak),s['global']['a_plus_p_plus_c_point_median_ape_percent'])
 for filename in ['summary.json','handoff.json']:
  q=source/key/filename;hashes[str(q.relative_to(root))]=hashlib.sha256(q.read_bytes()).hexdigest()
 metrics[key]={'request_gib':float(req.sum()/1024),'peak_gib':float(peak.sum()/1024),'unused_gibh':float(((req-peak).clip(lower=0)*d.final_runtime_seconds/3600/1024).sum()),'coverage':100*float((req>=peak).mean()),'mdape':s['global']['a_plus_p_plus_c_point_median_ape_percent'],'alignment_mdape':s['by_process']['ALIGN_CHUNK']['a_plus_p_plus_c_point_median_ape_percent'],'oom':s['global']['total_oom_attempts'],'tasks':len(d)}
 assert np.isclose(metrics[key]['coverage'],100*s['global']['applied_first_request_coverage'])
 shares.append([100*float(m.mean()) for m in [ratio<1,(ratio>=1)&(ratio<=1.05),(ratio>1.05)&(ratio<=1.10),(ratio>1.10)&(ratio<=1.25),ratio>1.25]])
fields=[('Requests (GiB)','request_gib',2),('Peak sum (GiB)','peak_gib',2),('Unused memory (GiB-h)','unused_gibh',5),(r'Coverage (\%)','coverage',2),(r'MdAPE (\%)','mdape',2),('Recorded OOMs','oom',0)]
for name,keys,header in [('warm_transfer',['warm_transfer_cold','warm_transfer_warm','warm_transfer_new_input'],r'Metric & Cold & Warm & New input\\'),('direct_transfer',['warm_transfer_new_input','direct_transfer_new_input'],r'New-input metric & Warm-Transfer & Direct-Transfer\\')]:
 rows=[label+' & '+' & '.join(f'{metrics[k][field]:,.{digits}f}' for k in keys)+r' \\' for label,field,digits in fields]
 if name=='direct_transfer':rows.insert(-1,r'Alignment MdAPE (\%) & '+ ' & '.join(f'{metrics[k]["alignment_mdape"]:.2f}' for k in keys)+r' \\')
 text=r'\begin{tabular}{@{}l'+'r'*len(keys)+r'@{}}'+'\n'+r'\toprule'+'\n'+header+'\n'+r'\midrule'+'\n'+'\n'.join(rows)+'\n'+r'\bottomrule'+'\n'+r'\end{tabular}'+'\n';(out/(name+'_table.tex')).write_text(text)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(3.45,2.4),layout='constrained');left=np.zeros(4);y=np.arange(4)[::-1]
for j,(label,color) in enumerate(zip(['Below peak','0–5%','5–10%','10–25%','>25%'],['#B64538','#237C64','#62AD92','#7C9BB3','#CFD8DE'])):
 vals=np.array(shares)[:,j];ax.barh(y,vals,left=left,height=.55,color=color,edgecolor='white',linewidth=.4,label=label);left+=vals
ax.set(yticks=y,yticklabels=['Cold','Warm','Warm-Transfer','Direct-Transfer'],xlabel='Share of tasks (%)',xlim=(0,100));ax.legend(title='CAMP request margin above task peak',title_fontsize=7,fontsize=7,loc='lower center',bbox_to_anchor=(.45,1.01),ncol=3,frameon=False,columnspacing=.8,handlelength=1.1)
fig.savefig(out/'live_margins.pdf');fig.savefig(out/'live_margins.png',dpi=200);plt.close(fig)
(out/'live_result_provenance.json').write_text(json.dumps({'source_sha256':hashes,'metrics':metrics,'margin_percent':shares,'definition':'First CAMP request and final successful peak/runtime. Excludes 128 MiB execution allowance; zero failed-attempt cost included.','direct_transfer_parent':'Exact Warm-Transfer cold checkpoint, no rerun.'},indent=2)+'\n');print('Verified and generated live Warm-Transfer/Direct-Transfer assets')
