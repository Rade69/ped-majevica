#!/usr/bin/env python
"""
Backup database for PED Majevica 1988.

Supports both SQLite (dev) and PostgreSQL (production).
Usage:
    python scripts/backup_db.py                # default location
    python scripts/backup_db.py --output /path # custom output
    python scripts/backup_db.py --compress     # gzip output
"""

import os
import sys
import gzip
import shutil
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Load .env from project root
load_dotenv()


def get_db_config():
    """Return database URL and type."""
    db_url = os.getenv("DATABASE_URL", "")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    is_postgres = db_url.startswith("postgresql://")
    is_sqlite = db_url.startswith("sqlite://") or not db_url

    if not is_sqlite and not is_postgres:
        # Assume sqlite
        is_sqlite = True

    return db_url, is_postgres, is_sqlite


def backup_sqlite(db_url, output_path):
    """Backup SQLite database by copying the file."""
    # Extract file path from sqlite:///instance/ped.db
    if db_url.startswith("sqlite://"):
        db_path = db_url.replace("sqlite:///", "")
        # Handle absolute path
        if db_path.startswith("/"):
            db_path = db_path[1:]
    else:
        # Default location
        backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(backend_root, "instance", "ped.db")

    if not os.path.exists(db_path):
        print(f"❌ SQLite database not found at: {db_path}")
        return False

    print(f"📦 Backing up SQLite database: {db_path}")
    shutil.copy2(db_path, output_path)
    print(f"✅ Backup saved to: {output_path}")
    return True


def backup_postgresql(db_url, output_path):
    """Backup PostgreSQL database using pg_dump."""
    import subprocess

    print(f"📦 Backing up PostgreSQL database via pg_dump...")

    cmd = [
        "pg_dump",
        "--format=custom",
        "--no-owner",
        "--no-privileges",
        f"--file={output_path}",
        db_url,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            print(f"❌ pg_dump failed: {result.stderr}")
            return False

        print(f"✅ Backup saved to: {output_path}")
        return True

    except subprocess.TimeoutExpired:
        print("❌ pg_dump timed out after 5 minutes")
        return False
    except FileNotFoundError:
        print("❌ pg_dump not found. Install postgresql-client or postgresql package.")
        return False
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False


def compress_file(filepath, remove_original=False):
    """Compress a file with gzip."""
    gz_path = filepath + ".gz"
    print(f"🗜️  Compressing: {filepath}")

    with open(filepath, "rb") as f_in:
        with gzip.open(gz_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    original_size = os.path.getsize(filepath)
    compressed_size = os.path.getsize(gz_path)
    ratio = (1 - compressed_size / original_size) * 100

    print(f"✅ Compressed: {original_size:,} bytes → {compressed_size:,} bytes ({ratio:.1f}% reduction)")

    if remove_original:
        os.remove(filepath)
        print(f"🗑️  Removed original: {filepath}")

    return gz_path


def cleanup_old_backups(backup_dir, keep=5):
    """Keep only the N most recent backups."""
    if not os.path.exists(backup_dir):
        return

    files = sorted(
        [f for f in os.listdir(backup_dir) if f.startswith("pedmajevica_backup_")],
        reverse=True,
    )

    to_remove = files[keep:]
    for f in to_remove:
        path = os.path.join(backup_dir, f)
        os.remove(path)
        print(f"🗑️  Removed old backup: {f}")


def main():
    parser = argparse.ArgumentParser(description="Backup PED Majevica database")
    parser.add_argument("--output", help="Output file path (default: auto-generated)")
    parser.add_argument("--compress", action="store_true", help="Compress backup with gzip")
    parser.add_argument("--keep", type=int, default=5, help="Number of backups to keep (default: 5)")
    parser.add_argument("--dir", help="Backup directory (default: backend/backups/)")
    args = parser.parse_args()

    db_url, is_postgres, is_sqlite = get_db_config()
    print(f"Database URL: {db_url[:30]}..." if len(db_url) > 30 else f"Database URL: {db_url}")
    print(f"Database type: {'PostgreSQL' if is_postgres else 'SQLite'}")

    # Determine output directory
    if args.dir:
        backup_dir = args.dir
    else:
        backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        backup_dir = os.path.join(backend_root, "backups")

    os.makedirs(backup_dir, exist_ok=True)

    # Generate output filename
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = "sql" if is_postgres else "db"
        output_path = os.path.join(backup_dir, f"pedmajevica_backup_{timestamp}.{ext}")

    # Perform backup
    success = False
    if is_sqlite:
        success = backup_sqlite(db_url, output_path)
    elif is_postgres:
        success = backup_postgresql(db_url, output_path)

    if not success:
        sys.exit(1)

    # Compress if requested
    if args.compress:
        output_path = compress_file(output_path, remove_original=True)

    # Cleanup old backups
    cleanup_old_backups(backup_dir, keep=args.keep)

    print(f"\n✅ Backup completed successfully!")
    print(f"   File: {output_path}")
    print(f"   Size: {os.path.getsize(output_path):,} bytes")


if __name__ == "__main__":
    main()
