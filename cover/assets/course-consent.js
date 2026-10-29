// This acknowledgment is remembered in this browser; it is not authentication.
(() => {
  "use strict";

  const version = "2026-10-14";
  const storageKey = "gen-ai-space:ai-for-work:copyright-acknowledgment";
  const menuUrl = new URL("menu.html", window.location.href);

  function hasAcknowledgment() {
    for (const name of ["localStorage", "sessionStorage"]) {
      try {
        const record = JSON.parse(window[name].getItem(storageKey));
        if (record?.version === version && typeof record.acknowledgedAt === "string") return true;
      } catch {
        // A blocked store or invalid record must not skip acknowledgment.
      }
    }
    return false;
  }

  function rememberAcknowledgment() {
    const record = JSON.stringify({ version, acknowledgedAt: new Date().toISOString() });
    for (const name of ["localStorage", "sessionStorage"]) {
      try {
        window[name].setItem(storageKey, record);
        if (window[name].getItem(storageKey) === record) return true;
      } catch {
        // Session storage can still work when persistent storage is blocked.
      }
    }
    return false;
  }

  function destination() {
    const requested = new URLSearchParams(window.location.search).get("returnTo");
    if (requested) {
      try {
        const target = new URL(requested, menuUrl);
        if (target.origin === menuUrl.origin && target.pathname === menuUrl.pathname) return target.href;
      } catch {
        // Only allow the course menu, with its original query and lesson hash.
      }
    }
    return menuUrl.href;
  }

  if (window.location.pathname === menuUrl.pathname) {
    if (!hasAcknowledgment()) {
      document.documentElement.classList.add("course-awaiting-consent");
      const coverUrl = new URL("index.html", window.location.href);
      coverUrl.searchParams.set("returnTo", `menu.html${window.location.search}${window.location.hash}`);
      coverUrl.hash = "copyright-notice";
      window.location.replace(coverUrl.href);
    }
    return;
  }

  function initializeCover() {
    const start = document.getElementById("courseStart");
    const accept = document.getElementById("acceptCopyright");
    const continueLink = document.getElementById("continueCourse");
    const status = document.getElementById("copyrightStatus");
    if (!start || !accept || !continueLink || !status) return;

    function updateAcknowledgedState() {
      start.href = destination();
      accept.hidden = true;
      continueLink.href = destination();
      continueLink.hidden = false;
      status.textContent = "รับทราบแล้ว สามารถเข้าเรียนได้โดยไม่ต้องกดตกลงซ้ำในเบราว์เซอร์นี้";
    }

    if (hasAcknowledgment()) updateAcknowledgedState();
    else accept.disabled = false;

    accept.addEventListener("click", () => {
      if (!rememberAcknowledgment()) {
        status.textContent = "ยังบันทึกการรับทราบไม่ได้ กรุณาอนุญาตการจัดเก็บข้อมูลเว็บไซต์ในเบราว์เซอร์ แล้วกดตกลงอีกครั้ง";
        return;
      }
      updateAcknowledgedState();
      window.location.assign(destination());
    });

    window.addEventListener("pageshow", () => {
      if (hasAcknowledgment()) updateAcknowledgedState();
      else {
        start.href = "#copyright-notice";
        accept.hidden = false;
        accept.disabled = false;
        continueLink.hidden = true;
        status.textContent = "กรุณาอ่านคำเตือนและกดตกลงก่อนเข้าเรียนครั้งแรก";
      }
    });

    window.addEventListener("storage", () => {
      if (hasAcknowledgment()) updateAcknowledgedState();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeCover, { once: true });
  } else initializeCover();
})();
