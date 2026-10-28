'use strict';
// Isolated synthetic engine fixture only. Never loaded or published by docs/.
module.exports = function addCGUFixture(data) {
  const copy = x => JSON.parse(JSON.stringify(x)), role = 'synthetic-cgu-ce', contest = 'synthetic-cgu-contest';
  const template = data.questions.find(q=>q.type==='true_false');
  const key = data.answerKeys.find(k=>k.id===template.answerKeyId), oldRule = data.scoringRules[0];
  data.contests.push({...copy(data.contests[0]),id:contest,title:'SYNTHETIC CGU TEST ONLY'});
  data.roles.push({...copy(data.roles[0]),id:role,contestId:contest,title:'SYNTHETIC CGU TEST ONLY'});
  const blocks = [
    {id:'basic',label:'Conhecimentos básicos',questionCount:40,correct:1,minimumScore:8},
    {id:'complementary',label:'Conhecimentos complementares',questionCount:40,correct:1,minimumScore:12},
    {id:'specific',label:'Conhecimentos específicos',questionCount:90,correct:2,minimumScore:54},
  ];
  data.scoringRules.push({...copy(oldRule),id:'synthetic-cgu-rule',roleId:role,durationMinutes:300,minimumTotalScore:78,
    blocks:blocks.map(b=>({...b,questionType:'true_false',incorrect:-b.correct,blank:0,doubleMarked:0,annulledPolicy:'credit',annulledPoints:null}))});
  let n=0;
  for (const block of blocks) {
    const id='synthetic-cgu-'+block.id;
    data.disciplines.push({id,label:block.label});
    data.topics.push({id,disciplineId:id,label:'SYNTHETIC PROGRAM TEST ONLY',parentId:null});
    data.syllabusItems.push({id,topicId:id,noticeId:oldRule.noticeId,roleId:role,block:block.id,status:'confirmed',number:'1',reference:'SYNTHETIC TEST ONLY'});
    for (let i=0;i<block.questionCount;i++) {
      const q=copy(template);q.id='synthetic-cgu-question-'+(++n);q.stem='SYNTHETIC TEST FIXTURE ONLY '+n;q.contextIds=[];q.answerKeyId=q.id+'-key';q.origin.number=1000+n;
      data.questions.push(q);data.answerKeys.push({...copy(key),id:q.answerKeyId,questionId:q.id});
      data.mappings.push({id:q.id+'-mapping',questionId:q.id,syllabusItemId:id,status:'confirmed'});
    }
  }
  return data;
};
