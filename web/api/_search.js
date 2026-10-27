// Book search for the voice agent. Generated from the same search code as index.html (lines "SEG" to "search").
"use strict";
const SEG=(typeof Intl!=="undefined"&&Intl.Segmenter)?new Intl.Segmenter("ta",{granularity:"grapheme"}):null;
const STOP_EN=new Set("what is are the a an of in on to and or for with by from how why does do did explain describe define definition meaning mean tell me about give short note write which who whom whose when where was were be been being this that these those it its as at into than then there their they them can could would should will shall may might difference differences between briefly detail details some any your you i we our please brief kindly sir madam mam teacher today doubt doubts quickly properly nicely clearly easily hello hi okay thanks thank sorry again student students exam".split(" "));
const STOP_TA=new Set(["என்றால்","என்ன","என்பது","என்பவை","யாவை","யாது","எது","எவை","ஏன்","எப்படி","எவ்வாறு","விளக்கு","விளக்குக","விளக்கவும்","விளக்கம்","பற்றி","கூறு","கூறுக","கூறவும்","சொல்","சொல்லு","சொல்லுங்கள்","என்று","மற்றும்","ஒரு","இது","அது","இந்த","அந்த","வேறுபாடு","வேறுபாடுகள்","வேறுபடுத்துக","என்னென்ன","எத்தனை","யார்","எங்கு","எப்போது","தருக","எழுதுக","எழுது","குறிப்பு","வரைக","என","எனப்படும்","ஆகும்","உள்ளன","உள்ளது","ஐயா","அம்மா","சார்","மேடம்","தயவுசெய்து","இன்று","வணக்கம்","நன்றி"]);
function graphemes(w){return SEG?[...SEG.segment(w)].map(x=>x.segment):[...w];}
function stem(w){
  if(/[\u0B80-\u0BFF]/.test(w)){ if(STOP_TA.has(w))return null; const g=graphemes(w); if(g.length<2)return null;
    return taPrefix(g,4); }
  if(STOP_EN.has(w)||w.length<3||/^\d+$/.test(w))return null;
  return w.replace(/ies$/,"y").replace(/(ss)es$/,"$1").replace(/([^su])s$/,"$1").replace(/(ing|ed)$/,"").replace(/(ation|ations)$/,"at");
}
// Tamil compounds are written both joined and apart ("மகரந்தச்சேர்க்கை" / "மகரந்தச் சேர்க்கை"):
// split a long Tamil word at a doubled-consonant joint so both parts are matched.
function splitTa(w){ const g=graphemes(w); if(g.length<7) return null;
  for(let i=g.length-3;i>=3;i--){ const a=g[i-1], b=g[i];
    if(a.length===2&&a[1]==="\u0BCD"&&b[0]===a[0]) return [g.slice(0,i).join(""), g.slice(i).join("")]; }
  return null; }
// Tamil words share a 4-letter root; long words also keep a 6-letter form so specific terms stay specific
function taPrefix(g,n){ const st=g.slice(0,Math.min(n,g.length)); while(st.length>2&&/\u0BCD$/.test(st[st.length-1]))st.pop(); return st.join(""); }
function toks(s){ const out=[]; (s.toLowerCase().match(/[\p{L}\p{M}\p{N}]+/gu)||[]).forEach(w=>{
    const st=stem(w); if(!st) return; out.push(st);
    if(/[\u0B80-\u0BFF]/.test(w)){ const g=graphemes(w);
      if(g.length>=8){ const l6=taPrefix(g,6); if(l6!==st) out.push(l6); }
      const sp=splitTa(w); if(sp){ const r=stem(sp[1]); if(r&&r!==st) out.push(r); } } });
  return out; }
