import json
import os
import sys
import time
import psycopg

# Environment variables with defaults matching compose.yml
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASS = os.getenv("DB_PASS", "secretpw")
DB_NAME = os.getenv("DB_NAME", "appdb")
TOP_N = int(os.getenv("APP_TOP_N", "5"))


def connect_with_retry(retries=10, delay=2):
    last_err = None
    for _ in range(retries):
        try:
            conn = psycopg.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASS,
                dbname=DB_NAME,
                connect_timeout=3,
            )
            return conn
        except Exception as e:
            last_err = e
            print("Waiting for database...", file=sys.stderr)
            time.sleep(delay)

    print("Failed to connect to Postgres:", last_err, file=sys.stderr)
    sys.exit(1)


def main():
    conn = connect_with_retry()
    with conn, conn.cursor() as cur:
        # 1. Total number of trips
        cur.execute("SELECT COUNT(*) FROM trips;")
        total_trips = cur.fetchone()[0]

        # 2. Average fare by city
        cur.execute("""
            SELECT 
                city, 
                ROUND(AVG(fare)::numeric, 2) AS avg_fare 
            FROM trips 
            GROUP BY city 
            ORDER BY avg_fare DESC;
        """)
        by_city = [{"city": c, "avg_fare": float(a)} for (c, a) in cur.fetchall()]

        # 3. Top N longest trips ordered by minutes
        cur.execute("""
            SELECT 
                id, 
                city, 
                minutes, 
                fare 
            FROM trips 
            ORDER BY minutes DESC 
            LIMIT %s;
        """, (TOP_N,))

        top = [
            {
                "id": row[0],
                "city": row[1],
                "minutes": row[2],
                "fare": float(row[3])
            }
            for row in cur.fetchall()
        ]

        summary = {
            "total_trips": int(total_trips),
            "avg_fare_by_city": by_city,
            "top_by_minutes": top
        }

        # Write out/summary.json
        os.makedirs("/out", exist_ok=True)
        with open("/out/summary.json", "w") as f:
            json.dump(summary, f, indent=2)

        # Print to stdout
        print("=== Summary ===")
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()