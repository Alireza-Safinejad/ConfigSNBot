import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "bot.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # جدول کاربران
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # جدول خریدها
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

        # جدول پرداخت‌ها
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

        await db.commit()

async def add_user(telegram_id: int, username: str, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (telegram_id, username, full_name)
            VALUES (?, ?, ?)
        """, (telegram_id, username, full_name))
        await db.commit()

async def get_user(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            return await cursor.fetchone()

async def get_active_purchase(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT * FROM purchases
            WHERE telegram_id = ? AND status = 'active'
            ORDER BY created_at DESC LIMIT 1
        """, (telegram_id,)) as cursor:
            return await cursor.fetchone()

async def get_purchase_history(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT * FROM purchases
            WHERE telegram_id = ?
            ORDER BY created_at DESC
            LIMIT 10
        """, (telegram_id,)) as cursor:
            return await cursor.fetchall()

async def add_payment(telegram_id: int, payment_id: str, amount_usd: float,
                      plan_type: str, plan_key: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO payments (telegram_id, payment_id, amount_usd, plan_type, plan_key)
            VALUES (?, ?, ?, ?, ?)
        """, (telegram_id, payment_id, amount_usd, plan_type, plan_key))
        await db.commit()

async def get_payment(payment_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT * FROM payments WHERE payment_id = ?", (payment_id,)
        ) as cursor:
            return await cursor.fetchone()

async def update_payment_status(payment_id: str, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE payments SET status = ? WHERE payment_id = ?",
            (status, payment_id)
        )
        await db.commit()

async def add_purchase(telegram_id: int, plan_type: str, plan_key: str,
                       price_usd: float, marzban_username: str,
                       config_link: str, payment_id: str, expires_at: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO purchases
            (telegram_id, plan_type, plan_key, price_usd, marzban_username,
             config_link, payment_id, status, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?)
        """, (telegram_id, plan_type, plan_key, price_usd,
              marzban_username, config_link, payment_id, expires_at))
        await db.commit()

async def get_all_users_count():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def get_active_users_count():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM purchases WHERE status = 'active'"
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def get_monthly_revenue():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT COALESCE(SUM(price_usd), 0) FROM purchases
            WHERE status = 'active'
            AND created_at >= datetime('now', 'start of month')
        """) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def get_today_sales():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT COUNT(*) FROM purchases
            WHERE status = 'active'
            AND created_at >= datetime('now', 'start of day')
        """) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0
