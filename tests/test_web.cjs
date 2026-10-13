const assert = require('node:assert/strict');
const {calculate,classify}=require('../web/calculator.js');
function near(a,b){assert.ok(Math.abs(a-b)<1e-9, a+' != '+b);}
for(const v of Object.values(calculate(400,60,'hr','male').values)) near(v,400);
const high=calculate(350,100,'hr','male');
near(high.values.framingham,411.6);near(high.values.hodges,420);
near(high.values.bazett,350/Math.sqrt(.6));
near(high.values.fridericia,350/Math.cbrt(.6));
near(calculate(350,600,'rr','female').values.framingham,411.6);
assert.equal(classify(500,'male'),'dangerous');
assert.equal(classify(445,'male'),'borderline');
assert.equal(classify(465,'female'),'borderline');
for(const bad of [0,-1,NaN,Infinity,'oops'])assert.throws(()=>calculate(bad,75,'hr','male'));
assert.throws(()=>calculate(350,0,'hr','male'));
assert.throws(()=>calculate(350,600,'rr','other'));
console.log('Browser calculation tests passed');
