"""
Storage module for persisting and retrieving assembled recommendations.

Handles database operations for recommendation sets with timestamp tracking.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from spendsense.recommendations.assembler import AssembledRecommendationSet

logger = logging.getLogger(__name__)


class RecommendationStorage:
    """
    Storage handler for assembled recommendations.

    Implements Story 4.5 AC5, AC6:
    - Stores assembled recommendations with timestamp
    - Retrieves recommendations by user_id
    - Tracks generation history

    For now uses JSON file storage for simplicity.
    Can be extended to use SQLite or other database backends.

    Usage:
        storage = RecommendationStorage("data/recommendations")
        storage.save_recommendation_set(rec_set)
        rec_set = storage.get_latest_by_user("user_123")
    """

    def __init__(self, storage_path: str = "data/recommendations"):
        """
        Initialize storage handler.

        Args:
            storage_path: Directory path for storing recommendation files
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"RecommendationStorage initialized at {self.storage_path}")

    def save_recommendation_set(
        self,
        recommendation_set: AssembledRecommendationSet,
    ) -> str:
        """
        Save assembled recommendation set to storage (PRD AC5).

        Args:
            recommendation_set: Assembled recommendation set to save

        Returns:
            File path where recommendation set was saved

        Example:
            >>> storage = RecommendationStorage()
            >>> path = storage.save_recommendation_set(rec_set)
            >>> print(f"Saved to {path}")
        """
        user_id = recommendation_set.user_id
        timestamp = recommendation_set.generated_at.strftime("%Y%m%d_%H%M%S_%f")  # Include microseconds
        time_window = recommendation_set.time_window

        # Create user directory if it doesn't exist
        user_dir = self.storage_path / user_id
        user_dir.mkdir(exist_ok=True)

        # Create filename with timestamp and time window
        filename = f"recommendations_{time_window}_{timestamp}.json"
        file_path = user_dir / filename

        # Convert to dict and save as JSON
        data = recommendation_set.to_dict()

        try:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(
                f"Saved recommendation set for {user_id} "
                f"({len(recommendation_set.recommendations)} items) to {file_path}"
            )

            # Also save as "latest" for easy retrieval
            latest_path = user_dir / f"latest_{time_window}.json"
            with open(latest_path, "w") as f:
                json.dump(data, f, indent=2, default=str)

            return str(file_path)

        except Exception as e:
            logger.error(f"Error saving recommendation set: {e}", exc_info=True)
            raise

    def get_latest_by_user(
        self,
        user_id: str,
        time_window: str = "30d",
    ) -> Optional[AssembledRecommendationSet]:
        """
        Get latest recommendation set for a user (PRD AC6).

        Args:
            user_id: User identifier
            time_window: Time window ("30d" or "180d")

        Returns:
            AssembledRecommendationSet if found, None otherwise

        Example:
            >>> storage = RecommendationStorage()
            >>> rec_set = storage.get_latest_by_user("user_123", "30d")
            >>> if rec_set:
            ...     print(f"Found {len(rec_set.recommendations)} recommendations")
        """
        user_dir = self.storage_path / user_id
        latest_path = user_dir / f"latest_{time_window}.json"

        if not latest_path.exists():
            logger.debug(f"No recommendations found for {user_id} ({time_window})")
            return None

        try:
            with open(latest_path, "r") as f:
                data = json.load(f)

            # Convert back to AssembledRecommendationSet
            # (simplified - just return dict for now)
            logger.info(
                f"Retrieved latest recommendations for {user_id} ({time_window}): "
                f"{len(data.get('recommendations', []))} items"
            )

            return data  # Return dict representation for API

        except Exception as e:
            logger.error(f"Error loading recommendation set: {e}", exc_info=True)
            return None

    def get_all_by_user(
        self,
        user_id: str,
        time_window: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all recommendation sets for a user (PRD AC6).

        Args:
            user_id: User identifier
            time_window: Optional time window filter ("30d" or "180d")

        Returns:
            List of recommendation set dicts sorted by timestamp (newest first)

        Example:
            >>> storage = RecommendationStorage()
            >>> rec_sets = storage.get_all_by_user("user_123")
            >>> print(f"Found {len(rec_sets)} recommendation sets")
        """
        user_dir = self.storage_path / user_id

        if not user_dir.exists():
            logger.debug(f"No recommendation history for {user_id}")
            return []

        # Find all recommendation files
        pattern = "recommendations_*.json"
        files = sorted(user_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)

        # Filter by time window if specified
        if time_window:
            files = [f for f in files if f"_{time_window}_" in f.name]

        # Exclude "latest" files
        files = [f for f in files if not f.name.startswith("latest_")]

        recommendation_sets = []
        for file_path in files:
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    recommendation_sets.append(data)
            except Exception as e:
                logger.warning(f"Error loading {file_path}: {e}")
                continue

        logger.info(
            f"Retrieved {len(recommendation_sets)} recommendation sets for {user_id}"
        )

        return recommendation_sets

    def delete_old_recommendations(
        self,
        user_id: str,
        keep_count: int = 10,
    ) -> int:
        """
        Delete old recommendation sets, keeping only the most recent N.

        Args:
            user_id: User identifier
            keep_count: Number of recent sets to keep per time window

        Returns:
            Number of files deleted

        Example:
            >>> storage = RecommendationStorage()
            >>> deleted = storage.delete_old_recommendations("user_123", keep_count=5)
            >>> print(f"Deleted {deleted} old recommendation files")
        """
        user_dir = self.storage_path / user_id

        if not user_dir.exists():
            return 0

        deleted_count = 0

        # Process each time window separately
        for time_window in ["30d", "180d"]:
            pattern = f"recommendations_{time_window}_*.json"
            files = sorted(
                user_dir.glob(pattern),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            # Delete files beyond keep_count
            for file_path in files[keep_count:]:
                try:
                    file_path.unlink()
                    deleted_count += 1
                    logger.debug(f"Deleted old recommendation file: {file_path}")
                except Exception as e:
                    logger.warning(f"Error deleting {file_path}: {e}")

        if deleted_count > 0:
            logger.info(
                f"Deleted {deleted_count} old recommendation files for {user_id}"
            )

        return deleted_count

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.

        Returns:
            Dict with storage metrics

        Example:
            >>> storage = RecommendationStorage()
            >>> stats = storage.get_storage_stats()
            >>> print(f"Total users: {stats['total_users']}")
        """
        if not self.storage_path.exists():
            return {
                "total_users": 0,
                "total_recommendation_files": 0,
                "total_size_mb": 0.0,
                "storage_path": str(self.storage_path),
            }

        user_dirs = [d for d in self.storage_path.iterdir() if d.is_dir()]

        total_users = len(user_dirs)
        total_files = sum(
            len([f for f in d.glob("recommendations_*.json") if not f.name.startswith("latest_")])
            for d in user_dirs
        )

        # Calculate total size
        total_size_bytes = sum(
            f.stat().st_size
            for d in user_dirs
            for f in d.glob("*.json")
        )

        return {
            "total_users": total_users,
            "total_recommendation_files": total_files,
            "total_size_mb": round(total_size_bytes / (1024 * 1024), 3),  # More precision
            "storage_path": str(self.storage_path),
        }
