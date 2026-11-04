"""Make the fictional sample inputs for the portfolio demo (ละออ, owner of บ้านละมุน).
python make-inputs.py   (needs python-docx + playwright with Chrome)
Writes: ประวัติ-ละออ.docx, ละออ.jpg (illustrated avatar, not a real person), 3 product photos, and
reference-style.jpg (screenshot of the trainer's own portfolio, used as the style reference).
"""
import pathlib

from docx import Document
from docx.shared import Pt
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
PROFILE = HERE.parents[2] / "profile-site" / "index.html"

doc = Document()
st = doc.styles["Normal"]; st.font.name = "Tahoma"; st.font.size = Pt(11)
doc.add_heading("ประวัติ: ละออ ใจงาม (เจ้าของร้านบ้านละมุน)", 1)
for line in [
    "ร้านบ้านละมุน (BAAN LAMUN) ขายของใช้บนโต๊ะทำงาน: ขวดน้ำ แผ่นรองโต๊ะ กระเป๋าใส่สายชาร์จ",
    "เปิดร้านปี 2565 ขายออนไลน์ (Facebook, LINE OA, Shopee) และขายส่งให้บริษัทเป็นของขวัญพนักงาน",
    "ทีม 5 คน: ละออ (เจ้าของ), อร (ขายองค์กร), บอย (คลัง), แพร (บัญชี), นิว (การตลาด)",
]:
    doc.add_paragraph(line)
doc.add_heading("ตัวเลขผลงาน", 2)
for line in [
    "ลูกค้าองค์กร 42 บริษัท (ปี 2566–2569)",
    "ส่งของขวัญพนักงานรวม 12,000 ชิ้น",
    "รีวิวเฉลี่ย 4.8 จาก 5 (Shopee, 1,350 รีวิว)",
    "งานสกรีนโลโก้เสร็จใน 14 วัน",
]:
    doc.add_paragraph(line, style="List Bullet")
doc.add_heading("ผลงานเด่น", 2)
for line in [
    "ชุดของขวัญปีใหม่ ฟ้าใสโลจิสติกส์: 500 ชุด ขวดน้ำ + แผ่นรองโต๊ะ สกรีนโลโก้ ส่งทันก่อนงานเลี้ยง 3 วัน",
    "Desk Set คลินิกฟันใจดี: 120 ชุด สีประจำคลินิก ลูกค้าสั่งซ้ำรอบที่ 2",
    "Cable Pouch รุ่นพนักงานใหม่ เอเชียแพ็ค: 300 ชิ้น ใช้เป็นชุดต้อนรับพนักงานใหม่",
]:
    doc.add_paragraph(line, style="List Bullet")
doc.add_heading("บริการ", 2)
for line in [
    "ของขวัญองค์กรสกรีนโลโก้ (ขั้นต่ำ 50 ชิ้น)",
    "ชุดต้อนรับพนักงานใหม่ (Welcome Kit)",
    "ของใช้บนโต๊ะทำงาน ขายปลีกออนไลน์",
]:
    doc.add_paragraph(line, style="List Bullet")
doc.add_heading("ติดต่อ", 2)
doc.add_paragraph("LINE: @baanlamun   อีเมล: hello@baanlamun.example")
doc.save(HERE / "ประวัติ-ละออ.docx")

AVATAR = """<div style="width:800px;height:800px;background:linear-gradient(160deg,#f4ece4,#e7d8c9);display:grid;place-items:center">
<svg width="560" height="620" viewBox="0 0 280 310"><circle cx="140" cy="118" r="70" fill="#f2c9a8"/>
<path d="M70 110c0-50 30-78 70-78s70 28 70 78c-8-30-30-44-70-44s-62 14-70 44z" fill="#3b2a22"/>
<path d="M68 112c-6 40 2 70 10 82M212 112c6 40-2 70-10 82" stroke="#3b2a22" stroke-width="16" fill="none" stroke-linecap="round"/>
<circle cx="115" cy="122" r="6" fill="#3b2a22"/><circle cx="165" cy="122" r="6" fill="#3b2a22"/>
<path d="M118 152q22 18 44 0" stroke="#b5584a" stroke-width="6" fill="none" stroke-linecap="round"/>
<path d="M40 310c6-70 46-104 100-104s94 34 100 104z" fill="#2c6e5a"/></svg></div>"""

def product(name, body, label):
    return f"""<div style="width:1000px;height:750px;background:linear-gradient(170deg,#f6f1e8,#e9e1d3);display:grid;place-items:center;font-family:Tahoma">
<div style="text-align:center">{body}<div style="margin-top:28px;font:600 28px Tahoma;color:#5b4b3a;letter-spacing:2px">{label}</div></div></div>"""

SHOTS = {
    "ละออ.jpg": (AVATAR, 800, 800),
    "ผลงาน-ชุดของขวัญปีใหม่-ฟ้าใส.jpg": (product("set", '<div style="display:flex;gap:40px;align-items:flex-end"><div style="width:130px;height:330px;border-radius:40px;background:#2c6e5a;box-shadow:0 20px 40px #0003"></div><div style="width:420px;height:40px;border-radius:12px;background:#3d4a5c;box-shadow:0 20px 40px #0003"></div></div>', "GIFT SET · ฟ้าใสโลจิสติกส์ · 500 ชุด"), 1000, 750),
    "ผลงาน-deskset-คลินิกฟันใจดี.jpg": (product("desk", '<div style="width:600px;height:300px;border-radius:24px;background:#9fd3d6;box-shadow:0 20px 40px #0003;display:grid;place-items:center;font:700 40px Tahoma;color:#1d5f63">ใจดี DENTAL</div>', "DESK SET · คลินิกฟันใจดี · 120 ชุด"), 1000, 750),
    "ผลงาน-cablepouch-เอเชียแพ็ค.jpg": (product("pouch", '<div style="width:420px;height:260px;border-radius:30px;background:#c98a4b;box-shadow:0 20px 40px #0003;position:relative"><div style="position:absolute;top:30px;left:40px;right:40px;height:10px;border-radius:5px;background:#7a4f25"></div></div>', "CABLE POUCH · เอเชียแพ็ค · 300 ชิ้น"), 1000, 750),
}

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    for name, (html, w, h) in SHOTS.items():
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.set_content(f"<body style='margin:0'>{html}</body>")
        pg.screenshot(path=str(HERE / name), type="jpeg", quality=85)
        pg.close()
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto(PROFILE.as_uri()); pg.wait_for_timeout(2500)
    pg.screenshot(path=str(HERE / "reference-style.jpg"), type="jpeg", quality=80)
    b.close()
print("ok")
