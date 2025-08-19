# EdonuOps API Documentation

## Overview

The EdonuOps API provides comprehensive RESTful endpoints for all ERP functionality. All endpoints return JSON responses and use standard HTTP status codes.

## Base URL
```
http://localhost:5000/api
```

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Common Response Format

### Success Response
```json
{
  "message": "Operation successful",
  "data": {...}
}
```

### Error Response
```json
{
  "error": "Error description",
  "status": 400
}
```

## Core Endpoints

### Dashboard
```
GET /dashboard/summary
```
Returns dashboard metrics and summary data.

**Response:**
```json
{
  "totalContacts": 25,
  "totalLeads": 12,
  "totalOpportunities": 8,
  "totalProducts": 45,
  "totalEmployees": 18,
  "totalRevenue": 125000,
  "recentTransactions": [...]
}
```

### Health Check
```
GET /health
```
Returns system health status.

## Finance Module

### Chart of Accounts
```
GET /finance/accounts
POST /finance/accounts
PUT /finance/accounts/{id}
DELETE /finance/accounts/{id}
```

**Account Object:**
```json
{
  "id": 1,
  "code": "1000",
  "name": "Cash",
  "type": "Asset",
  "description": "Cash on hand",
  "balance": 50000.00,
  "status": "Active"
}
```

### Journal Entries
```
GET /finance/journal-entries
POST /finance/journal-entries
PUT /finance/journal-entries/{id}
DELETE /finance/journal-entries/{id}
```

**Journal Entry Object:**
```json
{
  "id": 1,
  "entry_number": "JE-2024-001",
  "date": "2024-01-15",
  "description": "Monthly rent payment",
  "total_debit": 2000.00,
  "total_credit": 2000.00,
  "status": "Posted",
  "lines": [...]
}
```

## CRM Module

### Contacts
```
GET /crm/contacts
POST /crm/contacts
PUT /crm/contacts/{id}
DELETE /crm/contacts/{id}
```

**Contact Object:**
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "company": "ABC Corp",
  "status": "Active"
}
```

### Leads
```
GET /crm/leads
POST /crm/leads
PUT /crm/leads/{id}
DELETE /crm/leads/{id}
```

**Lead Object:**
```json
{
  "id": 1,
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane.smith@example.com",
  "phone": "+1234567891",
  "company": "XYZ Inc",
  "source": "Website",
  "status": "New"
}
```

### Opportunities
```
GET /crm/opportunities
POST /crm/opportunities
PUT /crm/opportunities/{id}
DELETE /crm/opportunities/{id}
```

**Opportunity Object:**
```json
{
  "id": 1,
  "title": "Software License Deal",
  "contact_id": 1,
  "amount": 25000.00,
  "stage": "Proposal",
  "probability": 75,
  "expected_close_date": "2024-03-15"
}
```

## HCM Module

### Employees
```
GET /hr/employees
POST /hr/employees
PUT /hr/employees/{id}
DELETE /hr/employees/{id}
```

**Employee Object:**
```json
{
  "id": 1,
  "first_name": "Alice",
  "last_name": "Johnson",
  "email": "alice.johnson@company.com",
  "phone": "+1234567892",
  "department": "Engineering",
  "position": "Senior Developer",
  "hire_date": "2023-01-15",
  "salary": 85000.00,
  "status": "Active"
}
```

### Payroll
```
GET /hr/payroll
POST /hr/payroll
PUT /hr/payroll/{id}
DELETE /hr/payroll/{id}
```

**Payroll Object:**
```json
{
  "id": 1,
  "employee_id": 1,
  "pay_period": "2024-01",
  "gross_pay": 7083.33,
  "net_pay": 5678.66,
  "taxes": 1404.67,
  "status": "Processed"
}
```

### Recruitment
```
GET /hr/recruitment
POST /hr/recruitment
PUT /hr/recruitment/{id}
DELETE /hr/recruitment/{id}
```

**Recruitment Object:**
```json
{
  "id": 1,
  "position": "Marketing Manager",
  "candidate_name": "Bob Wilson",
  "email": "bob.wilson@email.com",
  "phone": "+1234567893",
  "stage": "Interview",
  "status": "Active"
}
```

## Inventory Module

### Products
```
GET /inventory/products
POST /inventory/products
PUT /inventory/products/{id}
DELETE /inventory/products/{id}
```

**Product Object:**
```json
{
  "id": 1,
  "name": "Laptop Pro",
  "description": "High-performance laptop",
  "sku": "LAP-001",
  "category_id": 1,
  "price": 1299.99,
  "cost": 800.00,
  "stock_quantity": 25,
  "status": "Active"
}
```

### Categories
```
GET /inventory/categories
POST /inventory/categories
PUT /inventory/categories/{id}
DELETE /inventory/categories/{id}
```

**Category Object:**
```json
{
  "id": 1,
  "name": "Electronics",
  "description": "Electronic devices and accessories",
  "parent_id": null,
  "status": "Active"
}
```

### Warehouses
```
GET /inventory/warehouses
POST /inventory/warehouses
PUT /inventory/warehouses/{id}
DELETE /inventory/warehouses/{id}
```

**Warehouse Object:**
```json
{
  "id": 1,
  "name": "Main Warehouse",
  "location": "123 Main St, City, State",
  "capacity": 10000,
  "status": "Active"
}
```

## E-commerce Module

### Products
```
GET /ecommerce/products
POST /ecommerce/products
PUT /ecommerce/products/{id}
DELETE /ecommerce/products/{id}
```

**E-commerce Product Object:**
```json
{
  "id": 1,
  "name": "Wireless Headphones",
  "description": "Premium wireless headphones",
  "price": 199.99,
  "stock_quantity": 50,
  "category": "Audio",
  "status": "Active"
}
```

### Orders
```
GET /ecommerce/orders
POST /ecommerce/orders
PUT /ecommerce/orders/{id}
DELETE /ecommerce/orders/{id}
```

**Order Object:**
```json
{
  "id": 1,
  "order_number": "ORD-A1B2C3D4",
  "customer_name": "John Doe",
  "customer_email": "john.doe@email.com",
  "total_amount": 399.98,
  "status": "Shipped"
}
```

### Customers
```
GET /ecommerce/customers
POST /ecommerce/customers
PUT /ecommerce/customers/{id}
DELETE /ecommerce/customers/{id}
```

**Customer Object:**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@email.com",
  "phone": "+1234567890",
  "total_orders": 5,
  "total_spent": 1250.00
}
```

