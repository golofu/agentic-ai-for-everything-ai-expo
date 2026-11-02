(() => {
 'use strict';
 const stage=document.getElementById('stage'),prompt=document.getElementById('prompt'),full=prompt.textContent;
 const parcel=document.getElementById('parcel'),cursor=document.getElementById('cursor');
 const copy=document.getElementById('copy'),status=document.getElementById('copy-status');
 function fit(){stage.style.transform=`translate(-50%,-50%) scale(${Math.min(innerWidth/1920,innerHeight/1080)})`;}
 addEventListener('resize',fit);fit();
 for(let i=0;i<9;i++){const h=document.createElement('div');h.className='hole';h.style.top=(78+i*118)+'px';document.getElementById('holes').append(h);}
 const raw=new URLSearchParams(location.search).get('t');let frame=0;
 function seek(sec){
  const t=Math.max(0,Math.min(sec,8));
  const x=t<1.4?350+550*t/1.4:t<5.5?900:900+610*Math.min(1,(t-5.5)/1.5);
  parcel.setAttribute('transform',`translate(${x} 225)`);
  const count=Math.floor(full.length*Math.max(0,Math.min(1,(t-1.4)/3.6)));
  prompt.textContent=full.slice(0,count);prompt.style.minHeight='220px';
  const target=copy.offsetTop;
  cursor.style.transform=`translate(${t<4.8?30*(1-t/4.8):0}px,${target-550+15}px) scale(${t>4.8&&t<5.2?.8:1})`;
  copy.classList.toggle('clicked',t>4.8&&t<5.2);
 }
 function play(){cancelAnimationFrame(frame);status.textContent='';const start=performance.now();function tick(now){const sec=(now-start)/1000;seek(sec);if(sec<8)frame=requestAnimationFrame(tick);}frame=requestAnimationFrame(tick);}
 document.getElementById('replay').addEventListener('click',play);
 copy.addEventListener('click',async()=>{
  let ok=false;
  try{await navigator.clipboard.writeText(full);ok=true;}catch{
   const ta=document.createElement('textarea');ta.value=full;ta.style.cssText='position:fixed;top:0;left:0;opacity:0';document.body.append(ta);ta.select();
   try{ok=document.execCommand('copy');}catch{}ta.remove();copy.focus();
  }
  status.textContent=ok?'คัดลอกคำสั่งแล้ว':'คัดลอกไม่สำเร็จ กรุณาเลือกข้อความแล้วคัดลอกเอง';
  status.style.color=ok?'#216640':'#a52b20';
 });
 document.querySelectorAll('.copy-result').forEach(button=>button.addEventListener('click',async()=>{
  const message=button.parentElement.querySelector('.result-status');let ok=false;
  try{const response=await fetch(button.dataset.url);if(!response.ok)throw new Error('download');const text=await response.text();
   try{await navigator.clipboard.writeText(text);ok=true;}catch{const ta=document.createElement('textarea');ta.value=text;document.body.append(ta);ta.select();try{ok=document.execCommand('copy');}catch{}ta.remove();button.focus();}
  }catch{}
  message.textContent=ok?'คัดลอกผลลัพธ์แล้ว':'คัดลอกไม่สำเร็จ กรุณาดาวน์โหลดไฟล์แล้วคัดลอกเอง';
 }));
 const tabs=[...document.querySelectorAll('[data-app]')];
 function select(tab){tabs.forEach(b=>{const active=b===tab;b.setAttribute('aria-selected',String(active));b.tabIndex=active?0:-1;document.getElementById(b.dataset.app).hidden=!active;});}
 tabs.forEach((b,i)=>{b.addEventListener('click',()=>select(b));b.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();e.stopPropagation();const j=e.key==='Home'?0:e.key==='End'?1:1-i;select(tabs[j]);tabs[j].focus();}});});
 const dialog=document.getElementById('image-dialog');
 document.querySelectorAll('.shot').forEach(b=>b.addEventListener('click',()=>{dialog.querySelector('img').src=b.dataset.image;dialog.showModal();}));
 document.getElementById('close-dialog').addEventListener('click',()=>dialog.close());
 window.exampleMotion={seek,play};
 document.fonts.ready.then(()=>{if(raw!==null&&Number.isFinite(+raw))seek(+raw);else if(matchMedia('(prefers-reduced-motion: reduce)').matches)seek(99);else play();});
})();
