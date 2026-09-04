"""Negative controls for the export verifier; source data is never changed."""
import copy,json
import verify,reevaluate
def main():
    read=verify.read;cohort=read('data/cohort.json');bad=copy.deepcopy(cohort);bad['rows'][1]['taskId']=bad['rows'][0]['taskId']
    verify.read=lambda p:bad if p=='data/cohort.json' else read(p)
    try:
        try:verify.cohort_check()
        except ValueError as e:assert str(e)=='Duplicate task ID'
        else:raise AssertionError('Duplicate task accepted')
    finally:verify.read=read
    row=cohort['rows'][0];bad_evaluation=copy.deepcopy(read(row['references']['evaluation']));bad_evaluation['checks'][0]['pointsAwarded']+=1
    saved=reevaluate.read;reevaluate.read=lambda p:bad_evaluation if p==row['references']['evaluation'] else read(p)
    try:
        try:reevaluate.evaluate(row)
        except ValueError as e:assert 'Check-level score differs' in str(e)
        else:raise AssertionError('Altered score accepted')
    finally:reevaluate.read=saved
    raw=b'a\r\nb\xff'
    assert verify.historical_hash(raw,'sha256-bytes')!=verify.historical_hash(raw,'sha256-node-utf8-replacement-lf')
    assert verify.git_tree([])=='4b825dc642cb6eb9a060e54bf8d69288fbee4904'
    print(json.dumps(dict(status='pass',duplicateTaskRejected=True,alteredScoreRejected=True,hashAlgorithmsDistinguished=True,emptyGitTreeVerified=True)))
if __name__=='__main__':main()
