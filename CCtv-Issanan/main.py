# เรียกใช้งานไลบรารี OpenCV และ requests
import cv2 as cv
import requests

# เปิดกล้องเว็บแคมที่ติดตั้งในเครื่อง (ใช้หมายเลข 0)
camera = cv.VideoCapture(0)

# กำหนด URL ของ LINE Notify API และ Token ของคุณ
url = 'https://notify-api.line.me/api/notify'
token = 'YyC8BVO6omqWQ9SaE3O3SsTehmQvWBKxdC0mLrrkquB'

# กำหนดหัวเสริม (headers) สำหรับ HTTP request ไปยัง LINE Notify
headers = {
    'content-type': 'application/x-www-form-urlencoded',
    'Authorization': 'Bearer ' + token
}

# ข้อความที่จะส่งผ่าน LINE Notify เมื่อตรวจพบการเคลื่อนไหว
msg = 'has movement'

# เริ่มลูปคราวเอาเปิดกล้องและตรวจสอบภาพ
while camera.isOpened():
    # อ่านภาพจากกล้องเว็บแคมสองครั้ง
    retry, screen1 = camera.read()
    retry, screen2 = camera.read()

    # คำนวณความแตกต่างระหว่างภาพ
    difference = cv.absdiff(screen1, screen2)

    # แปลงภาพเป็นระดับสีเทา
    white = cv.cvtColor(difference, cv.COLOR_RGB2GRAY)

    # ทำการบลอร์ภาพเทา
    blur = cv.GaussianBlur(white, (5, 5), 0)

    # กำหนดค่าสิ้นสุด (threshold) เพื่อสร้างภาพขาวดำที่ตราบการเคลื่อนไหว
    _, threshold = cv.threshold(blur, 20, 255, cv.THRESH_BINARY)

    # ขยายขนาดพื้นที่ที่เคลื่อนไหวด้วยการขยายขนาด (dilation)
    dilation = cv.dilate(threshold, None, iterations=5)

    # ค้นหาขอบ (contours) ในภาพที่ถูกขยายขนาด
    contours, _, = cv.findContours(dilation, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # วาดขอบรอบการเคลื่อนไหวบนภาพต้นฉบับ
    cv.drawContours(screen1, contours, -1, (0, 255, 0), 2)
    
    # ตรวจสอบและส่งข้อความผ่าน LINE Notify เมื่อตรวจพบการเคลื่อนไหว
    for movement in contours:
        if cv.contourArea(movement) < 8000:
            continue
        x, y, height, width = cv.boundingRect(movement)
        cv.rectangle(screen1, (x, y), (x+height, y+width), (0, 255, 0), 2)

        notify = requests.post(url, headers=headers, data={'message': msg})
        print(notify.text)
        
    # รอรับข้อมูลและทำการแสดงภาพบนหน้าต่าง "pyCCTV"
    if cv.waitKey(10) == ord('q'):
        break
    
    cv.imshow('pyCCTV', screen1)

