from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import pymysql
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Freight API", version="1.0.0")

# ──────────────────────────────────────────────
# MODELS
# ──────────────────────────────────────────────

class FreightRequest(BaseModel):
    customer_name: str
    origin: str
    destination: str
    request_type: str  # Quote / Issue / Follow-up
    priority: str      # High / Medium / Low
    department: str    # Sales / Operations / Customer Service

class WebhookPayload(BaseModel):
    event: str
    data: dict

# ──────────────────────────────────────────────
# DB CONNECTION
# ──────────────────────────────────────────────

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="freight_db",
        cursorclass=pymysql.cursors.DictCursor
    )

# ──────────────────────────────────────────────
# ENDPOINTS
# ──────────────────────────────────────────────

@app.get("/")
def health_check():
    return {
        "status": "running",
        "service": "AI Freight API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/freight")
def create_freight_request(request: FreightRequest):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO freight_requests
                (customer_name, origin, destination, request_type, priority, department)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                request.customer_name,
                request.origin,
                request.destination,
                request.request_type,
                request.priority,
                request.department
            ))
            conn.commit()
            new_id = cursor.lastrowid
        conn.close()
        logger.info("New freight request created: ID %s", new_id)
        return {
            "status": "success",
            "message": "Freight request created",
            "id": new_id,
            "data": request.dict()
        }
    except Exception as e:
        logger.error("Failed to create request: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/freight")
def get_all_requests():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM freight_requests ORDER BY created_at DESC")
            results = cursor.fetchall()
        conn.close()
        return {
            "status": "success",
            "total": len(results),
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/freight/summary")
def get_summary():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT request_type, COUNT(*) as total
                FROM freight_requests
                GROUP BY request_type
            """)
            by_type = cursor.fetchall()

            cursor.execute("""
                SELECT priority, COUNT(*) as total
                FROM freight_requests
                GROUP BY priority
            """)
            by_priority = cursor.fetchall()
        conn.close()
        return {
            "status": "success",
            "by_type": by_type,
            "by_priority": by_priority
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook")
def receive_webhook(payload: WebhookPayload):
    logger.info("Webhook received: event=%s", payload.event)
    print(f"\n📦 WEBHOOK EVENT: {payload.event}")
    print(f"   Data: {payload.data}")
    return {
        "status": "received",
        "event": payload.event,
        "timestamp": datetime.now().isoformat()
    }

# ──────────────────────────────────────────────
# RUN
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("freight_api:app", host="127.0.0.1", port=8000, reload=True)