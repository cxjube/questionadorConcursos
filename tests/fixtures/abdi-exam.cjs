'use strict';
// Never loaded by docs/. Creates a private, explicitly synthetic quota fixture.
module.exports=function addInstitutionalFixture(data){
 const role='abdi-comunicacao-marketing',copy=x=>JSON.parse(JSON.stringify(x));
 const ids=new Set(data.syllabusItems.filter(s=>s.roleId===role && s.block==='institutional').map(s=>s.id));
 data.mappings=data.mappings.filter(m=>!ids.has(m.syllabusItemId));
 const template=data.questions.find(q=>q.type==='multiple_choice'),key=data.answerKeys.find(k=>k.id===template.answerKeyId);let n=0;
 for(const quota of data.scoringRules.find(r=>r.roleId===role).blocks[1].distribution){
  const topic=data.topics.find(t=>t.disciplineId===quota.disciplineId && ids.has(t.id));
  for(let i=0;i<quota.questionCount;i++){
   const id='synthetic-institutional-test-'+(++n),q=copy(template);q.id=id;q.stem='SYNTHETIC TEST FIXTURE ONLY '+n;q.contextIds=[];q.answerKeyId=id+'-key';q.origin.number=1000+n;
   data.questions.push(q);data.answerKeys.push({...copy(key),id:q.answerKeyId,questionId:id});data.mappings.push({id:id+'-mapping',questionId:id,syllabusItemId:topic.id,status:'confirmed'});
  }
 }
 return data;
};
