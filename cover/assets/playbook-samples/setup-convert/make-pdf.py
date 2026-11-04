import sys
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
pdfmetrics.registerFont(TTFont('T','C:/Windows/Fonts/tahoma.ttf'))
pdfmetrics.registerFont(TTFont('TB','C:/Windows/Fonts/tahomabd.ttf'))
pdfmetrics.registerFontFamily('T',normal='T',bold='TB')
st=lambda n,s,f='T',**k: ParagraphStyle(n,fontName=f,fontSize=s,leading=s*1.5,**k)
H=st('h',20,'TB'); H2=st('h2',13,'TB',spaceBefore=10,spaceAfter=4); B=st('b',10.5); C=st('c',10); CR=st('cr',10,alignment=2); CB=st('cb',10,'TB')
out=sys.argv[1]
d=SimpleDocTemplate(out,pagesize=A4,leftMargin=40,rightMargin=40,topMargin=40,bottomMargin=40,title="ใบเสนอราคา QT-2611-003")
S=[Paragraph("ใบเสนอราคา (QUOTATION)",H),
Paragraph("บ้านละมุน (BAAN LAMUN) ร้านของใช้บนโต๊ะทำงาน<br/>เลขที่เอกสาร QT-2611-003 &nbsp;&nbsp; วันที่ 2 พฤศจิกายน 2569 &nbsp;&nbsp; ยืนราคา 30 วัน",B),
Paragraph("1. ข้อมูลลูกค้า",H2),
Paragraph("ลูกค้า: บริษัท เอเชียแพ็ค จำกัด &nbsp; ผู้ติดต่อ: คุณวรินทร์ จัดซื้อ<br/>ผู้เสนอราคา: อร (ฝ่ายขายองค์กร) บ้านละมุน",B),
Paragraph("2. รายการสินค้า",H2)]
rows=[["ลำดับ","รายการ","จำนวน","ราคาต่อหน่วย (บาท)","รวม (บาท)"],
["1","ชุดของขวัญ Desk Set Premium","300","480","144,000"],
["2","แผ่นรองโต๊ะ Desk Mat สีเขียวเข้ม","300","220","66,000"],
["3","ขวดน้ำทรงเรียบ BAAN LAMUN","300","150","45,000"],
["4","สกรีนโลโก้บริษัท 1 สี","300","25","7,500"],
["5","กล่องของขวัญพร้อมริบบิ้น","300","40","12,000"],
["6","ค่าจัดส่งกรุงเทพและปริมณฑล","1","3,500","3,500"],
["รวมก่อนภาษี","","","","278,000"],
["ภาษีมูลค่าเพิ่ม 7%","","","","19,460"],
["ยอดรวมสุทธิ","","","","297,460"]]
P=lambda t,s: Paragraph(t,s)
data=[[P(c,CB if i==0 or i>=7 else C) if j in(1,) or i==0 else P(c,CB if i>=7 else (CR if j>=2 else C)) for j,c in enumerate(r)] for i,r in enumerate(rows)]
t=Table(data,colWidths=[40,215,50,110,100])
t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.5,colors.HexColor('#b9b4aa')),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eef6f0')),('BACKGROUND',(0,7),(-1,-1),colors.HexColor('#f6f3ee')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('SPAN',(0,7),(3,7)),('SPAN',(0,8),(3,8)),('SPAN',(0,9),(3,9))]))
S+=[t,Paragraph("3. เงื่อนไขการชำระเงิน",H2),
Paragraph("มัดจำ 50% เมื่อยืนยันใบสั่งซื้อ ส่วนที่เหลือชำระภายใน 15 วันหลังส่งมอบ<br/>โอนเข้าบัญชีร้านบ้านละมุน (ฝ่ายบัญชี: แพร)",B),
Paragraph("4. กำหนดส่งมอบ",H2),
Paragraph("ส่งมอบภายใน 14 วันทำการหลังอนุมัติแบบสกรีนโลโก้ (ตัวอย่างงานผลิตก่อนส่งจริง 1 ชุด) คลังสินค้า: บอย",B),
Paragraph("5. หมายเหตุ",H2),
Paragraph("ราคานี้ไม่รวมค่าออกแบบโลโก้ใหม่ หากต้องการเพิ่มสีสกรีน คิดเพิ่มสีละ 10 บาทต่อชิ้น<br/>หากสั่งเพิ่มเกิน 500 ชิ้น ติดต่ออรเพื่อขอราคาพิเศษ",B),
Spacer(1,20),
Paragraph("ผู้เสนอราคา ____________________ (อร) &nbsp;&nbsp;&nbsp;&nbsp; ผู้อนุมัติ ____________________ (ละออ เจ้าของร้าน)",B)]
d.build(S)
