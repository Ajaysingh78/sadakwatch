import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "sadakwatch.db")

def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ─── TABLE 1: CONTRACTORS ───────────────────────────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contractors (
        contractor_id       INTEGER PRIMARY KEY AUTOINCREMENT,
        name                TEXT NOT NULL,
        registration_number TEXT,
        headquarters_state  TEXT,
        total_roads_count   INTEGER DEFAULT 0,
        total_length_km     REAL DEFAULT 0,
        complaints_received INTEGER DEFAULT 0,
        complaints_resolved INTEGER DEFAULT 0,
        dlp_violations      INTEGER DEFAULT 0,
        repeat_failures     INTEGER DEFAULT 0,
        budget_overruns     INTEGER DEFAULT 0,
        accountability_score REAL DEFAULT 5.0,
        grade               TEXT DEFAULT 'Average'
    )
    """)

    # ─── TABLE 2: AUTHORITIES ───────────────────────────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS authorities (
        authority_id       INTEGER PRIMARY KEY AUTOINCREMENT,
        road_type          TEXT NOT NULL,
        authority_name     TEXT NOT NULL,
        authority_type     TEXT NOT NULL,
        state              TEXT,
        district           TEXT,
        engineer_name      TEXT,
        designation        TEXT,
        email              TEXT,
        phone              TEXT,
        office_address     TEXT,
        complaint_sla_days INTEGER DEFAULT 30
    )
    """)

    # ─── TABLE 3: ROADS ─────────────────────────────────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roads (
        road_id                INTEGER PRIMARY KEY AUTOINCREMENT,
        name                   TEXT NOT NULL,
        road_type              TEXT NOT NULL,
        state                  TEXT,
        district               TEXT,
        start_lat              REAL,
        start_lon              REAL,
        end_lat                REAL,
        end_lon                REAL,
        length_km              REAL,
        contractor_id          INTEGER,
        construction_date      TEXT,
        last_repair_date       TEXT,
        dlp_expiry_date        TEXT,
        budget_sanctioned_cr   REAL,
        budget_spent_cr        REAL,
        budget_utilization_pct REAL,
        funding_source         TEXT,
        source_document        TEXT,
        condition_score        INTEGER DEFAULT 5,
        accident_count_last3yr INTEGER DEFAULT 0,
        authority_id           INTEGER,
        FOREIGN KEY (contractor_id) REFERENCES contractors(contractor_id),
        FOREIGN KEY (authority_id)  REFERENCES authorities(authority_id)
    )
    """)

    # ─── TABLE 4: COMPLAINTS ────────────────────────────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        complaint_id       TEXT PRIMARY KEY,
        road_id            INTEGER,
        complaint_type     TEXT,
        severity           TEXT DEFAULT 'Medium',
        description        TEXT,
        reported_lat       REAL,
        reported_lon       REAL,
        photo_path         TEXT,
        timestamp          TEXT,
        reporter_contact   TEXT,
        status             TEXT DEFAULT 'Submitted',
        authority_assigned INTEGER,
        resolution_date    TEXT,
        resolution_notes   TEXT,
        FOREIGN KEY (road_id)            REFERENCES roads(road_id),
        FOREIGN KEY (authority_assigned) REFERENCES authorities(authority_id)
    )
    """)

    # ─── TABLE 5: GLOBAL ROADS ──────────────────────────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS global_roads (
        global_road_id       INTEGER PRIMARY KEY AUTOINCREMENT,
        country              TEXT NOT NULL,
        road_name            TEXT NOT NULL,
        road_type            TEXT,
        authority_name       TEXT,
        authority_contact    TEXT,
        complaint_portal_url TEXT,
        data_source          TEXT
    )
    """)

    # ─── INDEXES FOR FAST QUERIES ────────────────────────────────────────────
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_roads_type     ON roads(road_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_roads_state    ON roads(state)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_roads_district ON roads(district)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_roads_contractor ON roads(contractor_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_complaints_road ON complaints(road_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status)")

    conn.commit()
    conn.close()
    print("✅ Database schema created successfully at:", DB_PATH)

if __name__ == "__main__":
    create_database()