## AI Module

### Predictions
```
GET /ai/predictions
POST /ai/predictions
PUT /ai/predictions/{id}
DELETE /ai/predictions/{id}
```

**Prediction Object:**
```json
{
  "id": 1,
  "title": "Sales Forecast Q2",
  "description": "AI-powered sales forecast for Q2 2024",
  "prediction_type": "Sales",
  "accuracy": 87.5,
  "confidence_score": 0.92,
  "status": "Active"
}
```

### Insights
```
GET /ai/insights
POST /ai/insights
PUT /ai/insights/{id}
DELETE /ai/insights/{id}
```

**Insight Object:**
```json
{
  "id": 1,
  "title": "Customer Churn Risk",
  "description": "High-risk customers identified",
  "insight_type": "Risk Analysis",
  "impact_score": 8.5,
  "category": "Customer",
  "status": "Active"
}
```

### Recommendations
```
GET /ai/recommendations
POST /ai/recommendations
PUT /ai/recommendations/{id}
DELETE /ai/recommendations/{id}
```

**Recommendation Object:**
```json
{
  "id": 1,
  "title": "Inventory Optimization",
  "description": "Optimize stock levels for better cash flow",
  "recommendation_type": "Operations",
  "priority": "High",
  "implementation_status": "Pending"
}
```

## Sustainability Module

### Environmental Metrics
```
GET /sustainability/environmental
POST /sustainability/environmental
PUT /sustainability/environmental/{id}
DELETE /sustainability/environmental/{id}
```

**Environmental Metric Object:**
```json
{
  "id": 1,
  "metric_name": "Carbon Footprint",
  "value": 1250.5,
  "unit": "tons CO2",
  "category": "Emissions",
  "reporting_period": "2024-Q1",
  "status": "Active"
}
```

### Social Metrics
```
GET /sustainability/social
POST /sustainability/social
PUT /sustainability/social/{id}
DELETE /sustainability/social/{id}
```

**Social Metric Object:**
```json
{
  "id": 1,
  "metric_name": "Employee Satisfaction",
  "value": 85.2,
  "unit": "percentage",
  "category": "Workplace",
  "reporting_period": "2024-Q1",
  "status": "Active"
}
```

### Governance Metrics
```
GET /sustainability/governance
POST /sustainability/governance
PUT /sustainability/governance/{id}
DELETE /sustainability/governance/{id}
```

**Governance Metric Object:**
```json
{
  "id": 1,
  "metric_name": "Board Diversity",
  "value": 40.0,
  "unit": "percentage",
  "category": "Leadership",
  "reporting_period": "2024-Q1",
  "status": "Active"
}
```

### ESG Reports
```
GET /sustainability/reports
POST /sustainability/reports
PUT /sustainability/reports/{id}
DELETE /sustainability/reports/{id}
```

**ESG Report Object:**
```json
{
  "id": 1,
  "report_title": "Annual ESG Report 2024",
  "report_type": "Annual",
  "reporting_period": "2024",
  "esg_rating": "A+",
  "status": "Published"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |

## Rate Limiting

API requests are limited to:
- 100 requests per minute per IP
- 1000 requests per hour per user

## Pagination

For endpoints that return lists, pagination is supported:

```
GET /api/endpoint?page=1&per_page=20
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

## Filtering and Sorting

Most endpoints support filtering and sorting:

```
GET /api/endpoint?filter[status]=Active&sort=name&order=asc
```

## Webhooks

Webhooks are available for real-time notifications:

```
POST /webhooks/endpoint
```

Configure webhook URLs in the system settings.

## SDKs and Libraries

### JavaScript/TypeScript
```javascript
import { EdonuOpsAPI } from '@edonuops/sdk';

const api = new EdonuOpsAPI({
  baseURL: 'http://localhost:5000/api',
  token: 'your-jwt-token'
});

// Example usage
const contacts = await api.crm.getContacts();
```

### Python
```python
from edonuops import EdonuOpsAPI

api = EdonuOpsAPI(
    base_url='http://localhost:5000/api',
    token='your-jwt-token'
)

# Example usage
contacts = api.crm.get_contacts()
```

## Testing

### Postman Collection
Import the EdonuOps API collection for testing:
```
https://api.edonuops.com/postman-collection.json
```

### API Testing
```bash
# Test health endpoint
curl -X GET http://localhost:5000/api/health

# Test authenticated endpoint
curl -X GET http://localhost:5000/api/crm/contacts \
  -H "Authorization: Bearer your-jwt-token"
```

## Support

For API support:
- Documentation: `/docs/api`
- Issues: GitHub Issues
- Email: api-support@edonuops.com

---

**EdonuOps API** - Comprehensive RESTful API for enterprise resource planning. 🚀
