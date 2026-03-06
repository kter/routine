"""Root conftest: shared pytest fixtures."""

import os
import sys
from pathlib import Path

# Ensure the backend src is on the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend" / "src"))

# Set environment for tests
os.environ.setdefault("DB_TYPE", "sqlite")
os.environ.setdefault("SQLITE_PATH", ":memory:")
os.environ.setdefault("TEST_MODE", "true")
os.environ.setdefault("TEST_TENANT_ID", "00000000-0000-0000-0000-000000000001")
os.environ.setdefault("TEST_USER_SUB", "test-user-sub")
os.environ.setdefault("EVIDENCE_BUCKET_NAME", "test-evidence-bucket")
os.environ.setdefault("COGNITO_JWKS_URL", "https://example.com/jwks")
os.environ.setdefault("COGNITO_CLIENT_ID", "test-client-id")