function tidy(t){return t.replace(/\p{Co}/gu,"•").replace(/-\n(?=[a-z])/g,"").replace(/([^\n])\n(?!\n|•|\+|\d+[.)]|[A-Z][a-z]*:)/g,"$1 ").replace(/[ \t]+/g," ").replace(/\n{3,}/g,"\n\n").trim();}
// for searching: join wrapped lines of running text, but keep short label lines (figure labels, headings) apart
function tidyIdx(t){
  const L=t.replace(/\p{Co}/gu,"•").replace(/-\n(?=[a-z])/g,"").split("\n").map(x=>x.trim()); let out="";
  const isLabel=(x,next,prev)=>{ if(!x||x.length>=28||/[.,;:(=\-]$/.test(x))return false;
    // Tamil: a short line is a heading only when it stands alone (narrow book columns often hold just two words)
    const w=x.split(/\s+/); if(/[\u0B80-\u0BFF]/.test(x)) return w.length<=2&&!!next&&(!prev||/[.:?!)]$/.test(prev));
    return w.length<=4&&/^[A-Z0-9]/.test(x)&&!/\b(to|of|the|and|a|an|in|is|are|by|with|for|from|on|or)$/i.test(x)&&!!next&&/^[A-Z0-9•]/.test(next); };
  L.forEach((x,i)=>{ if(!x){out+="\n\n";return;} const prev=out.slice(-1);
    if(isLabel(x,L[i+1],L[i-1])) out+=(prev&&prev!=="\n"?"\n":"")+x+"\n"; else out+=(prev&&prev!=="\n"?" ":"")+x; });
  return out.replace(/[ \t]+/g," ").replace(/\n{3,}/g,"\n\n").trim();
}

