import pymysql
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# CONNECTION
# ──────────────────────────────────────────────

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",  # blank password
        database="freight_db",
        cursorclass=pymysql.cursors.DictCursor
    )

# ──────────────────────────────────────────────
# DAILY REPORT
# ──────────────────────────────────────────────

def generate_daily_report():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            logger.info("Generating daily freight report...")

            # Total requests today
            cursor.execute("""
                SELECT DATE(created_at) as date,
                       COUNT(*) as total,
                       SUM(priority = 'High') as high,
                       SUM(priority = 'Medium') as medium,
                       SUM(priority = 'Low') as low
                FROM freight_requests
                GROUP BY DATE(created_at)
            """)
            summary = cursor.fetchall()

            print("\n===== DAILY FREIGHT REPORT =====")
            for row in summary:
                print(f"Date     : {row['date']}")
                print(f"Total    : {row['total']}")
                print(f"High     : {row['high']}")
                print(f"Medium   : {row['medium']}")
                print(f"Low      : {row['low']}")

            # Requests by department
            cursor.execute("""
                SELECT department, COUNT(*) as total
                FROM freight_requests
                GROUP BY department
                ORDER BY total DESC
            """)
            dept = cursor.fetchall()

            print("\n--- By Department ---")
            for row in dept:
                print(f"  {row['department']}: {row['total']}")

            # High priority issues
            cursor.execute("""
                SELECT customer_name, origin, destination, request_type
                FROM freight_requests
                WHERE priority = 'High'
                ORDER BY created_at DESC
            """)
            high = cursor.fetchall()

            print("\n--- High Priority Requests ---")
            for row in high:
                print(f"  {row['customer_name']} | {row['origin']} → {row['destination']} | {row['request_type']}")

            print("\n================================")
            logger.info("Report generated successfully!")

    finally:
        conn.close()

if __name__ == "__main__":
    generate_daily_report()