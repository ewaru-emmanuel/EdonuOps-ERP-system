# The main application entry point for the EdonuOps backend.
# This file is responsible for creating and running the Flask application.

from app import create_app, db
# Import models to ensure they are registered with SQLAlchemy
# This is a crucial step so `db.create_all()` knows which tables to create.
from modules.finance.models import ChartOfAccount, JournalHeader, JournalLine
from modules.core.models import User, Role, Organization

# Create the Flask application instance using the factory pattern
app = create_app()

if __name__ == '__main__':
    # Use the application context to perform operations like creating tables
    with app.app_context():
        # Create all database tables based on the models defined in the modules
        db.create_all()
        
        # NOTE: You can uncomment the following block to seed the database with initial data
        # if not ChartOfAccount.query.first():
        #     print("Seeding initial data...")
        #     db.session.add(ChartOfAccount(account_name="Cash", account_type="Asset"))
        #     db.session.add(ChartOfAccount(account_name="Sales Revenue", account_type="Revenue"))
        #     db.session.commit()
        #     print("Initial data seeded.")

    # Run the Flask app in debug mode
    # It will automatically reload if code changes are detected.
    app.run(debug=True)
