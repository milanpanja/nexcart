# NexCart — Full-Stack E-Commerce Platform

## 🚀 Quick Start

```bash
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers Pillow
cd /home/claude
python manage.py runserver 0.0.0.0:8000
```
Open: http://localhost:8000

## 🔑 Demo Accounts
| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| User | demo | demo123 |

## 🏗️ Architecture

### Backend (Django + SQLite3 + JWT)
- **Authentication**: JWT via `djangorestframework-simplejwt`
- **API**: Django REST Framework with ViewSets
- **Database**: SQLite3 (easy to switch to PostgreSQL)

### Frontend (HTML + CSS + Vanilla JS)
- Single-page application with client-side routing
- Dark purple/violet aesthetic with glassmorphism
- Fully responsive (mobile-first)
- AI assistant powered by Claude claude-sonnet-4-6

## 📦 Features

### User Features
- Browse & search products by category
- Product detail with rating, stock info
- Shopping cart with quantity management
- Checkout with 4 payment methods (UPI, Card, Wallet, COD)
- Order history with status tracking
- Personal dashboard (spending, orders)
- Profile management
- 🤖 AI shopping assistant

### Admin Features
- Dashboard with revenue analytics
- Product management (add/edit/delete)
- Order management with status updates
- User management
- Low stock alerts

### AI Assistant
- Powered by Claude claude-sonnet-4-6 API
- Context-aware (knows user, cart, store)
- Product recommendations
- Order help & navigation

## 🔌 API Endpoints
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| /api/token/ | POST | No | Get JWT token |
| /api/register/ | POST | No | Create account |
| /api/products/ | GET | No | List products |
| /api/products/:id/ | GET/PUT/DELETE | Admin | Product CRUD |
| /api/categories/ | GET | No | List categories |
| /api/cart/ | GET/POST/DELETE | User | Cart management |
| /api/orders/ | GET/POST | User | Orders |
| /api/orders/:id/update_status/ | PATCH | Admin | Update order |
| /api/profile/ | GET/PUT | User | User profile |
| /api/user-dashboard/ | GET | User | Dashboard stats |
| /api/admin-dashboard/ | GET | Admin | Admin stats |
| /api/admin-users/ | GET | Admin | All users |
