"""Offline integrity and cohort verification; Python standard library only."""
import argparse, collections, hashlib, json, math, pathlib, statistics, sys, zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))
def sha(raw):return hashlib.sha256(raw).hexdigest()
def check(ok,message):
    if not ok:raise ValueError(message)
def file(path):
    p=(ROOT/path).resolve();check(p.is_relative_to(ROOT),f'Unsafe path: {path}');return p
def historical_hash(raw,algorithm):
    if algorithm=='sha256-node-utf8-replacement-lf':raw=raw.decode('utf-8',errors='replace').replace('\r\n','\n').encode('utf-8')
    else:check(algorithm=='sha256-bytes',f'Unknown hash algorithm: {algorithm}')
    return sha(raw)
def git_object(kind,raw):return hashlib.sha1(kind.encode()+b' '+str(len(raw)).encode()+b'\0'+raw).digest()
def git_tree(files):
    root={}
    for name,raw,mode in files:
        node=root;parts=name.split('/')
        for part in parts[:-1]:node=node.setdefault(part,{})
        node[parts[-1]]=(raw,mode)
    def tree(node):
        data=b''
        for name,value in sorted(node.items(),key=lambda kv:(kv[0]+('/' if isinstance(kv[1],dict) else '')).encode()):
            if isinstance(value,dict):mode='40000';digest=tree(value)
            else:raw,number=value;mode='100755' if int(number,8)&0o111 else '100644';digest=git_object('blob',raw)
            data+=mode.encode()+b' '+name.encode()+b'\0'+digest
        return git_object('tree',data)
    return tree(root).hex()
