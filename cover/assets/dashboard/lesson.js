(function () {
  'use strict';
  const library = window.dashboardLibrary;
  function el(tag, className, text) { const node=document.createElement(tag); if(className) node.className=className; if(text) node.textContent=text; return node; }
  function go(index) { window.dispatchEvent(new CustomEvent('dashboard-page', {detail:index})); const heading=document.querySelector('.dash-heading');if(heading){heading.tabIndex=-1;heading.focus({preventScroll:true});} }
  function showMenus() { window.dispatchEvent(new CustomEvent('dashboard-page', {detail:{index:0,section:'menus'}})); }
  const starters=[
    {id:3,question:'อะไรใช้เวลามากที่สุด?',hint:'เปรียบเทียบรายการและจัดอันดับ',name:'กราฟแท่งแนวนอน'},
    {id:6,question:'งานเร็วขึ้นหรือช้าลง?',hint:'ดูการเปลี่ยนแปลงตามเวลา',name:'กราฟเส้น'},
    {id:19,question:'งบส่วนใหญ่ใช้กับอะไร?',hint:'ดูสัดส่วนของยอดรวมเดียว',name:'กราฟวงกลม'},
    {id:9,question:'ฝึกมาก คะแนนสูงขึ้นด้วยไหม?',hint:'ดูความสัมพันธ์ของสองตัวเลข',name:'กราฟจุด'},
    {id:16,question:'ยอดรวมแต่ละเดือนมาจากอะไร?',hint:'ดูยอดรวมพร้อมส่วนประกอบ',name:'กราฟแท่งซ้อน'}
  ];
  function nav(active) {
    const row=el('nav','dash-nav'); row.setAttribute('aria-label','เลือกหัวข้อ Dashboard');
    if(active!==0){const start=el('button','dash-mode','กลับหน้าเริ่มต้น');start.type='button';start.addEventListener('click',()=>go(0));const back=el('button','dash-mode','กราฟทั้ง 21 แบบ');back.type='button';back.addEventListener('click',showMenus);row.append(start,back);}
    const select=el('select','dash-select'); select.setAttribute('aria-label','เลือกกราฟหรือบทสรุป');
    library.pages.forEach((page,i)=>{const option=el('option','',page.label);option.value=i;option.selected=i===active;select.append(option);});
    select.addEventListener('change',()=>go(Number(select.value)));row.append(select);return row;
  }
  function promptPanel(title,prompt,createCopyButton) {
    const section=el('section','dash-prompt');const top=el('div','dash-prompt-head');top.append(el('h4','',title));
    const copy=createCopyButton(prompt);copy.textContent='Copy Prompt';copy.setAttribute('aria-label',`Copy Prompt: ${title}`);top.append(copy);section.append(top,el('pre','',prompt));return section;
  }
  function download(item) {
    const link=el('a','dash-download','ดาวน์โหลดข้อมูลตัวอย่าง CSV');
    link.download=`dashboard-practice-${String(item.id).padStart(2,'0')}.csv`;
    link.href=`assets/dashboard/data/dashboard-practice-${String(item.id).padStart(2,'0')}.csv`;return link;
  }
  window.createDashboardPage = function (page,createCopyButton) {
    const root=el('article','dash-page');
    if(page.type==='dashboard-intro') {
      root.classList.add('dash-home');
      const hero=el('header','dash-home-hero');hero.append(el('p','dash-kicker','Dashboard&Prompt / เริ่มจากงานของคุณ'),el('h2','dash-heading','อยากรู้คำตอบอะไรจากข้อมูล?'),el('p','dash-lead','เลือกคำถามที่ใกล้กับงาน แล้วลองทำกราฟหนึ่งรูปได้เลย'));
      const shortcuts=el('nav','dash-home-shortcuts');shortcuts.setAttribute('aria-label','ทางลัด Dashboard');const catalog=el('button','dash-mode','กราฟทั้ง 21 แบบ');catalog.type='button';catalog.addEventListener('click',showMenus);const workshop=el('button','dash-mode','สรุปการเลือกกราฟ');workshop.type='button';workshop.addEventListener('click',()=>go(22));shortcuts.append(catalog,workshop);hero.append(shortcuts);root.append(hero);
      const starterGrid=el('div','dash-starter-grid');starters.forEach(starter=>{
        const item=library.items.find(i=>i.id===starter.id);const button=el('button','dash-starter');button.type='button';button.addEventListener('click',()=>go(item.id));
        const image=el('img');image.src=item.image;image.alt='';image.width=780;image.height=560;
        const body=el('span','dash-starter-body');body.append(el('strong','',starter.question),el('span','dash-starter-hint',starter.hint),el('span','dash-starter-name',`${starter.name} · ${item.name}`),el('span','dash-starter-action','เปิดกราฟและ Prompt'));button.append(image,body);starterGrid.append(button);
      });root.append(starterGrid);
      const how=el('section','dash-home-how');how.append(el('h3','','ลองใช้งานได้ใน 3 ขั้นตอน'));const steps=el('ol');['เลือกคำถาม แล้วดูภาพและคำอธิบายของกราฟ','Copy Prompt ไปวางใน AI ที่วิเคราะห์ข้อมูลได้ แล้วกดส่ง','ตรวจตัวเลขและกราฟที่ได้ จากนั้นลองใช้กับไฟล์ของคุณ'].forEach(text=>steps.append(el('li','',text)));how.append(steps);root.append(how);
      const menus=el('section','dash-home-menus');const menuHeading=el('h3','dash-section-heading','เลือกจากกราฟทั้ง 21 แบบ');menuHeading.id='dashboardChartMenus';menuHeading.tabIndex=-1;menus.append(menuHeading,el('p','dash-start-note','กดชื่อกราฟเพื่อเปิดหน้าของแบบนั้น แต่ละหน้ามีภาพ คำอธิบาย และ Prompt พร้อมใช้'));
      const grid=el('div','dash-group-grid');library.groups.forEach(group=>{
        const section=el('section','dash-group');section.dataset.group=group.key;
        section.append(el('p','dash-kicker',group.name),el('h3','',group.thai),el('p','',group.question));
        library.items.filter(i=>i.group===group.key).forEach(item=>{const b=el('button','dash-link',`${item.id}. ${item.name}`);b.type='button';b.addEventListener('click',()=>go(item.id));section.append(b);});grid.append(section);
      });menus.append(grid);root.append(menus);
      return root;
    }
    if(page.type==='dashboard-workshop') {
      root.append(nav(22),el('p','dash-kicker','Dashboard&Prompt / บทสรุป'),el('h2','dash-heading','เลือกตัวเลขและกราฟให้ตรงกับคำถาม'),el('p','dash-lead','Dashboard คือหน้ารวมตัวเลขและกราฟ เลือกเฉพาะส่วนที่ช่วยตอบคำถามของงาน'));
      const example=el('div','dash-workshop-map');
      [
        ['KPI · ตัวเลขสำคัญ','ตอนนี้งานมากแค่ไหน?','ดูจำนวนคำขอ งานค้าง และเวลาปิดงาน'],
        ['Comparison · เปรียบเทียบ','ต้องเริ่มแก้ตรงไหน?','ใช้ Bar Chart จัดอันดับงานค้างแต่ละประเภท'],
        ['Trend · แนวโน้ม','ภาระงานเพิ่มหรือลด?','ใช้ Line Chart ดูจำนวนคำขอแต่ละสัปดาห์'],
        ['Distribution · การกระจาย','งานส่วนใหญ่ใช้เวลาเท่าไร?','ใช้ Histogram ดูช่วงเวลาที่ใช้ปิดงาน'],
        ['Composition · สัดส่วน','คำขอมาจากช่องทางไหน?','ใช้ Stacked 100% Column ดูสัดส่วน พร้อมจำนวนจริง'],
        ['Relationship · ความสัมพันธ์','งานมากขึ้น ใช้เวลานานขึ้นไหม?','ใช้ Scatter Chart ดูจำนวนคำขอกับเวลาปิดงาน']
      ].forEach(([name,q,c])=>{const block=el('section','dash-info');block.append(el('p','dash-kicker',name),el('h3','',q),el('p','',c));example.append(block);});
      root.append(example);return root;
    }
    const item=library.items.find(i=>i.id===page.number);const group=library.groups.find(g=>g.key===item.group);
    root.dataset.chart=item.id;root.append(nav(item.id),el('p','dash-kicker',`${group.name} / ${group.thai}`),el('h2','dash-heading',`${String(item.id).padStart(2,'0')} ${item.name}`),el('h3','dash-subtitle',item.title),el('p','dash-question',item.question));
    const layout=el('div','dash-layout');const figure=el('figure','dash-figure');const img=el('img');img.src=item.image;img.alt=`${item.name}: ${item.read}`;img.width=780;img.height=560;figure.append(img,el('figcaption','','ข้อมูลตัวอย่างสำหรับฝึก • ชื่อในกราฟใช้ภาษาอังกฤษให้อ่านชื่อคอลัมน์คู่กันได้'));
    const zoomButton=el('button','dash-zoom-button','ดูภาพกราฟขนาดเต็ม');zoomButton.type='button';
    const dialog=el('dialog','dash-zoom');dialog.setAttribute('aria-label',`ภาพขนาดเต็ม: ${item.name}`);
    const zoomHeader=el('div','dash-zoom-header');const close=el('button','dash-mode','ปิดภาพ');close.type='button';close.addEventListener('click',()=>dialog.close());zoomHeader.append(el('h3','',item.name),close);
    const zoomScroll=el('div','dash-zoom-scroll');zoomScroll.tabIndex=0;zoomScroll.setAttribute('aria-label','ภาพกราฟขนาดเต็ม เลื่อนซ้ายขวาเพื่อดู');const zoomImg=img.cloneNode();zoomScroll.append(zoomImg);
    dialog.append(zoomHeader,el('p','','บนมือถือเลื่อนภาพซ้าย–ขวาเพื่ออ่านตัวเลข'),zoomScroll);zoomButton.addEventListener('click',()=>dialog.showModal());figure.append(zoomButton,dialog);
    const explanation=el('div','dash-explanation');[['เลือกกราฟนี้เมื่อไร',item.why],['อ่านภาพอย่างไร',item.read],['จุดที่ต้องตรวจ',item.check]].forEach(([heading,text])=>{const s=el('section','dash-info');s.append(el('h4','',heading),el('p','',text));explanation.append(s);});layout.append(figure,explanation);root.append(layout);
    const data=el('details','dash-data');data.append(el('summary','','ดูข้อมูลที่ใช้ในภาพ / ดาวน์โหลด CSV'),el('pre','',item.csv),download(item));root.append(data);
    root.append(el('p','dash-instruction','ทดลอง: กด Copy Prompt ด้านล่าง แล้ววางใน AI ที่วิเคราะห์ข้อมูลได้ ข้อมูลตัวอย่างอยู่ในคำสั่งแล้ว ไม่ต้องแนบไฟล์ หากใช้ข้อมูลจริง ให้เลือกชุด “ใช้ไฟล์ของฉัน” และแนบ Excel/CSV ก่อนส่ง'));
    const modes=el('div','dash-modes');modes.setAttribute('role','group');modes.setAttribute('aria-label','เลือกชุด Prompt');
    const demo=el('button','dash-mode','ทดลองด้วยข้อมูลตัวอย่าง');const own=el('button','dash-mode','ใช้ไฟล์ของฉัน');demo.type=own.type='button';
    const panels=el('div','dash-prompt-panels');const demoPanel=promptPanel('Prompt ทดลองได้ทันที',item.demoPrompt,createCopyButton);const ownPanel=promptPanel('Prompt ใช้กับ Excel/CSV ของฉัน',item.ownPrompt,createCopyButton);ownPanel.hidden=true;
    function mode(isOwn){demo.setAttribute('aria-pressed',String(!isOwn));own.setAttribute('aria-pressed',String(isOwn));demoPanel.hidden=isOwn;ownPanel.hidden=!isOwn;}
    demo.addEventListener('click',()=>mode(false));own.addEventListener('click',()=>mode(true));mode(false);modes.append(demo,own);panels.append(demoPanel,ownPanel);root.append(modes,panels);
    root.append(el('p','dash-outcome','ผลที่ควรได้: กราฟพร้อมหน่วย ตารางตัวเลขที่ตรวจย้อนกลับได้ ข้อค้นพบ 2 ข้อ และรายการที่ควรตรวจต่อ 1 ข้อ กราฟที่ดูสวยแต่ค่าหรือหน่วยไม่ตรง ต้องแก้ก่อนใช้งาน'));
    return root;
  };
})();
