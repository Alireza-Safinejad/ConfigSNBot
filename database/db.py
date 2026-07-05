import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "bot.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT,
                referred_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                plan_type TEXT NOT NULL,
                plan_key TEXT NOT NULL,
                price_usd REAL NOT NULL,
                marzban_username TEXT,
                config_link TEXT,
                payment_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                payment_id TEXT UNIQUE NOT NULL,
                amount_usd REAL NOT NULL,
                plan_type TEXT NOT NULL,
                plan_key TEXT NOT NULL,
                status TEXT DEFAULT 'waiting',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER NOT NULL,
                referred_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS referral_pending (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                plan_type TEXT NOT NULL,
                plan_key TEXT NOT NULL,
                required_refs INTEGER NOT NULL,
                current_refs INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_link TEXT UNIQUE NOT NULL,
                source TEXT,
                used INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def add_user(telegram_id: int, username: str, full_name: str, referred_by: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (telegram_id, username, full_name, referred_by)
            VALUES (?, ?, ?, ?)
        """, (telegram_id, username, full_name, referred_by))
        await db.commit()

async def get_user(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            return await cursor.fetchone()

async def get_active_purchase(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT * FROM purchases WHERE telegram_id = ? AND status = 'active'
            ORDER BY created_at DESC LIMIT 1
        """, (telegram_id,)) as cursor:
            return await cursor.fetchone()

async def get_purchase_history(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT * FROM purchases WHERE telegram_id = ?
            ORDER BY created_at DESC LIMIT 10
        """, (telegram_id,)) as cursor:
            return await cursor.fetchall()

async def add_payment(telegram_id: int, payment_id: str, amount_usd: float, plan_type: str, plan_key: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO payments (telegram_id, payment_id, amount_usd, plan_type, plan_key)
            VALUES (?, ?, ?, ?, ?)
        """, (telegram_id, payment_id, amount_usd, plan_type, plan_key))
        await db.commit()

async def get_payment(payment_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM payments WHERE payment_id = ?", (payment_id,)) as cursor:
            return await cursor.fetchone()

async def update_payment_status(payment_id: str, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE payments SET status = ? WHERE payment_id = ?", (status, payment_id))
        await db.commit()

async def add_purchase(telegram_id: int, plan_type: str, plan_key: str, price_usd: float,
                       marzban_username: str, config_link: str, payment_id: str, expires_at: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO purchases
            (telegram_id, plan_type, plan_key, price_usd, marzban_username, config_link, payment_id, status, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?)
        """, (telegram_id, plan_type, plan_key, price_usd, marzban_username, config_link, payment_id, expires_at))
        await db.commit()

async def get_all_users_count():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def get_active_users_count():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM purchases WHERE status = 'active'") as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def get_monthly_revenue():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT COALESCE(SUM(price_usd), 0) FROM purchases
            WHERE status = 'active' AND created_at >= datetime('now', 'start of month')
        """) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def get_today_sales():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT COUNT(*) FROM purchases
            WHERE status = 'active' AND created_at >= datetime('now', 'start of day')
        """) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def add_referral(referrer_id: int, referred_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO referrals (referrer_id, referred_id) VALUES (?, ?)",
                        (referrer_id, referred_id))
        await db.commit()

async def get_referral_count(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (telegram_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def add_referral_pending(telegram_id: int, plan_type: str, plan_key: str, required_refs: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO referral_pending (telegram_id, plan_type, plan_key, required_refs)
            VALUES (?, ?, ?, ?)
        """, (telegram_id, plan_type, plan_key, required_refs))
        await db.commit()

async def get_referral_pending(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT * FROM referral_pending WHERE telegram_id = ? AND status = 'pending'
            ORDER BY created_at DESC LIMIT 1
        """, (telegram_id,)) as cursor:
            return await cursor.fetchone()

async def update_referral_pending(telegram_id: int, current_refs: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE referral_pending SET current_refs = ? WHERE telegram_id = ? AND status = 'pending'
        """, (current_refs, telegram_id))
        await db.commit()

async def complete_referral_pending(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE referral_pending SET status = 'completed' WHERE telegram_id = ? AND status = 'pending'
        """, (telegram_id,))
        await db.commit()

# ==================== مدیریت کانفیگ‌ها ====================

async def save_config(config_link: str, source: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO configs (config_link, source) VALUES (?, ?)
        """, (config_link, source))
        await db.commit()

async def get_unused_config() -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT id, config_link FROM configs WHERE used = 0
            ORDER BY created_at ASC LIMIT 1
        """) as cursor:
            row = await cursor.fetchone()
            if row:
                await db.execute("UPDATE configs SET used = 1 WHERE id = ?", (row[0],))
                await db.commit()
                return row[1]
    return None

async def get_configs_count() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM configs WHERE used = 0") as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def delete_old_configs():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            DELETE FROM configs WHERE created_at < datetime('now', '-7 days')
        """)
        await db.commit()
        print("✅ کانفیگ‌های قدیمی حذف شدن.")
