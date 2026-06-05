#!/bin/bash
# Savdo.uz backend-ni ishga tushirish

echo "🚀 Savdo.uz backend ishga tushirilmoqda..."
echo ""

# .env mavjudmi?
if [ ! -f .env ]; then
    echo "⚠️  .env fayl topilmadi. .env.example dan nusxa ko'chirish..."
    cp .env.example .env
    echo "✅ .env fayl yaratildi. DB sozlamalarini kiriting!"
    echo ""
fi

# MySQL ishlayaptimi?
echo "📦 MySQL ulanishi tekshirilmoqda..."
python -c "
from backend.config import settings
import pymysql
try:
    conn = pymysql.connect(
        host=settings.DB_HOST, port=settings.DB_PORT,
        user=settings.DB_USER, password=settings.DB_PASSWORD,
    )
    # DB yaratish
    with conn.cursor() as c:
        c.execute(f'CREATE DATABASE IF NOT EXISTS {settings.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
    conn.close()
    print('✅ MySQL ulanishi muvaffaqiyatli')
except Exception as e:
    print(f'❌ MySQL ulanmadi: {e}')
    print('   MySQL ishlayotganini va .env dagi sozlamalarni tekshiring')
    exit(1)
" || exit 1

echo ""
echo "🌐 Server: http://localhost:8000"
echo "📚 API docs: http://localhost:8000/api/docs"
echo ""

uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
