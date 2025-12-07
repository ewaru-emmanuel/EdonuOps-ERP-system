# EdonuOps Developer Guide

## Welcome Developers! 🚀

This guide will help you understand the EdonuOps ERP system architecture, extend functionality, and contribute to the project.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Development Setup](#development-setup)
3. [Frontend Development](#frontend-development)
4. [Backend Development](#backend-development)
5. [Database Design](#database-design)
6. [API Development](#api-development)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Contributing](#contributing)

## Architecture Overview

### Technology Stack

**Frontend:**
- React.js 18 with functional components and hooks
- Material-UI (MUI) for UI components
- Custom hooks for real-time data management
- Context API for state management

**Backend:**
- Flask Python web framework
- SQLAlchemy ORM for database operations
- Blueprint architecture for modular design
- JWT authentication

**Database:**
- SQLite (development)
- PostgreSQL (production recommended)

### Project Structure

```
EdonuOps/
├── frontend/                 # React.js application
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── modules/          # Feature modules
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API services
│   │   └── App.jsx          # Main application
│   └── package.json
├── backend/                  # Flask application
│   ├── app/
│   │   └── __init__.py      # Flask app factory
│   ├── modules/             # Feature modules
│   ├── services/           # Business logic
│   └── run.py              # Server entry point
└── docs/                   # Documentation
```

## Development Setup

### Prerequisites

- Node.js 16+ and npm
- Python 3.8+ and pip
- Git
- Code editor (VS Code recommended)

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd EdonuOps
   ```

2. **Backend setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment variables**
   ```bash
   # Backend (.env)
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///edonuops.db
   
   # Frontend (.env)
   REACT_APP_API_URL=http://localhost:5000/api
   ```
   
   **📖 For comprehensive URL configuration and deployment setup, see [URL Configuration Guide](URL_CONFIGURATION_GUIDE.md)**

### Development Commands

```bash
# Backend
cd backend
python run.py                    # Start development server
python update_database.py        # Update database schema

# Frontend
cd frontend
npm start                       # Start development server
npm run build                   # Build for production
npm test                        # Run tests
```

## Frontend Development

### Component Architecture

#### Reusable Components

**ImprovedForm Component**
```jsx
import ImprovedForm from '../../components/ImprovedForm';

<ImprovedForm
  open={formOpen}
  onClose={() => setFormOpen(false)}
  type="contact"
  data={selectedContact}
  onSubmit={handleSubmit}
/>
```

**DetailViewModal Component**
```jsx
import DetailViewModal from '../../components/DetailViewModal';

<DetailViewModal
  open={detailOpen}
  onClose={() => setDetailOpen(false)}
  type="contact"
  data={selectedContact}
  onEdit={handleEdit}
/>
```

#### Custom Hooks

**useRealTimeData Hook**
```jsx
import { useRealTimeData } from '../../hooks/useRealTimeData';

const { 
  data: contacts, 
  loading, 
  error,
  create: createContact,
  update: updateContact,
  remove: deleteContact
} = useRealTimeData('/api/crm/contacts');
```

### Creating New Modules

1. **Create module directory**
   ```bash
   mkdir frontend/src/modules/yourmodule
   ```

2. **Create main module component**
   ```jsx
   // YourModule.jsx
   import React, { useState } from 'react';
   import { useRealTimeData } from '../../hooks/useRealTimeData';
   import ImprovedForm from '../../components/ImprovedForm';
   import DetailViewModal from '../../components/DetailViewModal';

   const YourModule = () => {
     const { data, loading, create, update, remove } = useRealTimeData('/api/yourmodule');
     
     // Component logic
   };

   export default YourModule;
   ```

3. **Add to navigation**
   ```jsx
   // App.jsx
   import YourModule from './modules/yourmodule/YourModule';

   // Add to routes
   <Route path="/yourmodule" element={<YourModule />} />
   ```

### Styling Guidelines

- Use Material-UI components
- Follow the established theme
- Use responsive design principles
- Maintain accessibility standards

```jsx
// Example styling
<Box sx={{ 
  display: 'flex', 
  flexDirection: 'column', 
  gap: 2,
  p: 3 
}}>
  <Typography variant="h4" component="h1">
    Module Title
  </Typography>
</Box>
```

## Backend Development

### Module Structure

Each module follows this structure:
```
modules/yourmodule/
├── __init__.py          # Module initialization
├── models.py           # Database models
├── routes.py           # API endpoints
└── services.py         # Business logic (optional)
```

### Creating New Modules

1. **Create module directory**
   ```bash
   mkdir backend/modules/yourmodule
   ```

2. **Create models**
   ```python
   # models.py
   from app import db
   from datetime import datetime

   class YourModel(db.Model):
       __tablename__ = 'your_models'
       
       id = db.Column(db.Integer, primary_key=True)
       name = db.Column(db.String(255), nullable=False)
       description = db.Column(db.Text)
       created_at = db.Column(db.DateTime, default=datetime.utcnow)
       updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
   ```

3. **Create routes**
   ```python
   # routes.py
   from flask import Blueprint, request, jsonify
   from app import db
   from .models import YourModel
   from datetime import datetime

   yourmodule_bp = Blueprint('yourmodule', __name__)

   @yourmodule_bp.route('/yourmodels', methods=['GET'])
   def get_yourmodels():
       try:
           models = YourModel.query.all()
           return jsonify([{
               'id': m.id,
               'name': m.name,
               'description': m.description,
               'created_at': m.created_at.isoformat()
           } for m in models]), 200
       except Exception as e:
           return jsonify({'error': str(e)}), 500

   @yourmodule_bp.route('/yourmodels', methods=['POST'])
   def create_yourmodel():
       try:
           data = request.get_json()
           model = YourModel(
               name=data['name'],
               description=data.get('description', '')
           )
           db.session.add(model)
           db.session.commit()
           return jsonify({'message': 'Model created successfully', 'id': model.id}), 201
       except Exception as e:
           db.session.rollback()
           return jsonify({'error': str(e)}), 500
   ```

4. **Register blueprint**
   ```python
   # app/__init__.py
   try:
       from modules.yourmodule.routes import yourmodule_bp
       app.register_blueprint(yourmodule_bp, url_prefix="/api/yourmodule")
       print("✅ YourModule blueprint registered")
   except ImportError:
       print("⚠️ YourModule not available")
   ```

### Database Models

#### Model Guidelines

- Use descriptive table names
- Include timestamps (created_at, updated_at)
- Use appropriate data types
- Add indexes for performance
- Include proper relationships

```python
# Example model with relationships
class ParentModel(db.Model):
    __tablename__ = 'parent_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    children = db.relationship('ChildModel', backref='parent', lazy=True)

class ChildModel(db.Model):
    __tablename__ = 'child_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent_models.id'), nullable=False)
```

### API Development

#### Response Format

**Success Response**
```python
return jsonify({
    'message': 'Operation successful',
    'data': result_data
}), 200
```

**Error Response**
```python
return jsonify({
    'error': 'Error description',
    'status': 400
}), 400
```

#### Error Handling

```python
@yourmodule_bp.route('/yourmodels/<int:model_id>', methods=['PUT'])
def update_yourmodel(model_id):
    try:
        model = YourModel.query.get_or_404(model_id)
        data = request.get_json()
        
        model.name = data.get('name', model.name)
        model.description = data.get('description', model.description)
        model.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'message': 'Model updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
```

## Database Design

### Schema Management

1. **Create migration script**
   ```python
   # update_database.py
   from app import create_app, db
   
   def update_database():
       app = create_app()
       with app.app_context():
           from modules.yourmodule import models
           db.create_all()
   ```

2. **Run migration**
   ```bash
   python update_database.py
   ```

### Best Practices

- Use meaningful table and column names
- Include proper constraints
- Add indexes for frequently queried columns
- Use foreign keys for relationships
- Include audit fields (created_by, updated_by)

## Testing

### Frontend Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test -- YourComponent.test.js
```

**Example Test**
```jsx
import { render, screen, fireEvent } from '@testing-library/react';
import YourComponent from './YourComponent';

test('renders component correctly', () => {
  render(<YourComponent />);
  expect(screen.getByText('Your Component')).toBeInTheDocument();
});
```

### Backend Testing

```python
# test_yourmodule.py
import unittest
from app import create_app, db
from modules.yourmodule.models import YourModel

class YourModuleTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def test_get_yourmodels(self):
        response = self.client.get('/api/yourmodule/yourmodels')
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
```

### API Testing

```bash
# Test with curl
curl -X GET http://localhost:5000/api/yourmodule/yourmodels

# Test with Postman
# Import the API collection and test endpoints
```

## Deployment

### Production Setup

1. **Environment Configuration**
   ```bash
   # Production environment variables
   FLASK_ENV=production
   DATABASE_URL=postgresql://user:pass@host:port/db
   SECRET_KEY=your-production-secret-key
   ```

2. **Database Setup**
   ```bash
   # Use PostgreSQL for production
   pip install psycopg2-binary
   ```

3. **WSGI Configuration**
   ```python
   # wsgi.py
   from app import create_app
   
   app = create_app()
   
   if __name__ == "__main__":
       app.run()
   ```

4. **Frontend Build**
   ```bash
   cd frontend
   npm run build
   ```

**📖 For detailed deployment instructions for AWS, GoDaddy, Render, Heroku, and other platforms, see [URL Configuration Guide](URL_CONFIGURATION_GUIDE.md)**

## Contributing

### Development Workflow

1. **Fork the repository**
2. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature
   ```
3. **Make changes**
4. **Add tests**
5. **Commit changes**
   ```bash
   git commit -m "feat: add your feature"
   ```
6. **Push to branch**
   ```bash
   git push origin feature/your-feature
   ```
7. **Create pull request**

### Code Standards

#### Frontend
- Use functional components with hooks
- Follow ESLint configuration
- Use TypeScript for type safety (recommended)
- Write unit tests for components

#### Backend
- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions
- Include error handling

#### Git Commits
- Use conventional commit format
- Write descriptive commit messages
- Keep commits focused and atomic

### Pull Request Guidelines

1. **Title**: Clear description of changes
2. **Description**: Detailed explanation of changes
3. **Tests**: Include or update tests
4. **Documentation**: Update relevant docs
5. **Screenshots**: For UI changes

## Performance Optimization

### Frontend
- Use React.memo for expensive components
- Implement code splitting
- Optimize bundle size
- Use lazy loading for routes

### Backend
- Add database indexes
- Implement caching
- Use connection pooling
- Optimize database queries

### Database
- Regular maintenance
- Monitor query performance
- Use appropriate indexes
- Consider read replicas for scaling

## Security Best Practices

### Authentication
- Use JWT tokens
- Implement token refresh
- Secure token storage
- Add rate limiting

### Data Validation
- Validate all inputs
- Sanitize user data
- Use parameterized queries
- Implement CSRF protection

### API Security
- Use HTTPS in production
- Implement API versioning
- Add request logging
- Monitor for suspicious activity

## Monitoring and Logging

### Application Monitoring
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    return jsonify({'error': 'Internal server error'}), 500
```

### Performance Monitoring
- Monitor API response times
- Track database query performance
- Monitor memory usage
- Set up alerts for errors

## Support and Resources

### Documentation
- [React Documentation](https://reactjs.org/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Material-UI Documentation](https://mui.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

### Community
- GitHub Issues for bug reports
- GitHub Discussions for questions
- Stack Overflow for technical help
- Discord/Slack for real-time support

---

**Happy Coding! 🚀**

The EdonuOps development team is here to help you build amazing features and contribute to the future of enterprise resource planning.
