'use strict';
const el=id=>document.getElementById(id);
const form=el('form'),output=el('output'),download=el('download');
let current=null;
function clear(){current=null;output.hidden=true;download.disabled=true;el('error').textContent='';}
el('type').addEventListener('change',function(){
 const rr=this.value==='rr';
 el('rate-label').textContent=rr?'RR interval':'Heart rate';
 el('rate-unit').textContent=rr?'(ms)':'(bpm)';
 el('rate').value=rr?'800':'75';
 clear();
});
for(const id of ['qt','rate','sex']) el(id).addEventListener('input',clear);
form.addEventListener('submit',event=>{
 event.preventDefault();clear();
 if(!form.reportValidity()) return;
 try{
   const sex=el('sex').value;
   const data=QTC.calculate(el('qt').value,el('rate').value,el('type').value,sex);
   for(const [key,value] of Object.entries(data.values)) el(key).textContent=value.toFixed(1)+' ms';
   el('class').textContent=data.classification[0].toUpperCase()+data.classification.slice(1)+' (Bazett)';
   el('class').className='classification '+data.classification;
   el('derived').textContent='RR '+data.rr.toFixed(1)+' ms · HR '+data.hr.toFixed(1)+' bpm';
   output.hidden=false;download.disabled=false;current={...data,sex};
 }catch(error){el('error').textContent=error.message;}
});
download.addEventListener('click',()=>{
 if(!current) return;
 const {qt,rr,hr,sex,values,classification}=current;
 const heads=['qt_ms','rr_ms','hr_bpm','sex','qtc_bazett','qtc_fridericia','qtc_framingham','qtc_hodges','classification'];
 const cells=[qt,rr,hr,sex,values.bazett,values.fridericia,values.framingham,values.hodges,classification];
 const csv=heads.join(',')+'\r\n'+cells.map(v=>typeof v==='number'?v.toFixed(1):v).join(',')+'\r\n';
 const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
 const link=document.createElement('a');link.href=url;link.download='qtc-results.csv';link.click();
 setTimeout(()=>URL.revokeObjectURL(url),1000);
});
