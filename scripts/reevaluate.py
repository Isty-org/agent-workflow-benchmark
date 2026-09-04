"""Recompute 36 final scores from locked objective receipts and blind reviews."""
import argparse,json,math,sys
from verify import read,check
def evaluate(row):
    ev=read(row['references']['evaluation']);receipt=read(row['references']['checks']);contract=read('evaluator/contracts-v7/'+row['scenario'].replace('-project','')+'.json')
    passes=ev['reviewPasses'];totals=[sum(c['pointsAwarded'] for c in p['checks']) for p in passes]
    check(len(passes)==(3 if abs(totals[0]-totals[1])>4 else 2),f'Review policy: {row["runId"]}')
    categories={k:0 for k in ['functional','regression','architecture','scope']};awarded={}
    for c in contract['checks']:
        if c['scoring']=='binary':
            values=[next((v for v in r['checks'] if v['id']==c['id']),{}) for r in receipt['repetitions']]
            points=c['maxPoints'] if len(values)==3 and all(v.get('passed') is True for v in values) else 0
        else:
            values=sorted(next(v['pointsAwarded'] for v in p['checks'] if v['id']==c['id']) for p in passes)
            points=math.floor(sum(values)/2+0.5) if len(values)==2 else values[1]
        check(0<=points<=c['maxPoints'],f'Out-of-range points: {row["runId"]}/{c["id"]}')
        awarded[c['id']]=points;categories[c['category']]+=points
    raw=sum(categories.values());severities={f['severity'] for f in ev['findings']};official=min(raw,49 if 'critical' in severities else 69 if 'major' in severities else 100)
    check(awarded=={c['id']:c['pointsAwarded'] for c in ev['checks']},f'Check-level score differs: {row["runId"]}')
    result=read(row['result']);check(official==result['quality']['official'],f'Official score differs: {row["runId"]}')
    reported_raw=result['quality']['rawBeforeSeverityCap']
    known={'v7-new-bmad-r3':(85,69),'v7-new-plain-r2':(81,69)}
    if raw!=reported_raw:
        check(ev.get('rawScore') is None and known.get(row['runId'])==(raw,reported_raw),f'Unexpected source raw-score discrepancy: {row["runId"]}')
    return dict(runId=row['runId'],rawRecomputed=raw,rawReported=reported_raw,rawFieldMatches=raw==reported_raw,official=official,categories=categories)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output');args=parser.parse_args()
    result=dict(status='pass',rows=[evaluate(r) for r in read('data/cohort.json')['rows']],scope='Scoring replay from frozen check receipts and reviews; no new model review or product execution.')
    if args.output:
        from pathlib import Path
        p=Path(args.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='pass',scoresRecomputed=len(result['rows']),officialScoresMatchFinal=True,inheritedRawFieldDiscrepancies=[{k:r[k] for k in ['runId','rawRecomputed','rawReported']} for r in result['rows'] if not r['rawFieldMatches']])))
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,OSError,AssertionError) as e:print('FAIL: '+str(e),file=sys.stderr);sys.exit(1)
