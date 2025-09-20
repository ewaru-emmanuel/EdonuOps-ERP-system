import sys
import os
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

def run_migration():
    app = create_app()
    with app.app_context():
        try:
            print("🔄 Starting sales tables creation migration...")
            
            with db.engine.connect() as connection:
                # Check if tables already exist
                inspector = db.inspect(db.engine)
                existing_tables = inspector.get_table_names()
                
                # Create customers table
                if 'customers' not in existing_tables:
                    print("📋 Creating customers table...")
                    customers_sql = """
                    CREATE TABLE customers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(200) NOT NULL,
                        email VARCHAR(120) UNIQUE,
                        phone VARCHAR(20),
                        address TEXT,
                        company_name VARCHAR(200),
                        tax_id VARCHAR(50),
                        credit_limit FLOAT DEFAULT 0.0,
                        payment_terms VARCHAR(50) DEFAULT 'Net 30',
                        is_active BOOLEAN DEFAULT 1,
                        customer_type VARCHAR(50) DEFAULT 'regular',
                        category VARCHAR(100),
                        region VARCHAR(100),
                        total_sales FLOAT DEFAULT 0.0,
                        outstanding_balance FLOAT DEFAULT 0.0,
                        last_payment_date DATE,
                        average_payment_days INTEGER DEFAULT 30,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        created_by VARCHAR(100)
                    )
                    """
                    connection.execute(text(customers_sql))
                    print("✅ Customers table created successfully!")
                else:
                    print("✅ Customers table already exists!")
                
                # Create invoices table
                if 'invoices' not in existing_tables:
                    print("📋 Creating invoices table...")
                    invoices_sql = """
                    CREATE TABLE invoices (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        customer_id INTEGER NOT NULL,
                        invoice_number VARCHAR(50) UNIQUE NOT NULL,
                        invoice_date DATE NOT NULL,
                        due_date DATE NOT NULL,
                        subtotal FLOAT DEFAULT 0.0,
                        tax_amount FLOAT DEFAULT 0.0,
                        discount_amount FLOAT DEFAULT 0.0,
                        total_amount FLOAT NOT NULL,
                        paid_amount FLOAT DEFAULT 0.0,
                        outstanding_amount FLOAT NOT NULL,
                        status VARCHAR(20) DEFAULT 'pending',
                        payment_method VARCHAR(50),
                        description TEXT,
                        notes TEXT,
                        po_reference VARCHAR(100),
                        project_id INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        created_by VARCHAR(100),
                        FOREIGN KEY (customer_id) REFERENCES customers (id)
                    )
                    """
                    connection.execute(text(invoices_sql))
                    print("✅ Invoices table created successfully!")
                else:
                    print("✅ Invoices table already exists!")
                
                # Create payments table
                if 'payments' not in existing_tables:
                    print("📋 Creating payments table...")
                    payments_sql = """
                    CREATE TABLE payments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        invoice_id INTEGER NOT NULL,
                        payment_date DATE NOT NULL,
                        amount FLOAT NOT NULL,
                        payment_method VARCHAR(50) NOT NULL,
                        reference_number VARCHAR(100),
                        status VARCHAR(20) DEFAULT 'completed',
                        notes TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        created_by VARCHAR(100),
                        FOREIGN KEY (invoice_id) REFERENCES invoices (id)
                    )
                    """
                    connection.execute(text(payments_sql))
                    print("✅ Payments table created successfully!")
                else:
                    print("✅ Payments table already exists!")
                
                # Create customer_communications table
                if 'customer_communications' not in existing_tables:
                    print("📋 Creating customer_communications table...")
                    communications_sql = """
                    CREATE TABLE customer_communications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        customer_id INTEGER NOT NULL,
                        communication_type VARCHAR(50) NOT NULL,
                        subject VARCHAR(200),
                        content TEXT,
                        direction VARCHAR(20) NOT NULL,
                        status VARCHAR(20) DEFAULT 'completed',
                        follow_up_date DATE,
                        follow_up_notes TEXT,
                        invoice_id INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        created_by VARCHAR(100),
                        FOREIGN KEY (customer_id) REFERENCES customers (id),
                        FOREIGN KEY (invoice_id) REFERENCES invoices (id)
                    )
                    """
                    connection.execute(text(communications_sql))
                    print("✅ Customer communications table created successfully!")
                else:
                    print("✅ Customer communications table already exists!")
                
                # Create indexes for better performance
                print("📋 Creating indexes...")
                
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_customers_name ON customers (name)",
                    "CREATE INDEX IF NOT EXISTS idx_customers_email ON customers (email)",
                    "CREATE INDEX IF NOT EXISTS idx_customers_active ON customers (is_active)",
                    "CREATE INDEX IF NOT EXISTS idx_invoices_customer ON invoices (customer_id)",
                    "CREATE INDEX IF NOT EXISTS idx_invoices_number ON invoices (invoice_number)",
                    "CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices (invoice_date)",
                    "CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices (status)",
                    "CREATE INDEX IF NOT EXISTS idx_invoices_due_date ON invoices (due_date)",
                    "CREATE INDEX IF NOT EXISTS idx_payments_invoice ON payments (invoice_id)",
                    "CREATE INDEX IF NOT EXISTS idx_payments_date ON payments (payment_date)",
                    "CREATE INDEX IF NOT EXISTS idx_communications_customer ON customer_communications (customer_id)",
                    "CREATE INDEX IF NOT EXISTS idx_communications_type ON customer_communications (communication_type)"
                ]
                
                for index_sql in indexes:
                    connection.execute(text(index_sql))
                
                print("✅ Indexes created successfully!")
                
                connection.commit()
                print("✅ Tables created successfully - completely empty and ready for your data!")
            
            print("🎉 Sales tables migration completed successfully!")
            print("💡 Sales module is now ready with customer and AR management!")
            return True
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            return False

if __name__ == "__main__":
    run_migration()
