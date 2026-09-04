"""Materialize one verified release-asset slice into a new isolated repository."""
import argparse,json,os,pathlib,subprocess,sys,zipfile
from verify import ROOT,read,sha,check
def prepare(run,kind,destination):
    row=next(r for r in read('data/cohort.json')['rows'] if r['runId']==run)
    asset=next(a for a in read('assets/release-assets.json')['assets'] if a['kind']==kind and a['scenario']==row['scenario'])
    archive=ROOT/asset['path'];check(archive.is_file(),'Place the release asset at '+str(archive))
    check(sha(archive.read_bytes())==asset['sha256'],'Archive checksum mismatch')
    target=pathlib.Path(destination).resolve();check(not target.exists(),'Destination must be a new path')
    manifest=read(asset['manifest']);prefix=run+'/';entries=[e for e in manifest['files'] if e['path'].startswith(prefix)]
    with zipfile.ZipFile(archive) as z:
        payload=[]
        for e in entries:
            rel=e['path'][len(prefix):];p=pathlib.PurePosixPath(rel)
            check(not p.is_absolute() and '..' not in p.parts and '\\' not in rel and ':' not in rel,'Unsafe archive path')
            raw=z.read(e['path']);check(sha(raw)==e['sha256'] and len(raw)==e['bytes'],'Member hash mismatch: '+rel);payload.append((rel,raw,e['mode']))
    target.mkdir(parents=True)
    for rel,raw,mode in payload:
        p=target/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        if os.name!='nt':p.chmod(int(mode,8)&0o777)
    env={**os.environ,'GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':os.devnull}
    def git(*args):subprocess.run(['git','-C',str(target),'-c','core.hooksPath=/dev/null','-c','core.autocrlf=false',*args],env=env,check=True,stdout=subprocess.DEVNULL)
    git('init','-b','main')
    # Repository-local Git metadata overrides source checkout conversion without editing product files.
    (target/'.git/info/attributes').write_bytes(b'* -text\n')
    git('add','--force','.');git('-c','user.name=Benchmark reproduction','-c','user.email=benchmark@example.invalid','commit','--allow-empty','-m','Materialize verified input')
    return row,target,asset
def main():
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--kind',choices=['baselines','first-pass','review-inputs'],required=True);p.add_argument('--destination',required=True);p.add_argument('--prompt-output');a=p.parse_args()
    if a.prompt_output:
        check(a.kind=='baselines','A measured prompt is only generated for a baseline')
        check(not pathlib.Path(a.prompt_output).exists(),'Prompt output must be new')
    row,target,asset=prepare(a.run,a.kind,a.destination)
    if a.prompt_output:
        source=(ROOT/row['references']['prompt']).read_text(encoding='utf-8')
        if row['condition']=='prist':
            lock=read(row['methodLock']);source=source.replace(lock['taskWorkspace'],str(target))
        else:source='Работай только в назначенном checkout: '+str(target)+'.\n\n'+(ROOT/row['references']['envelope']).read_text(encoding='utf-8').rstrip()+'\n\n'+source
        p=pathlib.Path(a.prompt_output);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(source.encode('utf-8'))
    print(json.dumps(dict(status='prepared',runId=a.run,kind=a.kind,destination=str(target),sourceAsset=asset['name'],sourceSetupCommit=row['setupCommit'],newGitIdentity=True,hostedProvisioningRequired=row['condition']=='prist' and a.kind=='baselines',measuredTaskDispatched=False)))
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,OSError,StopIteration,subprocess.CalledProcessError) as e:print('FAIL: '+str(e),file=sys.stderr);sys.exit(1)
