(function (root) {
'use strict';
function positive(value,name) {
 const n=Number(value);
 if (!Number.isFinite(n) || n<=0) throw new Error(name+' must be a finite positive number');
 return n;
}
function classify(qtc,sex) {
 if (sex!=='male' && sex!=='female') throw new Error('Select male or female thresholds');
 if(qtc>=500) return 'dangerous';
 const normal=sex==='female'?460:440, upper=sex==='female'?470:450;
 return qtc<normal?'normal':qtc<=upper?'borderline':'prolonged';
}
function calculate(qtInput,rateInput,rateType,sex) {
 if(rateType!=='hr' && rateType!=='rr') throw new Error('Invalid rate input');
 const qt=positive(qtInput,'QT'),rate=positive(rateInput,'Rate');
 const rr=rateType==='hr'?60000/rate:rate,hr=60000/rr,s=rr/1000;
 const values={bazett:qt/Math.sqrt(s),fridericia:qt/Math.cbrt(s),framingham:qt+154*(1-s),hodges:qt+1.75*(hr-60)};
 for(const v of Object.values(values)) positive(v,'QTc');
 return {qt,rr,hr,values,classification:classify(values.bazett,sex)};
}
const api=Object.freeze({calculate,classify});
if(typeof module!=='undefined' && module.exports) module.exports=api;
root.QTC=api;
})(typeof window!=='undefined'?window:globalThis);
