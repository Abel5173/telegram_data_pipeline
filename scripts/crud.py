from sqlalchemy import text
from datetime import date

def get_top_products(db, limit=10):
    result = db.execute(text("""
        SELECT product_label, COUNT(*) AS mention_count
        FROM raw.image_detections
        GROUP BY product_label
        ORDER BY mention_count DESC
        LIMIT :limit
    """), {"limit": limit})
    return [{"product_label": row[0], "mention_count": row[1]} for row in result]

def search_messages(db, query):
    result = db.execute(text("""
        SELECT f.message_id, c.channel_name, f.message_text, f.has_media, f.media_type, f.media_path
        FROM public_marts.fct_messages f
        JOIN public_marts.dim_channels c ON f.channel_id = c.channel_id
        WHERE f.message_text ILIKE :query
        LIMIT 50
    """), {"query": f"%{query}%"})

    # This works by mapping row keys to values
    rows = result.mappings().all()

    return [dict(row) for row in rows]


def get_channel_activity(db, channel_name: str):
    query = text("""
        SELECT d.date, COUNT(*) as message_count
        FROM public_marts.fct_messages f
        JOIN public_marts.dim_dates d ON f.date_id = d.date_id
        JOIN public_marts.dim_channels c ON f.channel_id = c.channel_id
        WHERE c.channel_name = :channel_name
        GROUP BY d.date
        ORDER BY d.date;
    """)

    result = db.execute(query, {"channel_name": channel_name})
    return [
        {
            "date": row[0].isoformat(),  # ← convert date → string
            "message_count": row[1]
        }
        for row in result.fetchall()
    ]
