# 🛒 ShopHub — Online Do'kon

Flask + PostgreSQL bilan qurilgan to'liq ishlaydigan online market.

## Imkoniyatlar

- ✅ Ro'yxatdan o'tish / Kirish (har bir foydalanuvchi alohida)
- ✅ Admin va User rollari
- ✅ Mahsulotlar katalogi (kategoriya, qidiruv)
- ✅ Savat (qo'shish, o'chirish, miqdor o'zgartirish)
- ✅ Buyurtma berish (ism, telefon, manzil)
- ✅ Foydalanuvchi buyurtmalari tarixi
- ✅ Admin panel (mahsulot CRUD, buyurtma holati, foydalanuvchilar)
- ✅ PostgreSQL baza (Render.com bepul)

---

## 💻 Lokal ishga tushirish

### 1. Kerakli dasturlar
- Python 3.10+
- pip

### 2. Loyihani yuklab oling
```bash
git clone https://github.com/SIZNING_USERNAME/shophub.git
cd shophub
```

### 3. Virtual muhit yarating
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 4. Kutubxonalarni o'rnating
```bash
pip install -r requirements.txt
```

### 5. Ishga tushiring
```bash
python app.py
```

Brauzerda oching: http://localhost:5000

**Admin kirish:** username: `admin` | parol: `admin123`

---

## 🚀 Render.com ga deploy qilish (BEPUL)

### 1-qadam: GitHub ga yuklang

```bash
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/USERNAME/shophub.git
git push -u origin main
```

### 2-qadam: Render.com da ro'yxatdan o'ting
- https://render.com ga boring
- GitHub akkaunt bilan kiring

### 3-qadam: Yangi Web Service yarating
1. **New +** → **Web Service**
2. GitHub repo ni ulang
3. Sozlamalar:
   - **Name:** shophub
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt && python build.py`
   - **Start Command:** `gunicorn app:app`

### 4-qadam: PostgreSQL baza yarating
1. **New +** → **PostgreSQL**
2. **Name:** shophub-db
3. **Free** plan tanlang
4. Yaratilgandan keyin **Internal Database URL** ni nusxalang

### 5-qadam: Environment Variables qo'shing
Web Service sozlamalarida **Environment** bo'limiga:
- `DATABASE_URL` = (4-qadamda nusxalangan URL)
- `SECRET_KEY` = (istalgan uzun parol, masalan: `mysecretkey2024xyz`)

### 6-qadam: Deploy!
- **Manual Deploy** → **Deploy latest commit**
- 2-3 daqiqa kutasiz, tayyor!

---

## Loyiha tuzilishi

```
shophub/
├── app.py              ← Asosiy Flask ilovasi (routes, models)
├── requirements.txt    ← Python kutubxonalari
├── build.py            ← Render uchun init script
├── Procfile            ← Render start command
├── render.yaml         ← Render konfiguratsiya
└── templates/
    ├── base.html       ← Umumiy sahifa (navbar, footer)
    ├── login.html      ← Kirish sahifasi
    ├── register.html   ← Ro'yxatdan o'tish
    ├── index.html      ← Bosh sahifa
    ├── products.html   ← Mahsulotlar ro'yxati
    ├── cart.html       ← Savat
    ├── checkout.html   ← Buyurtma berish
    ├── my_orders.html  ← Mening buyurtmalarim
    └── admin/
        ├── dashboard.html    ← Admin bosh sahifasi
        ├── products.html     ← Mahsulotlar boshqaruvi
        ├── product_form.html ← Qo'shish/tahrirlash formasi
        ├── orders.html       ← Buyurtmalar boshqaruvi
        └── users.html        ← Foydalanuvchilar ro'yxati
```

---

## Texnologiyalar

| Texnologiya | Maqsad |
|-------------|--------|
| Python Flask | Backend framework |
| SQLAlchemy | ORM (baza bilan ishlash) |
| PostgreSQL | Asosiy ma'lumotlar bazasi |
| Werkzeug | Parol xavfsizligi (hashing) |
| Jinja2 | HTML shablonlar |
| Gunicorn | Production server |
| Render.com | Bepul hosting |
