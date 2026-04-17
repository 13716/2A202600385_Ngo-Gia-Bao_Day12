"""
database.py — SQLite database layer cho XanhSM AI Agent
Tables:
  - trips   : thông tin chuyến đi (mock seed data)
  - tickets : ticket hỗ trợ được tạo bởi agent
"""

import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).with_name("xanhsm.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Khởi tạo bảng và seed dữ liệu mẫu nếu chưa có."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS trips (
                trip_id   TEXT PRIMARY KEY,
                driver    TEXT NOT NULL,
                vehicle   TEXT NOT NULL,
                time      TEXT NOT NULL,
                route     TEXT NOT NULL,
                status    TEXT NOT NULL DEFAULT 'completed'
            );

            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id  TEXT PRIMARY KEY,
                issue_type TEXT NOT NULL,
                description TEXT NOT NULL,
                trip_id    TEXT,
                time       TEXT,
                status     TEXT NOT NULL DEFAULT 'open',
                created_at TEXT NOT NULL
            );
        """)

        # Seed dữ liệu mẫu (INSERT OR IGNORE để không bị trùng khi restart)
        seed_trips = [
            ("101",  "Nguyễn Văn An",     "Xe máy",  "07:15",  "Hoàn Kiếm → Cầu Giấy",         "completed"),
            ("102",  "Trần Thị Bích",     "Ô tô",    "08:30",  "Đống Đa → Thanh Xuân",           "completed"),
            ("103",  "Lê Văn Cường",      "Xe máy",  "09:00",  "Hai Bà Trưng → Long Biên",       "completed"),
            ("104",  "Phạm Thị Dung",     "Ô tô",    "09:45",  "Nam Từ Liêm → Hoàng Mai",        "completed"),
            ("105",  "Hoàng Văn Em",      "Xe máy",  "10:20",  "Tây Hồ → Ba Đình",               "completed"),
            ("123",  "Nguyễn Minh Khoa",  "Xe máy",  "10:30",  "Hoàn Kiếm → Cầu Giấy",          "completed"),
            ("201",  "Vũ Thị Lan",        "Ô tô",    "11:00",  "Bắc Từ Liêm → Đống Đa",         "completed"),
            ("202",  "Đặng Văn Mạnh",     "Xe máy",  "11:30",  "Cầu Giấy → Hà Đông",            "completed"),
            ("203",  "Ngô Thị Ngân",      "Ô tô",    "12:00",  "Hoàng Mai → Thanh Trì",          "completed"),
            ("204",  "Bùi Văn Phúc",      "Xe máy",  "12:45",  "Long Biên → Gia Lâm",           "completed"),
            ("256",  "Trần Thị Bảo",      "Ô tô",    "14:30",  "Đống Đa → Thanh Xuân",           "completed"),
            ("301",  "Lý Thị Quỳnh",      "Xe máy",  "13:15",  "Tây Hồ → Cầu Giấy",             "completed"),
            ("302",  "Đinh Văn Sơn",      "Ô tô",    "14:00",  "Hoàn Kiếm → Đống Đa",           "completed"),
            ("303",  "Phan Thị Thu",      "Xe máy",  "15:00",  "Ba Đình → Nam Từ Liêm",          "completed"),
            ("304",  "Cao Văn Uy",        "Ô tô",    "15:30",  "Hai Bà Trưng → Hoàng Mai",       "completed"),
            ("512",  "Lê Quang Vinh",     "Xe máy",  "08:00",  "Hai Bà Trưng → Long Biên",       "completed"),
            ("401",  "Mai Thị Xuân",      "Ô tô",    "16:00",  "Thanh Xuân → Đống Đa",           "completed"),
            ("402",  "Trương Văn Yên",    "Xe máy",  "16:30",  "Hà Đông → Cầu Giấy",            "completed"),
            ("789",  "Phạm Hữu Zũng",     "Ô tô",    "17:45",  "Nam Từ Liêm → Hoàng Mai",        "completed"),
            ("1024", "Hoàng Đức Anh",     "Xe máy",  "12:15",  "Tây Hồ → Ba Đình",               "completed"),
        ]
        conn.executemany(
            "INSERT OR IGNORE INTO trips (trip_id, driver, vehicle, time, route, status) VALUES (?,?,?,?,?,?)",
            seed_trips,
        )

        conn.commit()


# ──────────────────────────────────────────────
# Query functions
# ──────────────────────────────────────────────

def db_lookup_trip(trip_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM trips WHERE trip_id = ?", (trip_id,)
        ).fetchone()
    return dict(row) if row else None


def db_create_ticket(
    issue_type: str,
    description: str,
    trip_id: str | None = None,
    time: str | None = None,
) -> str:
    ticket_id = "TK-" + uuid.uuid4().hex[:6].upper()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO tickets (ticket_id, issue_type, description, trip_id, time, status, created_at)
               VALUES (?, ?, ?, ?, ?, 'open', ?)""",
            (ticket_id, issue_type, description, trip_id, time, created_at),
        )
        conn.commit()
    return ticket_id


def db_list_tickets() -> list[dict]:
    """Tiện ích xem tất cả ticket (dùng để debug / admin)."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM tickets ORDER BY created_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]