function buildIndex(b){
  const chunks=[]; const df=new Map(); let total=0;
  const titles={}; b.chapters.forEach(c=>titles[c.u]=c.title);
  b.pages.forEach((p,pi)=>{
    const paras=tidyIdx(p.t).split(/\n\s*\n|\n(?=•)/).map(x=>x.trim()).filter(x=>x.length>0);
    let buf="";
    const push=()=>{ if(buf.trim().length<25){buf="";return;} const tk=toks(buf); if(!tk.length){buf="";return;}
      const tf=new Map(); tk.forEach(t=>tf.set(t,(tf.get(t)||0)+1)); tf.forEach((_,t)=>df.set(t,(df.get(t)||0)+1));
      chunks.push({pi,text:buf.trim(),tf,len:tk.length,title:new Set(toks(titles[p.u]||""))}); total+=tk.length; buf=""; };
    paras.forEach(x=>{ buf+=(buf?"\n":"")+x; if(buf.length>320)push(); }); push();
  });
  return {chunks,df,avg:total/Math.max(1,chunks.length)};
}
async function loadCatalog(){
  try{const r=await fetch("data/catalog.json");CATALOG=await r.json();}catch(e){CATALOG=[];}
  renderBooks(); return CATALOG;
}
async function loadBook(id){
  if(BOOKS[id])return BOOKS[id];
  const r=await fetch("data/books/"+id+".json"); const b=await r.json(); b.idx=null; BOOKS[id]=b; return b;
}
function booksFor(std,med){return CATALOG.filter(b=>b.std===std&&(!med||b.medium===med));}
const DEF0=/\b(is called|are called|is known as|are known as|is defined|refers to|is the process|are the|is a|is an)\b|என்பது|எனப்படும்|எனப்படுகிறது|என்று அழைக்கப்படுகிறது|ஆகும்/;
function splitSent(t){return t.replace(/\n+/g,"\u2029").split(/\u2029/).flatMap(x=>x.split(/(?<=[.!?।])\s+(?=[A-Z\u0B80-\u0BFF"'(•¾])|\s(?=\d+\.\d+(?:\.\d+)*\s+[A-Z\u0B80-\u0BFF])/)).map(x=>x.trim()).filter(x=>x.length>2);}
const NOISE=/Choose the correct|Evaluation|Answer the following|Fill in the blanks|Match the following|True or False|Multiple choice|சரியான விடையை|மதிப்பீடு|பொருத்துக|கோடிட்ட இடத்தை|சரியா தவறா|Learning Objectives|கற்றல் நோக்கங்கள்|Chapter Outline|Concept Map|ICT Corner|Scan the QR|QR code|பாட உள்ளடக்கம்|பாடஉள்ளடக்கம்|பாடச் சுருக்கம்|மதிப்பீடு|கருத்து வரைபடம்|இணையச் செயல்பாடு/i;
const SIDE=/Info bit|Activity|Do you know|More to know|Think|செயல்பாடு|உங்களுக்குத் தெரியுமா|மேலும் அறிந்துகொள்வோம்/i;
function sentScore(x,qt,idf,lead){
  x=x.replace(/^\s*\d+(\.\d+)*\s*/,"");
  const tk=toks(x); if(!tk.length)return 0; const set=new Set(tk); let s=0;
  const key=qt.reduce((a,t)=>idf(t)>idf(a)?t:a,qt[0]); const hasKey=set.has(key)||qt.length===1;
  qt.forEach(t=>{if(set.has(t))s+=idf(t);});
  // a definition: "<term> is/are/means ..." or "<term> என்பது ..." right at the start of the sentence
  const words=(x.replace(/\([^)]*\)/g,' ').match(/[\p{L}\p{M}\p{N}]+/gu)||[]).filter((w,i,a)=>i===0||w.toLowerCase()!==a[i-1].toLowerCase()).slice(0,6);
  if(/^["'‘“(]?[A-Z\u0B80-\u0BFF]/.test(x)) for(let i=0;i<Math.min(3,words.length-1);i++){
    const st=stem(words[i].toLowerCase());
    if(st&&qt.includes(st)){
      const nxt=words.slice(i+1,i+4).join(" ").toLowerCase();
      if(hasKey&&(/^(is|are|means|refers)\b/.test(nxt)||/\u0B8E\u0BA9\u0BCD\u0BAA\u0BA4\u0BC1|\u0B8E\u0BA9\u0BCD\u0BAA\u0BB5\u0BC8|\u0B8E\u0BA9\u0BAA\u0BCD\u0BAA\u0B9F\u0BC1\u0BB5\u0BA4\u0BC1/.test(nxt))){ s+=lead*((i===0||(i===1&&/^(the|a|an)$/i.test(words[0])))?2.5:1.0); }
      break;
    }
  }
  // "...is called a tissue" / "...known as ..." / "... எனப்படும்"
  const m=x.match(/\b(?:is|are)\s+(?:called|known as|termed|referred to as)\s+(?:an?\s+|the\s+)?([^,.;]{1,40})/i);
  if(m&&hasKey&&toks(m[1]).slice(0,3).includes(key)) s+=lead*3;
  for(const mm of x.replace(/\([^)]*\)/g," ").matchAll(/((?:[\p{L}\p{M}]+\s+){0,3}[\p{L}\p{M}]+)\s+(?:எனப்படும்|எனப்படுகிறது|என்று அழைக்கப்படுகிறது|என அழைக்கப்படுகிறது|என்று பெயர்)/gu)){
    const near=toks(mm[1].split(/\s+/).slice(-Math.max(2,qt.length)).join(' '));
    if(qt.every(t=>near.includes(t))){ s+=lead*3; break; } }
  { const em=x.match(/[\p{L}\p{M}]+\u0BC7\s+([\p{L}\p{M}]+)(?:\s+\u0B86\u0B95\u0BC1\u0BAE\u0BCD)?\s*[.]?\s*$/u); if(em&&qt.includes(stem(em[1]))) s+=lead*2.5; }   // "...கூட்டமே திசு (ஆகும்)."
  if(x.length<40) s*=0.5;
  if((x.match(/(^|\s)\(?[a-dA-D]\)\s/g)||[]).length>=2||/\b(Choose|Pick out|Fill in|Match the)\b/i.test(x)) s*=0.15;
  if(/\?\s*$/.test(x)||/^\(?[a-d]\)\s/.test(x)||/^\d+\.\s+[A-Z]/.test(x)&&/\b(Describe|Explain|Name|Write|What|Why|How|Define|Give|List|Mention|State)\b/.test(x)) s*=0.25;
  const letters=(x.match(/[\p{L}\p{M}]/gu)||[]).length; if(letters/x.length<0.7) s*=0.4;
  if((x.match(/(^|\s)\d+[.)]\s/g)||[]).length>=3) s*=0.4;
  return s;
}
function lev(a,b,max){ if(Math.abs(a.length-b.length)>max)return max+1; let prev=Array.from({length:b.length+1},(_,j)=>j);
  for(let i=1;i<=a.length;i++){ const cur=[i]; let lo=i; for(let j=1;j<=b.length;j++){ cur[j]=Math.min(prev[j]+1,cur[j-1]+1,prev[j-1]+(a[i-1]===b[j-1]?0:1)); if(cur[j]<lo)lo=cur[j]; } if(lo>max)return max+1; prev=cur; } return prev[b.length]; }
function search(b,q,deep){
  if(!b.idx)b.idx=buildIndex(b);
  const {chunks,df,avg}=b.idx; const N=chunks.length; let qt=[...new Set(toks(q))];
  if(!qt.length)return null;
  // words the book never uses: try a close spelling (same first letters), otherwise the book does not cover this
  if(!b.idx.keys)b.idx.keys=[...df.keys()];
  const fixed=[]; let missing=0;
  qt.forEach(t=>{ if(df.has(t)){fixed.push(t);return;}
    const pre=[...t].slice(0,Math.max(4,Math.min(6,[...t].length-1))).join("");
    let best=null,bn=0; b.idx.keys.forEach(k=>{ if(k.startsWith(pre)){const n=df.get(k); if(n>bn){bn=n;best=k;}} });
    if(!best){ // misheard word: closest word in this book (one letter off; two for long English words)
      const g=graphemes(t), latin=/^[a-z]/.test(t), max=latin&&t.length>=9?2:1; let bd=max+1;
      // only long words: short ones are usually real everyday words that are simply not in this book
      if(latin?t.length>=7:g.length>=5) b.idx.keys.forEach(k=>{ const kg=graphemes(k); if(Math.abs(kg.length-g.length)>max)return; const d=lev(g,kg,max); if(d<bd||(d===bd&&best&&df.get(k)>df.get(best))){bd=d;best=k;} });
      if(bd>max)best=null; }
    if(best)fixed.push(best); else if([...t].length>=4) missing++; });
  qt=[...new Set(fixed)];
  if(!qt.length||missing>0)return null;
  const idf=t=>{const n=df.get(t)||0; return n?Math.log(1+(N-n+.5)/(n+.5)):0;};
  const lead=Math.max(...qt.map(idf));
  const k1=1.3,bb=0.7; const cand=[];
  chunks.forEach((c,ci)=>{
    let s=0,hit=0;
    qt.forEach(t=>{const f=c.tf.get(t)||0; if(!f&&!c.title.has(t))return; const w=idf(t);
      if(f){hit++; s+=w*f*(k1+1)/(f+k1*(1-bb+bb*c.len/avg));} if(c.title.has(t))s+=w*0.6;});
    if(!hit)return;
    s*=(0.5+0.5*hit/qt.length);
    if(NOISE.test(c.text))s*=0.35; else if(SIDE.test(c.text))s*=0.7;
    cand.push({ci,s,hit});
  });
  if(!cand.length)return null;
  cand.sort((a,b)=>b.s-a.s);
  let best=null;
  cand.slice(0,400).forEach(c=>{
    const sents=splitSent(chunks[c.ci].text); let bi=0,bs=-1;
    sents.forEach((x,i)=>{const v=sentScore(x,qt,idf,lead); if(v>bs){bs=v;bi=i;}});
    const titleAll=qt.every(t=>chunks[c.ci].title.has(t));
    const total=Math.log1p(c.s)*2+bs+(titleAll?lead*1.2:0);
    if(!best||total>best.total)best={...c,total,bi,sents};
  });
  if(!best||best.total<2.2||best.hit<1)return null;
  const c=chunks[best.ci]; const sents=best.sents; const bi=best.bi;
  let out=sents.slice(bi,bi+(deep?8:3));
  if(deep){ let j=best.ci+1; while(out.join(" ").length<900&&j<chunks.length&&chunks[j].pi-c.pi<=1&&!NOISE.test(chunks[j].text)){ out=out.concat(splitSent(chunks[j].text)); j++; } out=out.slice(0,12); }
  else if(out.join(" ").length>420) out=out.slice(0,2);
  const page=b.pages[c.pi]; const ch=b.chapters.find(x=>x.u===page.u);
  // start the answer where the definition / section actually begins
  let f=out[0]; const di=f.search(/Definition\s*:|வரையறை\s*:/i); if(di>0)f=f.slice(di).replace(/^\S+\s*:\s*/,"");
  else { const secs=[...f.matchAll(/\b\d+(\.\d+)+\s+/g)]; if(secs.length){const last=secs[secs.length-1]; const rest=f.slice(last.index+last[0].length); if(qt.some(t=>toks(rest).includes(t))) f=rest;} }
  out[0]=f.replace(/^\s*\d+(\.\d+)+\s*/,"").replace(/^(\S+)\s+\1\b/i,"$1");
  out=out.filter((x,i)=>i===0||!(/\|/.test(x)||/^(Table|Figure|Fig\.|அட்டவணை|படம்)\s*\d/i.test(x)||/\b(1[5-9]|20)\d\d\b.*\b(1[5-9]|20)\d\d\b/.test(x)));
  return {text:out.join(" ").replace(/\s+\d{1,3}\s*$/,"").replace(/^•\s*/,"").replace(/\s+•\s*/g," "),book:b,page,ch,score:best.total};
}
module.exports={search,toks};
