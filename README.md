# 🔨 Savdo.uz — O'zbekiston Auktsion Platformasi

O'zbekiston uchun to'liq stack auktsion platformasi. Real vaqt bidding, xavfsiz escrow to'lov tizimi va qulay interfeys.

![Platform](https://img.shields.io/badge/FastAPI-0.128-009688?style=flat-square&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat-square&logo=mysql)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## ✨ Asosiy xususiyatlar

- 🔨 **Real vaqt bidding** — WebSocket orqali jonli taklif berish
- 💳 **Escrow to'lov tizimi** — Xaridor buyumni olgach, sotuvchiga pul o'tkaziladi
- 🏷️ **1% garov to'lovi** — Sotuvchilar jiddiyligini tasdiqlash uchun
- 🎟️ **Ishtirok to'lovi** — Xaridorlar auktsiyonga qo'shilish uchun to'laydi
- 👤 **JWT autentifikatsiya** — Xavfsiz token asosida tizimga kirish
- 📊 **Shaxsiy kabinet** — Takliflar, to'lovlar va bildirishnomalar tarixi
- 📱 **Responsive dizayn** — Mobil va desktop uchun optimallashtirilgan

---

## 🛠️ Texnologiyalar

| Qatlam | Texnologiya |
|--------|-------------|
| Backend | FastAPI (Python 3.13) |
| Ma'lumotlar bazasi | MySQL 8.0 + SQLAlchemy |
| Autentifikatsiya | JWT (python-jose) |
| Parol xeshlash | bcrypt (passlib) |
| Real vaqt | WebSockets |
| Frontend | HTML5, CSS3, Vanilla JavaScript |

---

## 📁 Loyiha tuzilmasi

```
savdo-uz/
├── backend/
│   ├── main.py              # FastAPI app, CORS, routerlar
│   ├── config.py            # Sozlamalar (.env)
│   ├── database.py          # MySQL ulanish
│   ├── dependencies.py      # JWT auth dependency
│   ├── models/              # SQLAlchemy modellari
│   │   ├── user.py
│   │   ├── auction.py
│   │   ├── bid.py
│   │   ├── payment.py
│   │   └── category.py
│   ├── schemas/             # Pydantic sxemalar
│   ├── services/            # Biznes logika
│   │   ├── auth_service.py
│   │   ├── auction_service.py
│   │   ├── bid_service.py
│   │   └── payment_service.py
│   ├── routers/             # API endpointlar
│   │   ├── auth.py          # /api/auth/*
│   │   ├── auctions.py      # /api/auctions/*
│   │   ├── bids.py          # /api/bids/*
│   │   ├── payments.py      # /api/payments/*
│   │   ├── users.py         # /api/users/*
│   │   └── admin.py         # /api/admin/*
│   └── utils/
│       ├── security.py      # JWT, bcrypt
│       ├── helpers.py       # Yordamchi funksiyalar
│       └── websocket_manager.py
├── database/
│   ├── schema.sql           # Jadvallar
│   └── seed.sql             # Test ma'lumotlar
├── frontend/
│   ├── index.html           # Bosh sahifa
│   ├── auctions.html        # Auktsionlar ro'yxati
│   ├── auction-detail.html  # Bid berish sahifasi
│   ├── create-auction.html  # Auktsion yaratish
│   ├── dashboard.html       # Foydalanuvchi kabineti
│   ├── login.html           # Kirish
│   └── register.html        # Ro'yxatdan o'tish
├── .env.example
├── requirements.txt
└── run.sh
```

---

## 🚀 O'rnatish

### 1. Reponi klonlash

```bash
git clone https://github.com/hamzayevtemur-lab/auction-uz.git
cd auction-uz
```

### 2. Virtual muhit yaratish

```bash
python3 -m venv venv
source venv/bin/activate       # Mac/Linux
# venv\Scripts\activate        # Windows
```

### 3. Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 4. `.env` faylini sozlash

```bash
cp .env.example .env
```

`.env` ni oching va quyidagilarni to'ldiring:

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=auction_uz
DB_USER=root
DB_PASSWORD=your_mysql_password

SECRET_KEY=your-secret-key-min-32-chars
```

### 5. MySQL bazasini yaratish

```bash
mysql -u root -p
```

```sql
CREATE DATABASE auction_uz CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 6. Jadvallar va test ma'lumotlarini yuklash

```bash
mysql -u root -p auction_uz < database/schema.sql
mysql -u root -p auction_uz < database/seed.sql
```

### 7. Serverni ishga tushirish

```bash
uvicorn backend.main:app --reload
```

✅ API: **http://localhost:8000**
📚 Swagger UI: **http://localhost:8000/api/docs**

---

## 🔑 Test hisoblar

| Rol | Email | Parol |
|-----|-------|-------|
| Xaridor | jasur@test.uz | test1234 |
| Sotuvchi | malika@test.uz | test1234 |
| Admin | admin@savdo.uz | test1234 |

---

## 📍 API Endpointlar

```
POST   /api/auth/register              Ro'yxatdan o'tish
POST   /api/auth/login                 Kirish (JWT token)

GET    /api/auctions                   Auktsionlar ro'yxati
POST   /api/auctions                   Yangi auktsion yaratish
GET    /api/auctions/{id}              Bitta auktsion
GET    /api/auctions/my                Mening auktsionlarim
WS     /api/auctions/{id}/ws           Real vaqt WebSocket

POST   /api/bids                       Taklif berish
GET    /api/bids/my                    Mening takliflarim
GET    /api/bids/auction/{id}          Auktsion takliflari

POST   /api/payments/seller-fee/{id}   1% garov to'lov
POST   /api/payments/participation/{id} Ishtirok to'lov
POST   /api/payments/escrow/{id}       G'oliblik to'lovi
GET    /api/payments/my                To'lovlar tarixi

GET    /api/users/me                   Profil
PUT    /api/users/me                   Profilni yangilash
GET    /api/users/me/notifications     Bildirishnomalar
```

---

## 💰 To'lov jarayoni

```
SOTUVCHI:
  1. Auktsion yaratadi
  2. Boshlang'ich narxning 1% garov to'lovini to'laydi
  3. Auktsion faollashadi
  4. G'olib xaridor to'laydi → Sotuvchi pul oladi

XARIDOR:
  1. Auktsiyonga qo'shilish uchun ishtirok to'lovini to'laydi
  2. Real vaqtda taklif beradi
  3. G'alaba qilsa, escrow orqali to'laydi
  4. Buyumni olgach pul sotuvchiga o'tkaziladi
```

---

## 📄 Litsenziya

MIT License — erkin foydalaning va tarqating.

---

*Savdo.uz — O'zbekistonda auktsion savdosini yangi bosqichga olib chiqamiz* 🇺🇿