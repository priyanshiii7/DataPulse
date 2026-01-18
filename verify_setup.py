import os
import sys

print("🔍 Verifying DataPulse setup...")
print()

# Check directory structure
required_dirs = [
    'app',
    'app/api',
    'app/services',
    'app/templates',
    'app/static',
    'app/static/css',
    'app/static/js',
]

required_files = [
    'app/__init__.py',
    'app/config.py',
    'app/models.py',
    'app/schemas.py',
    'app/database.py',
    'app/main.py',
    'app/api/__init__.py',
    'app/api/pipelines.py',
    'app/api/health_checks.py',
    'app/api/metrics.py',
    'app/services/__init__.py',
    'app/services/cache.py',
    'app/services/health_checker.py',
    'app/services/alerts.py',
    'app/templates/base.html',
    'app/templates/dashboard.html',
    'app/templates/pipeline_detail.html',
    'requirements.txt',
    '.env',
]

missing_dirs = []
missing_files = []

for d in required_dirs:
    if not os.path.exists(d):
        missing_dirs.append(d)
        print(f"❌ Missing directory: {d}")
    else:
        print(f"  Directory exists: {d}")

print()

for f in required_files:
    if not os.path.exists(f):
        missing_files.append(f)
        print(f"❌ Missing file: {f}")
    else:
        # Check if file is empty (except __init__.py which can be empty)
        if os.path.getsize(f) == 0 and not f.endswith('__init__.py') and not f.endswith('.js'):
            print(f"   File exists but is EMPTY: {f}")
        else:
            print(f"  File exists: {f}")

print()
print("=" * 60)

if missing_dirs or missing_files:
    print("❌ Setup is INCOMPLETE")
    print()
    if missing_dirs:
        print("Missing directories:")
        for d in missing_dirs:
            print(f"   - {d}")
    if missing_files:
        print("Missing files:")
        for f in missing_files:
            print(f"   - {f}")
else:
    print("  Setup looks GOOD!")
    print()
    print("Next steps:")
    print("1. python -c \"import asyncio; from app.database import init_db; asyncio.run(init_db())\"")
    print("2. uvicorn app.main:app --reload")
    print("3. Visit http://localhost:8000")

print("=" * 60)
