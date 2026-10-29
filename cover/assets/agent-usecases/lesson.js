(function () {
  "use strict";
  const library = window.agentUsecaseLibrary;
  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  window.createAgentUsecasePage = function (page, createCopyButton) {
    const panel = el("section", "agent-page");
    const header = el("header", "agent-page-header");
    const heading = el("div");
    heading.append(el("p", "agent-page-kicker", `USECASE FOR AI AGENTS · ${page.number} / 6`), el("h3", "", page.heading), el("p", "agent-page-intro", page.intro));
    header.append(heading);
    const layout = el("div", "agent-layout");
    const list = el("nav", "agent-case-list");
    list.setAttribute("aria-label", `เลือกงานในหมวด ${page.heading}`);
    const mobileSelect = el("select", "agent-case-select");
    mobileSelect.setAttribute("aria-label", `เลือก Usecase ในหมวด ${page.heading}`);
    const detail = el("article", "agent-detail");
    detail.tabIndex = -1;
    const items = page.ids.map(id => library.cases.find(item => item.id === id));

    function showCase(item, moveFocus = false) {
      mobileSelect.value = item.id;
      [...list.children].forEach(button => button.setAttribute("aria-pressed", String(button.dataset.case === item.id)));
      detail.replaceChildren();
      detail.dataset.case = item.id;
      const top = el("header", "agent-detail-header");
      const title = el("div");
      title.append(el("h4", "", item.title), el("p", "agent-tool", `เครื่องมือสำหรับงานนี้: ${item.tool}`));
      top.append(title);

      const preparation = el("div", "agent-preparation");
      // 1. ใส่ — folder and files in one card; real Word/PDF/Excel files, the .md names are only samples
      const folder = el("section", "agent-section");
      const h1 = el("h5", "", "ใส่ · สร้างโฟลเดอร์แล้วใส่ไฟล์ของคุณ"); h1.dataset.step = "1"; folder.append(h1);
      const steps = el("ol", "agent-steps");
      [`สร้างโฟลเดอร์ใหม่ชื่องานนี้ เช่น ${item.folder} แล้วเปิดให้ AI เข้าถึง`, "ใส่ไฟล์จริงของคุณตามรายการด้านล่าง เป็น Word, PDF, Excel หรือรูปก็ได้", "ชื่อไฟล์ไม่ต้องตรงกับตัวอย่าง แค่แก้ชื่อใน Prompt ให้ตรงกับไฟล์ของคุณ"].forEach(text => steps.append(el("li", "", text)));
      folder.append(steps);
      const fileList = el("dl", "agent-file-list");
      item.files.forEach(file => {
        const row = el("div", "agent-file-row");
        const sample = el("small", "agent-file-sample", `ตัวอย่าง: ${file}`);
        const dt = el("dt", "", library.fileDescriptions[file].split(":")[0]);
        const dd = el("dd", "", library.fileDescriptions[file].includes(":") ? library.fileDescriptions[file].split(":").slice(1).join(":").trim() : "");
        dd.append(sample);
        row.append(dt, dd);
        fileList.append(row);
      });
      folder.append(fileList);
      preparation.append(folder);

      // 2. สั่ง
      const prompt = el("section", "agent-section agent-prompt");
      const promptHeading = el("div", "agent-prompt-header");
      const copy = createCopyButton(item.prompt);
      copy.textContent = "คัดลอก Prompt"; copy.setAttribute("aria-label", `คัดลอก Prompt ${item.title}`);
      const h3 = el("h5", "", "สั่ง · Prompt พร้อมใช้"); h3.dataset.step = "2"; promptHeading.append(h3, copy);
      prompt.append(promptHeading, el("pre", "", item.prompt));

      // 3. ต่อด้วย — README.md that logs what was done in this folder
      const readmePrompt = `สร้างไฟล์ README.md ในโฟลเดอร์นี้ เพื่อบันทึกการทำงานของโฟลเดอร์นี้โดยเฉพาะ ใส่หัวข้อ งานนี้คืออะไร / ไฟล์ต้นทางที่ใช้ / ไฟล์ผลงานที่ได้และอยู่ที่ไหน / วันที่ทำ / สิ่งที่ต้องทำต่อหรือต้องให้คนตรวจ ถ้ามี README.md อยู่แล้วให้เพิ่มต่อท้ายเป็นรายการใหม่ ห้ามเขียนทับของเดิม`;
      const readme = el("section", "agent-section agent-readme");
      const readmeHeading = el("div", "agent-prompt-header");
      const copyReadme = createCopyButton(readmePrompt);
      copyReadme.textContent = "คัดลอก Prompt"; copyReadme.setAttribute("aria-label", "คัดลอก Prompt สร้าง README.md");
      const h4 = el("h5", "", "ต่อด้วย · สร้าง README.md บันทึกงานของโฟลเดอร์นี้"); h4.dataset.step = "3"; readmeHeading.append(h4, copyReadme);
      readme.append(readmeHeading, el("p", "agent-file-note", "พอ AI ทำงานเสร็จ ส่งคำสั่งนี้ต่อในแชตเดียวกัน ครั้งหน้ากลับมาเปิดโฟลเดอร์จะรู้ทันทีว่าทำอะไรไปแล้ว"), el("pre", "", readmePrompt));

      // 4. ได้
      const results = el("section", "agent-section agent-results");
      const h5 = el("h5", "", "ได้ · ผลลัพธ์ที่ควรได้"); h5.dataset.step = "4"; results.append(h5);
      const resultFiles = el("ul");
      item.results.forEach(file => resultFiles.append(el("li", "", file)));
      resultFiles.append(el("li", "", "README.md บันทึกงานของโฟลเดอร์นี้"));
      results.append(resultFiles, el("p", "agent-result-example", item.example));
      detail.append(top, preparation, prompt, readme, results);
      if (moveFocus && window.matchMedia("(max-width: 900px)").matches) detail.focus({ preventScroll: false });
    }
    items.forEach(item => {
      const option = el("option", "", `${String(item.number).padStart(2, "0")} · ${item.title}`);
      option.value = item.id;
      mobileSelect.append(option);
      const button = el("button", "agent-case-button");
      button.type = "button";
      button.dataset.case = item.id;
      button.setAttribute("aria-pressed", "false");
      button.append(el("span", "", String(item.number).padStart(2, "0")), document.createTextNode(item.title));
      button.addEventListener("click", () => showCase(item, true));
      list.append(button);
    });
    mobileSelect.addEventListener("change", () => showCase(items.find(item => item.id === mobileSelect.value)));
    layout.append(mobileSelect, list, detail);
    panel.append(header, layout);
    showCase(items[0]);
    return panel;
  };
})();
