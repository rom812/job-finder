# Quick Start Guide

## Frontend לבד (עם Mock Data)

הפרונטאנד עובד עכשיו!

```bash
cd frontend
npm run dev
```

פתח בדפדפן: **http://localhost:5173**

הפרונטאנד יציג mock data אם ה-backend לא זמין.

## Backend + Frontend (מלא)

### Terminal 1 - Backend:
```bash
source venv/bin/activate
python api/server.py
```

### Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

פתח: **http://localhost:5173**

## בעיות נפוצות

### Frontend לא עובד / תקוע בטעינה

```bash
cd frontend
rm -rf node_modules .vite
npm cache clean --force
npm install
npm run dev
```

### Port 5173 תפוס

```bash
# מצא את התהליך
lsof -i :5173

# עצור אותו
kill -9 <PID>
```

### Backend לא עובד

```bash
# ודא שהvirtu environment פעיל
source venv/bin/activate

# התקן dependencies
pip install flask flask-cors

# הרץ
python api/server.py
```

## מה אני רואה?

הפרונטאנד מציג:

1. **Dashboard Header** - כותרת + search config
2. **Statistics** - סטטיסטיקות כלליות
3. **Filters** - סינון לפי רמת התאמה
4. **Job Cards** - רשימת משרות עם:
   - Match score מעגלי
   - פרטי חברה
   - Skills analysis
   - Company insights
   - כפתור Apply

## בעיות?

אם משהו לא עובד:

1. וודא ש-Node.js מותקן: `node --version`
2. וודא ש-npm מותקן: `npm --version`
3. נקה cache ונסה שוב (ראה מעלה)
4. פתח issue בגיטהאב

---

**הפרונטאנד זמין עכשיו ב-http://localhost:5173 !**
