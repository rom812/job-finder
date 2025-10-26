# 🤝 Partnership Guide - Rom & Claude

**פרויקט:** job-finder
**תאריך:** 21 אוקטובר 2025

---

## 🎯 המטרה

**Rom לומד לבנות פרויקט multi-agent מא' עד ת' - בעצמו!**

זה לא על Claude שכותב את הקוד.
זה על **Rom שלומד לכתוב קוד מקצועי** עם הדרכה.

---

## 📜 כללי העבודה

### 1️⃣ Rom מממש 80%, Claude מנחה 20%

**Rom אחראי על:**
- ✅ כתיבת כל הקוד
- ✅ כתיבת כל ה-tests
- ✅ הרצת הקוד ובדיקה שעובד
- ✅ Debug של בעיות

**Claude אחראי על:**
- ✅ הסבר איך לעשות דברים
- ✅ Code review וביקורת
- ✅ הצעות לשיפור
- ✅ עזרה כשתקוע
- ✅ כתיבת documentation

---

### 2️⃣ לפני כל agent - הסבר מלא!

**Claude יעשה:**
1. 📖 **הסבר תיאורטי** - מה ה-agent עושה
2. 💡 **דוגמה קטנה** - קוד לדוגמה פשוט
3. 🎯 **מה צריך לממש** - רשימת משימות ברורה
4. ❓ **שאלות הבנה** - Rom יאשר שהבין

**רק אז Rom מתחיל לכתוב!**

---

### 3️⃣ תהליך העבודה לכל agent

```
┌─────────────────────────────────────┐
│ 1. Claude מסביר את ה-agent         │
├─────────────────────────────────────┤
│ 2. Rom שואל שאלות הבהרה            │
├─────────────────────────────────────┤
│ 3. Rom כותב את הקוד (בעצמו!)       │
├─────────────────────────────────────┤
│ 4. Rom מריץ ובודק                  │
├─────────────────────────────────────┤
│ 5. אם יש בעיות - Rom מתקן          │
│    (Claude עוזר רק אם תקוע)        │
├─────────────────────────────────────┤
│ 6. Claude עושה code review         │
├─────────────────────────────────────┤
│ 7. Rom כותב tests                  │
├─────────────────────────────────────┤
│ 8. Rom מריץ tests ומוודא שעובר     │
├─────────────────────────────────────┤
│ 9. Done! ✅ עובר ל-agent הבא       │
└─────────────────────────────────────┘
```

---

### 4️⃣ כשRom תקוע

**Rom אומר:** "אני תקוע ב-X, נסיתי Y, לא עובד"

**Claude עושה:**
1. שואל שאלות הבנה
2. מסביר את הבעיה
3. נותן רמז (לא פתרון מלא!)
4. Rom מנסה שוב

**רק אם Rom באמת תקוע** - Claude יראה פתרון (אבל Rom כותב!)

---

## 🎓 עקרונות למידה

### ✅ טוב:
- Rom כותב קוד ושואל "זה נכון?"
- Rom מנסה לפתור בעיה לבד לפני לשאול
- Rom מסביר חזרה ל-Claude מה למד
- Rom מציע רעיונות לשיפור

### ❌ לא טוב:
- "תכתוב לי את הקוד"
- "תתקן לי את זה"
- להעתיק קוד בלי להבין
- לא לבדוק אם הקוד עובד

---

## 📚 יומן למידה - job-finder

### 21 אוקטובר 2025 - Day 0: Setup

**מה עשינו:**
- ✅ יצרנו repo חדש פרטי: job-finder
- ✅ יצרנו את מבנה התיקיות
- ✅ כתבנו ARCHITECTURE.md
- ✅ כתבנו PARTNERSHIP_GUIDE.md

**מה הבא:**
- 📝 Rom יכתוב את models.py
- 🤖 Rom יממש Agent 1: CV Analyzer

---

## 🎯 תוכנית העבודה

### יום 1: Models + Agent 1 (CV Analyzer)
**Rom יעשה:**
1. כתיבת `models/models.py` - כל המודלים
2. כתיבת `agents/cv_analyzer.py` - Agent 1
3. כתיבת `tests/test_cv_analyzer.py`
4. הרצת tests ובדיקה שעובד

**Claude יעשה:**
- הסבר על Pydantic models
- הסבר על PyPDF2
- Code review
- עזרה אם תקוע

---

### יום 2: Agent 2 + 3
**Rom יעשה:**
1. כתיבת `agents/job_scraper.py` - Agent 2
2. כתיבת `agents/news_agent.py` - Agent 3
3. Tests לשניהם

**Claude יעשה:**
- הסבר על BeautifulSoup
- הסבר על Reddit API (PRAW)
- Code review

---

### יום 3: Agent 4 + Pipeline
**Rom יעשה:**
1. כתיבת `agents/matcher.py` - Agent 4
2. כתיבת `pipeline/orchestrator.py`
3. כתיבת `pipeline/tasks.py`
4. Tests

