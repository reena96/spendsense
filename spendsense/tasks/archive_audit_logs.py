"""
Audit log archival script for Epic 6 Story 6.5.

Archives audit logs older than 2 years to Parquet files for 7-year
retention compliance (financial services standard).
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from spendsense.config.database import get_db_path
from spendsense.ingestion.database_writer import AuditLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Archive configuration
ARCHIVE_AGE_DAYS = 730  # 2 years
ARCHIVE_ROOT = Path("data/audit_archives")


def archive_old_logs():
    """
    Archive audit logs older than 2 years to Parquet files.

    - Active logs: Last 2 years in database
    - Archived logs: 2-7 years in Parquet files (monthly partitions)
    - Deletion: Logs older than 7 years (configurable)
    """
    db_path = get_db_path()
    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        return

    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Calculate cutoff date (2 years ago)
        cutoff_date = datetime.utcnow() - timedelta(days=ARCHIVE_AGE_DAYS)
        logger.info(f"Archiving logs older than {cutoff_date.date()}")

        # Get logs to archive
        old_logs = session.query(AuditLog).filter(
            AuditLog.timestamp < cutoff_date
        ).all()

        if not old_logs:
            logger.info("No logs to archive")
            return

        logger.info(f"Found {len(old_logs)} logs to archive")

        # Convert to DataFrame
        log_data = []
        for log in old_logs:
            log_data.append({
                "log_id": log.log_id,
                "event_type": log.event_type,
                "user_id": log.user_id,
                "operator_id": log.operator_id,
                "recommendation_id": log.recommendation_id,
                "timestamp": log.timestamp,
                "event_data": log.event_data,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent
            })

        df = pd.DataFrame(log_data)

        # Group by month and save to Parquet
        df['year_month'] = pd.to_datetime(df['timestamp']).dt.to_period('M')

        archived_count = 0
        for period, group in df.groupby('year_month'):
            # Create archive directory
            archive_dir = ARCHIVE_ROOT / str(period.year) / f"{period.month:02d}"
            archive_dir.mkdir(parents=True, exist_ok=True)

            # Save to Parquet
            archive_file = archive_dir / f"audit_log_{period}.parquet"
            group.drop(columns=['year_month']).to_parquet(archive_file, compression='snappy')

            archived_count += len(group)
            logger.info(f"Archived {len(group)} logs to {archive_file}")

        # Delete archived logs from database
        session.query(AuditLog).filter(
            AuditLog.timestamp < cutoff_date
        ).delete()
        session.commit()

        logger.info(f"Successfully archived {archived_count} logs and removed from database")

    except Exception as e:
        session.rollback()
        logger.error(f"Archive failed: {e}", exc_info=True)
        raise
    finally:
        session.close()


if __name__ == "__main__":
    archive_old_logs()
