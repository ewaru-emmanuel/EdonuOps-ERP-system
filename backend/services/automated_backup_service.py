"""
Automated Backup & Disaster Recovery Service
Provides scheduled backups, offsite storage, and backup verification
"""

import os
import shutil
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import hashlib

logger = logging.getLogger(__name__)

class AutomatedBackupService:
    """Automated backup service with offsite storage and verification"""
    
    def __init__(self, backup_dir: str = "backups", retention_days: int = 30):
        self.backup_dir = Path(backup_dir)
        self.retention_days = retention_days
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup metadata file
        self.metadata_file = self.backup_dir / "backup_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load backup metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading metadata: {e}")
        return {"backups": [], "last_backup": None, "backup_count": 0}
    
    def _save_metadata(self):
        """Save backup metadata"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
    
    def _get_database_path(self) -> Optional[Path]:
        """Get database file path"""
        db_url = os.getenv('DATABASE_URL', '')
        
        # SQLite database
        if 'sqlite' in db_url.lower() or not db_url:
            # Default SQLite path
            db_path = Path('edonuops.db')
            if not db_path.exists():
                db_path = Path('instance/edonuops.db')
            return db_path if db_path.exists() else None
        
        # PostgreSQL - will use pg_dump
        elif 'postgresql' in db_url.lower():
            return None  # Will use pg_dump instead
        
        return None
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file for integrity verification"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def create_backup(self, backup_type: str = "full") -> Optional[Dict]:
        """
        Create a database backup
        
        Args:
            backup_type: "full" or "incremental"
        
        Returns:
            Backup metadata dict or None if failed
        """
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            db_url = os.getenv('DATABASE_URL', '')
            
            # SQLite backup
            if 'sqlite' in db_url.lower() or not db_url:
                return self._create_sqlite_backup(timestamp, backup_type)
            
            # PostgreSQL backup
            elif 'postgresql' in db_url.lower():
                return self._create_postgresql_backup(timestamp, backup_type)
            
            else:
                logger.error(f"Unsupported database type: {db_url}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating backup: {e}", exc_info=True)
            return None
    
    def _create_sqlite_backup(self, timestamp: str, backup_type: str) -> Optional[Dict]:
        """Create SQLite database backup"""
        db_path = self._get_database_path()
        if not db_path:
            logger.error("SQLite database file not found")
            return None
        
        backup_filename = f"backup_{backup_type}_{timestamp}.db"
        backup_path = self.backup_dir / backup_filename
        
        try:
            # Copy database file
            shutil.copy2(db_path, backup_path)
            
            # Calculate hash for integrity verification
            file_hash = self._calculate_file_hash(backup_path)
            file_size = backup_path.stat().st_size
            
            # Create backup metadata
            backup_info = {
                "backup_id": f"{backup_type}_{timestamp}",
                "filename": backup_filename,
                "path": str(backup_path),
                "type": backup_type,
                "timestamp": timestamp,
                "created_at": datetime.utcnow().isoformat(),
                "file_size": file_size,
                "file_hash": file_hash,
                "database_type": "sqlite",
                "verified": False,
                "offsite_synced": False
            }
            
            # Add to metadata
            self.metadata["backups"].append(backup_info)
            self.metadata["last_backup"] = backup_info["created_at"]
            self.metadata["backup_count"] = len(self.metadata["backups"])
            self._save_metadata()
            
            logger.info(f"✅ Backup created: {backup_filename} ({file_size:,} bytes)")
            return backup_info
            
        except Exception as e:
            logger.error(f"Error creating SQLite backup: {e}", exc_info=True)
            return None
    
    def _create_postgresql_backup(self, timestamp: str, backup_type: str) -> Optional[Dict]:
        """Create PostgreSQL database backup using pg_dump"""
        db_url = os.getenv('DATABASE_URL', '')
        if not db_url:
            logger.error("DATABASE_URL not set")
            return None
        
        backup_filename = f"backup_{backup_type}_{timestamp}.sql"
        backup_path = self.backup_dir / backup_filename
        
        try:
            # Extract connection details from DATABASE_URL
            # Format: postgresql://user:password@host:port/database
            from urllib.parse import urlparse
            parsed = urlparse(db_url)
            
            # Build pg_dump command
            cmd = [
                'pg_dump',
                '-h', parsed.hostname or 'localhost',
                '-p', str(parsed.port or 5432),
                '-U', parsed.username or 'postgres',
                '-d', parsed.path.lstrip('/') or 'edonuops',
                '-F', 'c',  # Custom format (compressed)
                '-f', str(backup_path)
            ]
            
            # Set password via environment variable
            env = os.environ.copy()
            if parsed.password:
                env['PGPASSWORD'] = parsed.password
            
            # Execute pg_dump
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode != 0:
                logger.error(f"pg_dump failed: {result.stderr}")
                return None
            
            # Calculate hash for integrity verification
            file_hash = self._calculate_file_hash(backup_path)
            file_size = backup_path.stat().st_size
            
            # Create backup metadata
            backup_info = {
                "backup_id": f"{backup_type}_{timestamp}",
                "filename": backup_filename,
                "path": str(backup_path),
                "type": backup_type,
                "timestamp": timestamp,
                "created_at": datetime.utcnow().isoformat(),
                "file_size": file_size,
                "file_hash": file_hash,
                "database_type": "postgresql",
                "verified": False,
                "offsite_synced": False
            }
            
            # Add to metadata
            self.metadata["backups"].append(backup_info)
            self.metadata["last_backup"] = backup_info["created_at"]
            self.metadata["backup_count"] = len(self.metadata["backups"])
            self._save_metadata()
            
            logger.info(f"✅ PostgreSQL backup created: {backup_filename} ({file_size:,} bytes)")
            return backup_info
            
        except FileNotFoundError:
            logger.error("pg_dump not found. Please install PostgreSQL client tools.")
            return None
        except Exception as e:
            logger.error(f"Error creating PostgreSQL backup: {e}", exc_info=True)
            return None
    
    def verify_backup(self, backup_id: str) -> Tuple[bool, Optional[str]]:
        """
        Verify backup integrity
        
        Returns:
            (is_valid, error_message)
        """
        try:
            # Find backup in metadata
            backup_info = None
            for backup in self.metadata["backups"]:
                if backup["backup_id"] == backup_id:
                    backup_info = backup
                    break
            
            if not backup_info:
                return False, f"Backup {backup_id} not found"
            
            backup_path = Path(backup_info["path"])
            if not backup_path.exists():
                return False, f"Backup file not found: {backup_path}"
            
            # Verify file hash
            current_hash = self._calculate_file_hash(backup_path)
            if current_hash != backup_info["file_hash"]:
                return False, "File hash mismatch - backup may be corrupted"
            
            # For SQLite, try to open the database
            if backup_info["database_type"] == "sqlite":
                try:
                    import sqlite3
                    conn = sqlite3.connect(str(backup_path))
                    conn.execute("SELECT 1")
                    conn.close()
                except Exception as e:
                    return False, f"Database integrity check failed: {e}"
            
            # Mark as verified
            backup_info["verified"] = True
            backup_info["verified_at"] = datetime.utcnow().isoformat()
            self._save_metadata()
            
            logger.info(f"✅ Backup verified: {backup_id}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error verifying backup: {e}", exc_info=True)
            return False, str(e)
    
    def sync_to_offsite(self, backup_id: str, storage_type: str = "s3") -> Tuple[bool, Optional[str]]:
        """
        Sync backup to offsite storage
        
        Args:
            backup_id: Backup to sync
            storage_type: "s3", "gcs", "azure", or "local" (for testing)
        
        Returns:
            (success, error_message)
        """
        try:
            # Find backup
            backup_info = None
            for backup in self.metadata["backups"]:
                if backup["backup_id"] == backup_id:
                    backup_info = backup
                    break
            
            if not backup_info:
                return False, f"Backup {backup_id} not found"
            
            backup_path = Path(backup_info["path"])
            if not backup_path.exists():
                return False, f"Backup file not found: {backup_path}"
            
            # Sync based on storage type
            if storage_type == "s3":
                success, error = self._sync_to_s3(backup_path, backup_info)
            elif storage_type == "gcs":
                success, error = self._sync_to_gcs(backup_path, backup_info)
            elif storage_type == "azure":
                success, error = self._sync_to_azure(backup_path, backup_info)
            elif storage_type == "local":
                # For testing - copy to a "remote" directory
                remote_dir = self.backup_dir / "offsite"
                remote_dir.mkdir(exist_ok=True)
                remote_path = remote_dir / backup_info["filename"]
                shutil.copy2(backup_path, remote_path)
                success, error = True, None
            else:
                return False, f"Unsupported storage type: {storage_type}"
            
            if success:
                backup_info["offsite_synced"] = True
                backup_info["offsite_synced_at"] = datetime.utcnow().isoformat()
                backup_info["offsite_storage_type"] = storage_type
                self._save_metadata()
                logger.info(f"✅ Backup synced to {storage_type}: {backup_id}")
            
            return success, error
            
        except Exception as e:
            logger.error(f"Error syncing backup: {e}", exc_info=True)
            return False, str(e)
    
    def _sync_to_s3(self, backup_path: Path, backup_info: Dict) -> Tuple[bool, Optional[str]]:
        """Sync backup to Amazon S3"""
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            s3_bucket = os.getenv('S3_BACKUP_BUCKET')
            s3_key_prefix = os.getenv('S3_BACKUP_PREFIX', 'backups/')
            
            if not s3_bucket:
                return False, "S3_BACKUP_BUCKET environment variable not set"
            
            s3_client = boto3.client('s3')
            s3_key = f"{s3_key_prefix}{backup_info['filename']}"
            
            # Upload with metadata
            s3_client.upload_file(
                str(backup_path),
                s3_bucket,
                s3_key,
                ExtraArgs={
                    'Metadata': {
                        'backup_id': backup_info['backup_id'],
                        'backup_type': backup_info['type'],
                        'timestamp': backup_info['timestamp'],
                        'file_hash': backup_info['file_hash']
                    }
                }
            )
            
            return True, None
            
        except ImportError:
            return False, "boto3 not installed. Install with: pip install boto3"
        except ClientError as e:
            return False, f"S3 upload failed: {e}"
        except Exception as e:
            return False, f"Error syncing to S3: {e}"
    
    def _sync_to_gcs(self, backup_path: Path, backup_info: Dict) -> Tuple[bool, Optional[str]]:
        """Sync backup to Google Cloud Storage"""
        try:
            from google.cloud import storage
            
            gcs_bucket = os.getenv('GCS_BACKUP_BUCKET')
            gcs_prefix = os.getenv('GCS_BACKUP_PREFIX', 'backups/')
            
            if not gcs_bucket:
                return False, "GCS_BACKUP_BUCKET environment variable not set"
            
            client = storage.Client()
            bucket = client.bucket(gcs_bucket)
            blob = bucket.blob(f"{gcs_prefix}{backup_info['filename']}")
            
            # Upload with metadata
            blob.metadata = {
                'backup_id': backup_info['backup_id'],
                'backup_type': backup_info['type'],
                'timestamp': backup_info['timestamp'],
                'file_hash': backup_info['file_hash']
            }
            
            blob.upload_from_filename(str(backup_path))
            
            return True, None
            
        except ImportError:
            return False, "google-cloud-storage not installed. Install with: pip install google-cloud-storage"
        except Exception as e:
            return False, f"Error syncing to GCS: {e}"
    
    def _sync_to_azure(self, backup_path: Path, backup_info: Dict) -> Tuple[bool, Optional[str]]:
        """Sync backup to Azure Blob Storage"""
        try:
            from azure.storage.blob import BlobServiceClient
            
            azure_connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
            azure_container = os.getenv('AZURE_BACKUP_CONTAINER', 'backups')
            
            if not azure_connection_string:
                return False, "AZURE_STORAGE_CONNECTION_STRING environment variable not set"
            
            blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
            blob_client = blob_service_client.get_blob_client(
                container=azure_container,
                blob=backup_info['filename']
            )
            
            # Upload with metadata
            with open(backup_path, 'rb') as data:
                blob_client.upload_blob(
                    data,
                    metadata={
                        'backup_id': backup_info['backup_id'],
                        'backup_type': backup_info['type'],
                        'timestamp': backup_info['timestamp'],
                        'file_hash': backup_info['file_hash']
                    },
                    overwrite=True
                )
            
            return True, None
            
        except ImportError:
            return False, "azure-storage-blob not installed. Install with: pip install azure-storage-blob"
        except Exception as e:
            return False, f"Error syncing to Azure: {e}"
    
    def cleanup_old_backups(self) -> int:
        """
        Remove backups older than retention period
        
        Returns:
            Number of backups deleted
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            deleted_count = 0
            
            backups_to_keep = []
            for backup in self.metadata["backups"]:
                backup_date = datetime.fromisoformat(backup["created_at"])
                
                if backup_date < cutoff_date:
                    # Delete backup file
                    backup_path = Path(backup["path"])
                    if backup_path.exists():
                        backup_path.unlink()
                        logger.info(f"🗑️  Deleted old backup: {backup['filename']}")
                        deleted_count += 1
                else:
                    backups_to_keep.append(backup)
            
            self.metadata["backups"] = backups_to_keep
            self.metadata["backup_count"] = len(backups_to_keep)
            self._save_metadata()
            
            logger.info(f"✅ Cleaned up {deleted_count} old backups")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up backups: {e}", exc_info=True)
            return 0
    
    def get_backup_status(self) -> Dict:
        """Get backup status and statistics"""
        try:
            total_size = sum(backup.get("file_size", 0) for backup in self.metadata["backups"])
            verified_count = sum(1 for backup in self.metadata["backups"] if backup.get("verified", False))
            synced_count = sum(1 for backup in self.metadata["backups"] if backup.get("offsite_synced", False))
            
            return {
                "total_backups": self.metadata["backup_count"],
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "verified_backups": verified_count,
                "synced_backups": synced_count,
                "last_backup": self.metadata.get("last_backup"),
                "retention_days": self.retention_days
            }
        except Exception as e:
            logger.error(f"Error getting backup status: {e}")
            return {}

# Global backup service instance
backup_service = AutomatedBackupService()