def cohort_check():
    cohort=read('data/cohort.json');rows=cohort['rows'];source=read('reports/benchmark-v7-final/source-snapshot.json')
    check(len(rows)==36,'Expected 36 rows')
    check(len({r['runId'] for r in rows})==36,'Duplicate run ID')
    check(len({r['taskId'] for r in rows})==36,'Duplicate task ID')
    cells=collections.defaultdict(list);lineage=collections.Counter();algorithms=collections.Counter()
    source_by_task={r['taskId']:r for r in source['rows']}
    v7c='benchmark-v7c-prist-permissions-corrected-2026-09-02'
    for item in read('evidence/'+v7c+'/freeze/content-lock.json')['fileHashes']:
        raw=file(item['path']).read_bytes();check(sha(raw)==item['sha256'] and len(raw)==item['bytes'],f'Frozen input drift: {item["path"]}')
    for path,digest in read('evidence/'+v7c+'/checks/large-uniform-adjudication/evaluator-lock.json')['files'].items():
        check(sha(file(path).read_bytes())==digest,f'Locked evaluator drift: {path}')
    for r in rows:
        result=read(r['result']);fp=read(r['references']['firstPass']);ev=read(r['references']['evaluation']);usage=read(r['references']['usage']);receipt=read(r['references']['checks'])
        run=r['runId'];check(result==source_by_task[r['taskId']],f'Result differs from final source: {run}')
        lock=read(r['methodLock']);manifest=read('manifests/'+r['sourceSeries']+'.json')
        check(lock==next(x for x in manifest['cells'] if x['runId']==run),f'Method lock projection mismatch: {run}')
        if r['condition']=='prist':check(sha(file(r['references']['prompt']).read_bytes())==lock['promptSha256'],f'Prompt lock mismatch: {run}')
        check(fp['task']['taskId']==r['taskId']==usage['source']['taskId'],f'Task lineage mismatch: {run}')
        for key in ['scenario','condition','replica']:check(r[key]==result[key]==fp[key],f'Row dimension mismatch: {run}/{key}')
        check(result['model']=='gpt-5.6-luna' and result['reasoning']=='xhigh',f'Model mismatch: {run}')
        check(result['firstPassOnly'] and not result['browserUsed'] and result['interventions']==0,f'Execution policy mismatch: {run}')
        check(fp['task']['repairTurns']==0 and fp['task']['actualModel']==result['model'] and fp['task']['actualReasoning']==result['reasoning'],f'First-pass policy mismatch: {run}')
        check(fp['setup']['commit']==r['setupCommit'] and fp['setup']['tree']==r['setupTree'],f'Setup mismatch: {run}')
        check(ev['totalScore']==result['quality']['official'],f'Evaluation mismatch: {run}')
        check(len(ev['reviewPasses']) in [2,3],f'Review count: {run}')
        check(len(receipt['repetitions'])==3 and receipt['statePreserved'] is True,f'Objective state/repetitions: {run}')
        check(len({x['stateFingerprint'] for x in receipt['repetitions']})==1,f'Objective content drift: {run}')
        if ev.get('checkReceiptSha256'):check(sha(file(r['references']['checks']).read_bytes())==ev['checkReceiptSha256'],f'Final receipt identity: {run}')
        contract=file('evaluator/contracts-v7/'+r['scenario'].replace('-project','')+'.json').read_bytes()
        check(sha(contract.decode('utf-8').replace('\r\n','\n').encode())==ev['contractSha256'],f'Contract identity: {run}')
        for result_key,usage_key in [('total','totalTokens'),('uncachedInput','uncachedInputTokens'),('cachedInput','cachedInputTokens'),('outputIncludingReasoning','outputTokens')]:
            check(result['tokens'][result_key]==usage[usage_key],f'Usage mismatch: {run}/{result_key}')
        check(math.isclose(usage['billing']['estimatedTaskCostUsd'],result['costUsd']['lateChangeTask'],abs_tol=1e-10),f'Cost mismatch: {run}')
        check(fp['timing']['taskElapsedMs']==result['timing']['taskElapsedMs'],f'Timing mismatch: {run}')
        expected='benchmark-v7c-prist-permissions-corrected-2026-09-02' if r['condition']=='prist' else 'benchmark-v7-luna-xhigh-n3-2026-09-01'
        check(r['sourceSeries']==expected==fp['benchmarkId'],f'Series lineage mismatch: {run}')
        cells[r['scenario']+'/'+r['condition']].append(result);lineage[expected]+=1;algorithms[r['sourceHashAlgorithm']]+=1
    expected_cells={s+'/'+m for s in ['new-project','small-project','large-project'] for m in ['plain','bmad','classic-spec','prist']}
    check(set(cells)==expected_cells,'Expected 12 exact scenario/method cells')
    metrics={'totalTokens':('tokens','total'),'uncachedInputTokens':('tokens','uncachedInput'),'cachedInputTokens':('tokens','cachedInput'),'outputTokens':('tokens','outputIncludingReasoning'),'taskCostUsd':('costUsd','lateChangeTask'),'taskElapsedMs':('timing','taskElapsedMs'),'quality':('quality','official'),'interventions':('interventions',)}
    for key,group in cells.items():
        check(len(group)==3 and sorted(r['replica'] for r in group)==[1,2,3],f'Invalid repetitions: {key}')
        for metric,path in metrics.items():
            values=[]
            for row in group:
                v=row
                for component in path:v=v[component]
                values.append(v)
            for name,value in [('median',statistics.median(values)),('mean',statistics.mean(values))]:
                check(math.isclose(value,source['aggregate'][key][metric][name],rel_tol=1e-12,abs_tol=1e-9),f'Aggregate mismatch: {key}/{metric}/{name}')
    check(dict(lineage)==cohort['lineageCounts'],'Expected lineage 27+9')
    ratio_metrics={'totalTokensMedianRatioToPlain':'totalTokens','uncachedTokensMedianRatioToPlain':'uncachedInputTokens','cachedTokensMedianRatioToPlain':'cachedInputTokens','taskCostMedianRatioToPlain':'taskCostUsd','elapsedMedianRatioToPlain':'taskElapsedMs'}
    for key,record in source['ratiosToPlain'].items():
        baseline=source['aggregate'][key.split('/')[0]+'/plain'];current=source['aggregate'][key]
        for metric,aggregate_key in ratio_metrics.items():
            value=round(current[aggregate_key]['median']/baseline[aggregate_key]['median'],4)
            check(math.isclose(value,record[metric],abs_tol=1e-9),f'Ratio mismatch: {key}/{metric}')
        check(current['quality']['median']-baseline['quality']['median']==record['qualityMedianDeltaVsPlain'],f'Quality delta mismatch: {key}')
    return dict(rows=36,uniqueTasks=36,cells=12,repetitionsPerCell=3,lineage=dict(lineage),sourceHashAlgorithms=dict(algorithms),aggregateGroupsVerified=12)
