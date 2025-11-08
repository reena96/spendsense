#!/usr/bin/env python3
"""
Generate recommendations for all users in the database.

This script calls the recommendation API for each user to ensure
all users have fresh recommendations generated.
"""

import subprocess
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    print("=" * 70)
    print("Generating Recommendations for All Users")
    print("=" * 70)
    print()

    success_count = 0
    error_count = 0
    total_users = 120

    for i in range(total_users):
        user_id = f"user_MASKED_{i:03d}"

        try:
            # Call the API using curl
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                 f"http://localhost:8000/api/recommendations/{user_id}"],
                capture_output=True,
                text=True,
                timeout=10
            )

            status_code = result.stdout.strip()

            if status_code == "200":
                print(f"[{i+1:3d}/{total_users}] ✅ {user_id}")
                success_count += 1
            else:
                print(f"[{i+1:3d}/{total_users}] ❌ {user_id} (HTTP {status_code})")
                error_count += 1

        except Exception as e:
            print(f"[{i+1:3d}/{total_users}] ❌ {user_id}: {str(e)[:40]}")
            error_count += 1

        # Small delay to avoid overwhelming the API
        time.sleep(0.05)

    print()
    print("=" * 70)
    print(f"✅ SUCCESS: {success_count}/{total_users} users")
    print(f"❌ FAILED:  {error_count}/{total_users} users")
    print("=" * 70)

if __name__ == "__main__":
    main()
