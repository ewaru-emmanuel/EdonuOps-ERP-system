"""
Database Schema Synchronization Utility
Automatically syncs database schema with SQLAlchemy models
Adds missing columns without affecting existing data
"""

from sqlalchemy import text, inspect
from app import db
import logging

logger = logging.getLogger(__name__)

def sync_model_columns(model_class):
    """
    Sync a single model's columns with the database
    Adds missing columns without affecting existing data
    """
    try:
        table_name = model_class.__tablename__
        inspector = inspect(db.engine)
        
        # Get existing columns from database
        existing_columns = {col['name']: col for col in inspector.get_columns(table_name)}
        
        # Get expected columns from model
        expected_columns = {}
        for column in model_class.__table__.columns:
            expected_columns[column.name] = {
                'type': column.type,
                'nullable': column.nullable,
                'default': column.default
            }
        
        # Find missing columns
        missing_columns = []
        for col_name, col_info in expected_columns.items():
            if col_name not in existing_columns:
                missing_columns.append((col_name, col_info))
        
        # Add missing columns
        if missing_columns:
            for col_name, col_info in missing_columns:
                try:
                    # Convert SQLAlchemy type to SQL
                    col_type = str(col_info['type'])
                    
                    # Handle PostgreSQL-specific types
                    if 'TEXT' in col_type.upper():
                        sql_type = 'TEXT'
                    elif 'VARCHAR' in col_type.upper() or 'STRING' in col_type.upper():
                        # Extract length if available
                        length_match = None
                        if hasattr(col_info['type'], 'length'):
                            length = col_info['type'].length
                            if length:
                                sql_type = f'VARCHAR({length})'
                            else:
                                sql_type = 'VARCHAR(255)'
                        else:
                            sql_type = 'VARCHAR(255)'
                    elif 'INTEGER' in col_type.upper() or 'INT' in col_type.upper():
                        sql_type = 'INTEGER'
                    elif 'FLOAT' in col_type.upper() or 'REAL' in col_type.upper():
                        sql_type = 'FLOAT'
                    elif 'BOOLEAN' in col_type.upper() or 'BOOL' in col_type.upper():
                        sql_type = 'BOOLEAN'
                    elif 'DATE' in col_type.upper():
                        sql_type = 'DATE'
                    elif 'DATETIME' in col_type.upper() or 'TIMESTAMP' in col_type.upper():
                        sql_type = 'TIMESTAMP'
                    elif 'JSONB' in col_type.upper():
                        sql_type = 'JSONB'
                    else:
                        sql_type = 'TEXT'  # Default fallback
                    
                    # Build ALTER TABLE statement
                    nullable_clause = '' if col_info['nullable'] else ' NOT NULL'
                    default_clause = ''
                    
                    if col_info['default']:
                        if hasattr(col_info['default'], 'arg'):
                            # Handle SQLAlchemy defaults
                            default_value = col_info['default'].arg
                            if isinstance(default_value, (int, float)):
                                default_clause = f' DEFAULT {default_value}'
                            elif isinstance(default_value, bool):
                                default_clause = f' DEFAULT {str(default_value).upper()}'
                            elif isinstance(default_value, str):
                                default_clause = f" DEFAULT '{default_value}'"
                    
                    alter_sql = f"""
                        ALTER TABLE {table_name} 
                        ADD COLUMN IF NOT EXISTS {col_name} {sql_type}{nullable_clause}{default_clause}
                    """
                    
                    db.session.execute(text(alter_sql))
                    logger.info(f"✅ Added missing column '{col_name}' to table '{table_name}'")
                    
                except Exception as e:
                    logger.warning(f"⚠️  Could not add column '{col_name}' to '{table_name}': {e}")
                    # Continue with other columns even if one fails
        
        if missing_columns:
            db.session.commit()
            logger.info(f"✅ Synced {len(missing_columns)} missing column(s) for table '{table_name}'")
            return len(missing_columns)
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Error syncing columns for {table_name}: {e}")
        db.session.rollback()
        return 0

def sync_all_models():
    """
    Sync all registered models with the database
    This should be called on application startup
    Automatically adds missing columns without affecting existing data
    """
    try:
        # Import models dynamically to avoid circular imports
        models_to_sync = []
        
        try:
            from modules.finance.models import Account
            models_to_sync.append(Account)
        except ImportError as e:
            logger.debug(f"Could not import Account model: {e}")
        
        if not models_to_sync:
            logger.debug("No models to sync")
            return 0
        
        total_synced = 0
        for model in models_to_sync:
            try:
                # Check if table exists before syncing
                inspector = inspect(db.engine)
                table_name = model.__tablename__
                
                if not inspector.has_table(table_name):
                    logger.debug(f"Table '{table_name}' does not exist, skipping sync (will be created by db.create_all())")
                    continue
                
                synced = sync_model_columns(model)
                total_synced += synced
            except Exception as e:
                logger.warning(f"⚠️  Could not sync model {model.__name__}: {e}")
                continue
        
        if total_synced > 0:
            logger.info(f"✅ Database schema sync complete: {total_synced} column(s) added")
        else:
            logger.debug("✅ Database schema is up to date")
        
        return total_synced
        
    except Exception as e:
        logger.error(f"❌ Error during database schema sync: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return 0

