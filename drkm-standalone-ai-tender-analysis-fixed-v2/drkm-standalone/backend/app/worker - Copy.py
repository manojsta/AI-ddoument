from celery import Celery
from .config import settings

celery_app = Celery("drkm", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(task_serializer="json", accept_content=["json"], result_serializer="json")

@celery_app.task(name="drkm.index_document")
def index_document(document_id: str):
    from .database import SessionLocal
    from .models import Document, DocumentChunk
    from .services.extract import extract_document
    from .services.ai import embed_text
    from sqlalchemy import delete
    db = SessionLocal()
    try:
        doc = db.get(Document, document_id)
        if not doc:
            return {"error": "document not found"}
        doc.status = "processing"
        db.commit()
        pages = extract_document(doc.storage_path, doc.filename)
        full_text = "\n\n".join(p["text"] for p in pages if p["text"])
        doc.extracted_text = full_text
        doc.metadata_json = {
            "suggested_title": doc.filename.rsplit(".", 1)[0],
            "page_count": len(pages),
            "text_characters": len(full_text),
            "classification": "Needs review"
        }
        db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == doc.id))
        chunks = []
        for page in pages:
            text = page["text"]
            for start in range(0, len(text), 900):
                part = text[start:start+1100].strip()
                if part:
                    chunks.append(DocumentChunk(
                        document_id=doc.id, chunk_number=len(chunks),
                        page_number=page.get("page"), content=part,
                        embedding=embed_text(part)
                    ))
        db.add_all(chunks)
        doc.status = "indexed" if chunks else "no_text"
        db.commit()
        return {"document_id": document_id, "chunks": len(chunks), "status": doc.status}
    except Exception as exc:
        db.rollback()
        doc = db.get(Document, document_id)
        if doc:
            doc.status = "failed"
            doc.metadata_json = {**(doc.metadata_json or {}), "error": str(exc)[:500]}
            db.commit()
        raise
    finally:
        db.close()
