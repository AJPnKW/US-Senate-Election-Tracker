"use strict";
const STATES=[["AK","Alaska"],["IA","Iowa"],["KS","Kansas"],["ME","Maine"],["MI","Michigan"],["OH","Ohio"],["TX","Texas"],["NC","North Carolina"]];
const $=id=>document.getElementById(id);
const dash="—";
const pct=v=>typeof v==="number"&&Number.isFinite(v)?v.toFixed(1)+"%":dash;
const votes=v=>Number.isFinite(v)?v.toLocaleString():dash;
function cell(row,value){const td=document.createElement("td");td.textContent=value;row.append(td)}
function render(data,status){
  const map=new Map((data.races||[]).map(r=>[r.state,r]));
  const live=Boolean(data.source_validated&&data.races?.length);
  let called=0;
  const body=$("races");body.replaceChildren();
  for(const [code,name] of STATES){
    const r=map.get(code),tr=document.createElement("tr");
    const d=r?.candidates?.find(c=>c.party==="D");
    const rep=r?.candidates?.find(c=>c.party==="R");
    const total=(r?.candidates||[]).reduce((n,c)=>n+(Number.isFinite(c.votes)?c.votes:0),0);
    const dp=d&&total>0?100*d.votes/total:null;
    const rp=rep&&total>0?100*rep.votes/total:null;
    const leader=r?.called_party?"Called "+r.called_party:
      d&&rep&&d.votes!==rep.votes?(d.votes>rep.votes?"D":"R")+" +"+votes(Math.abs(d.votes-rep.votes)):
      r?"No declared winner":"No source coverage";
    if(r?.called_party)called++;
    [name,d?.name||dash,rep?.name||dash,
     pct(dp)+(d?" ("+votes(d.votes)+")":""),
     pct(rp)+(rep?" ("+votes(rep.votes)+")":""),
     pct(r?.reporting_pct),leader].forEach(v=>cell(tr,v));
    body.append(tr);
  }
  const hasCalls=(data.races||[]).some(r=>r.call_source);
  $("called").textContent=hasCalls?called+"/8":dash;
  $("uncalled").textContent=hasCalls?(8-called)+"/8":dash;
  $("flips").textContent=dash;
  $("balance").textContent="National control unavailable: this state-results feed does not cover all 35 Senate races or issue race calls.";
  $("feed-state").textContent=live?(data.stale?"STATE COUNTS — STALE":"OFFICIAL STATE COUNTS"):data.source_validated?"AWAITING STATE RESULTS":"DATA UNAVAILABLE";
  $("updated").textContent=data.updated_at?
    "State counts as of: "+data.updated_at+" · Source: Open America · "+map.size+"/8 monitored races covered":
    "Source: official state election offices via Open America · No validated counts yet";
  $("error").textContent=status?.error||"";
  $("checked").textContent=status?.checked_at?"Last collection attempt: "+status.checked_at:"";
  $("feed-state").parentElement.classList.toggle("error",!live||!!status?.error||!!data.stale);
}
async function readJson(path){const r=await fetch(path+"?t="+Date.now(),{cache:"no-store"});if(!r.ok)throw Error(path+": HTTP "+r.status);return r.json()}
function convertPublic(payload){
  if(!payload||payload.api!==1||payload.year!==2026||String(payload.office).toLowerCase()!=="senate"||!payload.races||typeof payload.races!=="object")throw Error("Unexpected public-feed schema");
  const races=Object.entries(payload.races).filter(([state,r])=>STATES.some(s=>s[0]===state)&&r&&Array.isArray(r.cands)).map(([state,r])=>({
    state,reporting_pct:typeof r.pct_in==="number"?r.pct_in:null,called_party:null,
    candidates:r.cands.filter(c=>typeof c.n==="string"&&Number.isSafeInteger(c.v)&&c.v>=0).map(c=>({name:c.n,party:["D","R","I"].includes(c.p)?c.p:"O",votes:c.v}))
  })).filter(r=>r.candidates.length);
  return {source_validated:true,source:"Official state election offices via Open America",updated_at:payload.as_of||null,stale:Boolean(payload.stale),races};
}
async function refresh(){
  let snapshot=null,status=null;
  try{[snapshot,status]=await Promise.all([readJson("data/results.json"),readJson("data/fetch_status.json")])}catch(e){status={error:"GitHub snapshot unavailable: "+e.message}}
  try{
    const url="https://openamerica.io/elections/results.json?year=2026&office=Senate";
    const response=await fetch(url,{cache:"no-store",credentials:"omit"});
    if(!response.ok)throw Error("HTTP "+response.status);
    const direct=convertPublic(await response.json());
    if(direct.races.length){render(direct,{checked_at:new Date().toISOString(),error:direct.stale?"Public state feed is stale":null});return}
    if(snapshot?.races?.length){render(snapshot,{...status,error:"Direct public feed returned no monitored races; showing saved snapshot"});return}
    render(direct,{checked_at:new Date().toISOString(),error:"No monitored state counts available in public feed yet"});return;
  }catch(e){
    if(snapshot){render(snapshot,{...status,error:"Direct public feed unavailable: "+e.message+(status?.error?" · "+status.error:"")});return}
    render({races:[],source_validated:false},{error:"No results source available: "+e.message});
  }
}
$("refresh").addEventListener("click",refresh);refresh();setInterval(refresh,60000);
