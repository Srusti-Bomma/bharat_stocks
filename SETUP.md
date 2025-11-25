# Bharat Stocks Insight - Setup Guide

## Backend Setup ✅ COMPLETED

### 1. Install Dependencies
The required packages should already be installed. If not:
```bash
pip install -r requirements.txt
```

### 2. Initialize Database and Create Admin User
```bash
python backend/init_admin.py
```

This will:
- Create the `users` table in MySQL
- Create admin user with credentials:
  - Username: `srushti`
  - Password: `12345`

### 3. Start the Backend Server
```bash
python -m uvicorn backend.app.main:app --reload
```

The API will run on `http://127.0.0.1:8000`

### 4. Verify Backend
Open: http://127.0.0.1:8000/docs

## Frontend Setup 🚧 IN PROGRESS

### Files Created:
- ✅ `frontend/index.html` - Login page
- ✅ `frontend/css/styles.css` - Custom styles
- ✅ `frontend/js/auth.js` - Authentication utilities

### Still Need to Create:
- `frontend/register.html` - Registration page
- `frontend/dashboard.html` - Main dashboard
- `frontend/trending.html` - Trending stocks page
- `frontend/most-active.html` - Most active stocks page
- `frontend/news.html` - News page
- `frontend/powerbi.html` - Power BI dashboard page
- `frontend/js/app.js` - Main application logic

## API Endpoints Available

### Authentication:
- POST `/auth/register` - Register new user
- POST `/auth/login` - Login user
- GET `/auth/me` - Get current user info
- GET `/auth/users` - Get all users (Admin only)

### Stocks:
- GET `/api/fetch-now?symbol=X` - Get single stock
- GET `/api/live-data?symbols=X,Y` - Get multiple stocks
- GET `/api/most-active` - Most active stocks
- GET `/api/trending` - Trending stocks (gainers/losers)

### News:
- GET `/api/news` - GNews API
- GET `/api/news-indian` - Indian API news

## Testing

### Test Backend:
```powershell
# Health check
Invoke-WebRequest -Uri "http://127.0.0.1:8000/"

# Test stock endpoint
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/fetch-now?symbol=TCS"
```

### Test Frontend:
1. Open `frontend/index.html` in browser
2. Login with admin credentials (srushti / 12345)
3. Or register a new user

## Next Steps

1. Run `python backend/init_admin.py` to create admin user
2. Start backend server
3. I'll continue creating the remaining frontend pages
4. Test authentication flow
5. Complete all pages with stock data integration

## Admin Credentials
- Username: `srushti`
- Password: `12345`
- ⚠️ Change password after first login!