**Claude יעשה:**
- הסבר על embeddings
- הסבר על async/await
- Code review

---

### יום 4: Integration + Examples
**Rom יעשה:**
1. חיבור כל ה-agents ביחד
2. כתיבת `examples/run_example.py`
3. בדיקה end-to-end
4. תיקון bugs

**Claude יעשה:**
- עזרה בintegration
- הצעות לoptimization

---

### יום 5: Documentation + Polish
**Rom יעשה:**
1. כתיבת README.md מדהים
2. הוספת comments לקוד
3. ניקוי קוד
4. Commit + Push

**Claude יעשה:**
- Review של README
- הצעות לשיפור presentation

---

## 🛠️ כלים וטכנולוגיות שנלמד

### Python Core:
- ✅ Type hints
- ✅ Async/await
- ✅ List comprehensions
- ✅ Error handling (try/except)

### Libraries:
- ✅ Pydantic - data validation
- ✅ PyPDF2 - PDF reading
- ✅ BeautifulSoup4 - web scraping
- ✅ PRAW - Reddit API
- ✅ OpenAI - embeddings & chat
- ✅ pytest - testing

### Best Practices:
- ✅ Clean code structure
- ✅ Separation of concerns
- ✅ Testing every component
- ✅ Documentation
- ✅ Git commits (meaningful messages)

---

## ✅ Checklist לכל agent

**לפני שמתחילים:**
- [ ] קראתי את ARCHITECTURE.md
- [ ] הבנתי מה ה-agent צריך לעשות
- [ ] הבנתי מה ה-input ומה ה-output
- [ ] יש לי את ה-API keys (אם צריך)

**בזמן כתיבה:**
- [ ] כתבתי את הפונקציות הבסיסיות
- [ ] הוספתי type hints
- [ ] הוספתי docstrings
- [ ] בדקתי שהקוד עובד (הרצתי אותו!)

**לפני commit:**
- [ ] כתבתי tests
- [ ] כל ה-tests עוברים
- [ ] הקוד נקי (אין print() מיותרים)
- [ ] הוספתי comments למקומות מסובכים

---

## 💬 פורמט התקשורת

### כשRom מסיים task:
```
✅ סיימתי לכתוב את [X]
📝 הקוד נמצא ב-[file]
🧪 Tests: [passed/failed]
❓ שאלות: [שאלות אם יש]
```

### כשClaude עושה review:
```
🎯 מה טוב:
- [רשימת דברים טובים]

💡 הצעות לשיפור:
- [רשימת הצעות]

❓ שאלות לrom:
- [שאלות הבנה]
```

---

## 🚨 כללים חשובים

### Rom לא יעשה:
- ❌ להעתיק קוד בלי להבין
- ❌ לדלג על tests
- ❌ לדלג על type hints
- ❌ commit קוד שלא עובד

### Claude לא יעשה:
- ❌ לכתוב קוד במקום Rom
- ❌ לתת פתרונות מלאים ישר
- ❌ להמשיך בלי שRom הבין
- ❌ לוותר על איכות
- ❌ **לכתוב הערות בעברית בקוד** - רק באנגלית!

### 📝 Code Style (חובה!):
- ✅ **כל ההערות בקוד באנגלית בלבד** - No Hebrew in code comments!
- ✅ Type hints לכל הפונקציות
- ✅ Docstrings באנגלית
- ✅ שמות משתנים וקבועים באנגלית
- ✅ קוד נקי וקריא - כאילו recruiter יקרא אותו!

---

## 🎖️ הצלחה נמדדת ב:

1. **Rom יודע להסביר** את הקוד שכתב
2. **Rom יכול לכתוב** agent חדש לבד
3. **הפרויקט עובד** end-to-end
4. **הקוד מקצועי** וראוי ל-portfolio
5. **Rom גאה בעבודה** שלו!

---

## 📞 תקשורת יעילה

### דוגמאות טובות:

✅ **Rom:** "סיימתי לכתוב את CV Analyzer. הוא קורא PDF ושולח ל-OpenAI. Tests עוברים. רוצה code review?"

✅ **Rom:** "אני תקוע - הPDF לא נקרא נכון, מקבל UnicodeDecodeError. נסיתי utf-8 encoding אבל לא עובד"

✅ **Rom:** "אני לא בטוח איך לעשות async call ל-Reddit API. אפשר הסבר?"

### דוגמאות פחות טובות:

❌ "זה לא עובד, תתקן"
❌ "תכתוב את זה בשבילי"
❌ "אני לא מבין כלום"

---

## 🚀 Let's Build!

**Remember:**
- 💪 אתה כותב את הקוד
- 🧠 אתה לומד
- 🎯 אתה בונה portfolio
- 🤝 אני כאן לעזור!

**עדכון אחרון:** 21 אוקטובר 2025