def assets_check():
    index=read('assets/release-assets.json');cohort={r['runId']:r for r in read('data/cohort.json')['rows']};count=0;historical=0;excluded=0;baseline_trees=0
    for asset in index['assets']:
        path=file(asset['path']);check(path.is_file(),f'Missing release asset: {asset["name"]}')
        check(path.stat().st_size==asset['bytes'] and sha(path.read_bytes())==asset['sha256'],f'Archive hash mismatch: {asset["name"]}')
        manifest=read(asset['manifest']);expected={f['path']:f for f in manifest['files']}
        check(len(expected)==len(manifest['files']),f'Duplicate archive entry: {asset["name"]}')
        with zipfile.ZipFile(path) as z:
            baseline_files={run:[] for run in manifest['runIds']}
            check(len(z.namelist())==len(set(z.namelist())) and set(z.namelist())==set(expected),f'Archive member mismatch: {asset["name"]}')
            historical_by_run={}
            if asset['kind']=='first-pass':
                for run in manifest['runIds']:
                    f=read(cohort[run]['references']['firstPass'])['snapshot'];historical_by_run[run]=f.get('files') or {v['path']:v['sha256'] for v in f['fileHashes']}
                accounted={run:set() for run in manifest['runIds']}
                for x in manifest['excluded']:
                    check(x['path']=='.prist/connection.json',f'Unexpected first-pass exclusion: {x["path"]}')
                    check(historical_by_run[x['runId']][x['path']]==x['sha256'],'Excluded credential hash mismatch')
                    accounted[x['runId']].add(x['path']);excluded+=1
            for name,entry in expected.items():
                parts=pathlib.PurePosixPath(name).parts;check(len(parts)>1 and '..' not in parts and not name.startswith('/') and '\\' not in name,'Unsafe archive path')
                raw=z.read(name);check(len(raw)==entry['bytes'] and sha(raw)==entry['sha256'],f'Raw file hash mismatch: {name}');count+=1
                if asset['kind']=='baselines':
                    run,rel=name.split('/',1);baseline_files[run].append((rel,raw,entry['mode']))
                if asset['kind']=='first-pass':
                    run,rel=name.split('/',1);check(historical_hash(raw,cohort[run]['sourceHashAlgorithm'])==historical_by_run[run][rel],f'Historical file hash mismatch: {name}');historical+=1;accounted[run].add(rel)
            if asset['kind']=='first-pass':
                for run in accounted:check(accounted[run]==set(historical_by_run[run]),f'First-pass coverage mismatch: {run}')
            if asset['kind']=='baselines':
                check(not manifest['excluded'],'Baseline tree has omitted tracked files')
                for run,files in baseline_files.items():check(git_tree(files)==cohort[run]['setupTree'],f'Baseline Git tree mismatch: {run}');baseline_trees+=1
    return dict(archives=len(index['assets']),rawFileHashes=count,historicalFileHashes=historical,credentialHashesOnly=excluded,baselineGitTreesReconstructed=baseline_trees)
def verify_index():
    index=read('hashes/export-files.json');expected={x['path']:x for x in index['files']}
    for p,x in expected.items():
        raw=file(p).read_bytes();check(len(raw)==x['bytes'] and sha(raw)==x['sha256'],f'Export hash mismatch: {p}')
    skip={'.git','release-assets','work','node_modules','__pycache__'}
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and not any(x in skip for x in p.relative_to(ROOT).parts) and p.relative_to(ROOT).as_posix() not in ['hashes/export-files.json','hashes/SHA256SUMS'] and not p.name.endswith('.pyc')}
    check(actual==set(expected),f'Unindexed/missing export files: {sorted(actual^set(expected))[:10]}')
    sums=''.join(x['sha256']+'  '+x['path']+'\n' for x in index['files'])
    check(file('hashes/SHA256SUMS').read_text()==sums,'SHA256SUMS differs from file index')
    return len(expected)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--assets',action='store_true');parser.add_argument('--skip-index',action='store_true',help=argparse.SUPPRESS);args=parser.parse_args()
    result=dict(status='pass',cohort=cohort_check())
    if not args.skip_index:result['exportFiles']=verify_index()
    if args.assets:
        from build_evidence_packages import verify_all
        raw_assets=assets_check()
        packages=verify_all(ROOT/'release-assets'/'packages',ROOT/'release-assets')
        result['assets']={
            'rawArchives':raw_assets,
            'sanitizedPackages':{
                'packages':len(packages),
                'includedEvidenceMembers':sum(x['includedEvidenceMembers'] for x in packages),
                'excludedRawMembers':sum(x['excludedRawMembers'] for x in packages),
                'priorCredentialHashesOnly':sum(x['priorCredentialHashesOnly'] for x in packages),
                'records':packages,
            },
        }
    print(json.dumps(result,indent=2))
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,OSError,AssertionError) as e:print('FAIL: '+str(e),file=sys.stderr);sys.exit(1)
