"""Execute the frozen evaluator on a new copy of a final first-pass snapshot."""
import argparse,pathlib,subprocess,sys,uuid
from prepare import prepare
from verify import ROOT,read
def main():
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    output=pathlib.Path(a.output).resolve()
    if output.exists():raise ValueError('Output must be a new file')
    row,workspace,_=prepare(a.run,'first-pass',ROOT/'work'/('checks-'+uuid.uuid4().hex))
    scenario=row['scenario'].replace('-project','');lock=read(row['methodLock'])
    blind=lock.get('sourceBlindId',row['blindId'])
    runner='run-checks-v7c-adjudicated.mjs' if scenario=='large' else 'run-checks-v7.mjs'
    result=subprocess.run(['node',str(ROOT/'evaluator/scripts'/runner),'--blind',blind,'--scenario',scenario,'--workspace',str(workspace),'--output',str(output)],cwd=ROOT)
    print('Product failures are recorded outcomes; inspect the receipt. Copy retained: '+str(workspace))
    sys.exit(result.returncode)
if __name__=='__main__':
    try:main()
    except (ValueError,OSError) as e:print('FAIL: '+str(e),file=sys.stderr);sys.exit(1)
