# EdonuOps Enterprise ERP System

A comprehensive enterprise resource planning (ERP) system built with modern technologies.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd EdonuOps
   ```

2. **Run the startup script**
   ```bash
   python start_edonuops.py
   ```

This script will:
- Install all Python dependencies
- Create a virtual environment
- Initialize the database with sample data
- Install Node.js dependencies
- Start both backend and frontend servers

### Manual Setup (Alternative)

#### Backend Setup
   ```bash
   cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate
   pip install -r requirements.txt
python init_database.py
   python run.py
   ```

#### Frontend Setup
   ```bash
   cd frontend
   npm install
   npm start
   ```

## 🌐 Access Points

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/health
- **API Documentation**: http://localhost:5000/docs

## 🔐 Default Login

- **Username**: admin
- **Email**: admin@edonuops.com
- **Password**: admin123

## 📋 System Modules

### Core Modules
- **Finance**: Chart of accounts, journal entries, invoicing, payments
- **Inventory**: Product management, stock tracking, warehouses
- **CRM**: Contact management, leads, opportunities, sales pipeline
- **HCM**: Employee management, payroll, recruitment
- **E-commerce**: Online store management, orders, customers
- **AI Intelligence**: AI-powered insights and automation
- **Sustainability**: ESG tracking and reporting

### Enterprise Features
- Multi-tenancy support
- Role-based access control
- Workflow automation
- Real-time data synchronization
- API integrations
- Audit logging
- Performance monitoring

## 🛠️ Development

### Backend Structure
```
backend/
├── app/                 # Flask application factory
├── modules/            # Business logic modules
│   ├── core/          # Core functionality
│   ├── finance/       # Financial management
│   ├── inventory/     # Inventory management
│   ├── crm/          # Customer relationship management
│   ├── hr/           # Human resources
│   └── ...
├── routes/            # API route definitions
├── services/          # Business services
└── config/           # Configuration files
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/    # Reusable UI components
│   ├── modules/       # Feature modules
│   ├── services/      # API services
│   ├── hooks/         # Custom React hooks
│   └── utils/         # Utility functions
```

## 🔧 Configuration

### Environment Variables
Create a `backend/config.env` file with:
```env
DATABASE_URL=sqlite:///edonuops.db
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
FLASK_ENV=development
FLASK_DEBUG=True
```

### Database
The system uses SQLite by default for development. For production, configure PostgreSQL:
```env
DATABASE_URL=postgresql://user:password@localhost/edonuops
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
python test_minimal.py
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📊 API Endpoints

### Finance
- `GET /api/finance/accounts` - Get chart of accounts
- `POST /api/finance/accounts` - Create account
- `GET /api/finance/journal-entries` - Get journal entries
- `POST /api/finance/journal-entries` - Create journal entry

### Inventory
- `GET /api/inventory/products` - Get products
- `POST /api/inventory/products` - Create product
- `GET /api/inventory/categories` - Get categories
- `GET /api/inventory/warehouses` - Get warehouses

### CRM
- `GET /api/crm/contacts` - Get contacts
- `POST /api/crm/contacts` - Create contact
- `GET /api/crm/leads` - Get leads
- `GET /api/crm/opportunities` - Get opportunities

### HCM
- `GET /api/hr/employees` - Get employees
- `POST /api/hr/employees` - Create employee
- `GET /api/hr/departments` - Get departments

## 🚀 Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Production Setup
1. Set up a production database (PostgreSQL recommended)
2. Configure environment variables for production
3. Set up a reverse proxy (nginx)
4. Configure SSL certificates
5. Set up monitoring and logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API endpoints

## 🔄 Updates

To update the system:
1. Pull the latest changes
2. Run database migrations if needed
3. Restart the services

---

**EdonuOps** - Empowering businesses with comprehensive ERP solutions.
