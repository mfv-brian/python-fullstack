from fastapi import APIRouter, Depends, HTTPException
from pydantic.networks import EmailStr
from datetime import datetime

from app.api.deps import get_current_active_superuser
from app.models import Message
from app.utils import generate_test_email, send_email
from app.core.optimization import optimize_database, get_tenant_performance_report
from app.core.db import check_db_health, get_db_stats, vacuum_database, reindex_database

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")


@router.get("/health-check/")
async def health_check() -> bool:
    return True


@router.get("/db/health")
def check_database_health():
    """Check database health and connectivity."""
    return {
        "healthy": check_db_health(),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/db/stats")
def get_database_statistics():
    """Get database statistics and connection pool info."""
    return get_db_stats()

@router.post("/db/optimize")
def optimize_database_endpoint():
    """Run database optimization tasks."""
    try:
        results = optimize_database()
        return {
            "message": "Database optimization completed",
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database optimization failed: {str(e)}"
        )

@router.post("/db/vacuum")
def vacuum_database_endpoint():
    """Run VACUUM on the database."""
    success = vacuum_database()
    if success:
        return {"message": "Database VACUUM completed successfully"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Database VACUUM failed"
        )

@router.post("/db/reindex")
def reindex_database_endpoint():
    """Reindex the database."""
    success = reindex_database()
    if success:
        return {"message": "Database reindex completed successfully"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Database reindex failed"
        )

@router.get("/db/tenant/{tenant_id}/performance")
def get_tenant_performance(tenant_id: str):
    """Get performance report for a specific tenant."""
    try:
        report = get_tenant_performance_report(tenant_id)
        return {
            "tenant_id": tenant_id,
            "report": report,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get tenant performance report: {str(e)}"
        )
