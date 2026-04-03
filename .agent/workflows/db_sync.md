---
description: Serverdagi PostgreSQL bazasini localhostga ko'chirish (Sync)
---

Bu workflow serverdagi PostgreSQL ma'lumotlarini (Docker ishlatilgan holda) local kompyuteringizga ko'chirish uchun bosqichlarni o'z ichiga oladi.

### 1. Serverda ma'lumotlarni dump qilish (backup olish)
Serveringizga SSH orqali kiring va bazadan nusxa oling:
```bash
docker exec -t epl-db-1 pg_dump -U epl_user epl_db > db_backup.sql
```

### 2. Faylni localga ko'chirish
Local kompyuteringiz terminalida (serverda emas) ushbu komandani ishlating:
```bash
scp user@server-ip_manzili:/path/to/db_backup.sql ./db_backup.sql
```
*Izoh: `user` o'rniga server useri, `server-ip_manzili` o'rniga serveringiz IP manzilini yozing.*

### 1-usul: PostgreSQL SQL Dump (Tezkor va tavsiya etilgan)
*Yuqoridagi bosqichlar (db_backup.sql).*

### 2-usul: Django JSON Dump (Cross-platform uchun qulay)
Agar SQL bilan muammo bo'lsa yoki bazalar xilma-xil bo'lsa (masalan, SQLite dan Postgres ga), Django JSON usulidan foydalaning:

**1. Serverda ma'lumotlarni JSON ga dump qilish:**
```bash
docker exec -t epl-web-1 python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 2 > data.json
```

**2. Faylni localga ko'chirish:**
```bash
scp user@server-ip_manzili:/path/to/data.json ./data.json
```

**3. Localhost bazasiga yuklash (Import):**
```bash
# Avval local bazani tozalash (migrate qilish)
docker exec -it epl-web-1 python manage.py flush --no-input

# Ma'lumotlarni yuklash
cat data.json | docker exec -i epl-web-1 python manage.py loaddata --format=json -
```

### 3. Media fayllarni ko'chirish (Rasm va PDFlar)
Agar rasm yoki PDFlar ham kerak bo'lsa, `media` papkasini ko'chiring:
```bash
scp -r user@server-ip_manzili:/path/to/project/media/* ./media/
```
