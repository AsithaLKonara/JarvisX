# Testing Guide - JarvisX V2 Multi-Platform UI

## Quick Start

### 1. Start Backend Server
```bash
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start Web App
```bash
cd web-app
npm run dev
```

### 3. Access Applications
- **Web App**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Test Credentials

```
Email: test@jarvisx.com
Password: test123456
```

## Testing Checklist

### Backend API Testing

1. **Health Check**
   ```bash
   curl http://localhost:8000/health
   ```
   Expected: `{"status": "healthy"}`

2. **User Registration**
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"newuser@test.com","password":"test123456","username":"newuser"}'
   ```
   Expected: Returns access_token and refresh_token

3. **User Login**
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@jarvisx.com","password":"test123456"}'
   ```
   Expected: Returns access_token and refresh_token

4. **Get User Info** (requires token)
   ```bash
   curl http://localhost:8000/api/v1/user/me \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```
   Expected: Returns user information

5. **Send Chat Message** (requires token)
   ```bash
   curl -X POST http://localhost:8000/api/v1/chat/messages \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -d '{"content":"Hello, JarvisX!"}'
   ```
   Expected: Returns AI response

### Web Application Testing

1. **Landing Page**
   - Navigate to http://localhost:3000
   - Verify gradient background
   - Check "Get Started" and "Try Demo" buttons
   - Verify liquid glass UI effects

2. **Login Page**
   - Navigate to http://localhost:3000/login
   - Enter test credentials
   - Click "Login" button
   - Verify redirect to chat page

3. **Chat Interface**
   - Navigate to http://localhost:3000/chat
   - Verify glass morphism UI
   - Check gradient blob avatar
   - Test sending a message
   - Verify AI response

4. **OAuth Buttons**
   - Click Google/Apple/Facebook buttons
   - Verify OAuth flow initiation (will redirect to providers)

### Mobile App Testing

1. **Install Dependencies**
   ```bash
   cd mobile
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm start
   # Or for specific platform:
   npm run ios
   npm run android
   ```

3. **Test Features**
   - Login/Register screens
   - Chat widget
   - OAuth authentication
   - Liquid glass UI

### Desktop App Testing

1. **Install Dependencies**
   ```bash
   cd desktop
   pip install -r requirements.txt
   ```

2. **Run Application**
   ```bash
   python3 src/main.py
   ```

3. **Test Features**
   - System tray icon
   - Chat widget window
   - Login functionality
   - Liquid glass styling

## Browser Testing

### Chrome DevTools
1. Open http://localhost:3000
2. Press F12 to open DevTools
3. Test responsive design (mobile/tablet/desktop)
4. Check console for errors
5. Verify network requests to backend

### Test Scenarios

1. **Full User Flow**
   - Register new account
   - Login
   - Send chat message
   - Receive AI response
   - Logout

2. **UI/UX Testing**
   - Verify liquid glass effects
   - Check gradient animations
   - Test responsive layouts
   - Verify button interactions
   - Check form validation

3. **Error Handling**
   - Invalid login credentials
   - Network errors
   - API failures
   - Token expiration

## API Documentation

Access interactive API documentation at:
http://localhost:8000/docs

This provides:
- All available endpoints
- Request/response schemas
- Try-it-out functionality
- Authentication testing

## Troubleshooting

### Backend Not Starting
- Check if port 8000 is available
- Verify dependencies: `pip install -r requirements.txt`
- Check database file exists: `backend/jarvisx.db`

### Web App Not Loading
- Check if port 3000 is available
- Verify dependencies: `npm install`
- Check browser console for errors

### Database Issues
- Reinitialize: `cd backend && python3 init_db.py`
- Check SQLite file permissions
- Verify database file exists

### Authentication Failing
- Verify test user exists in database
- Check JWT secret key in config
- Verify token expiration settings

## Performance Testing

1. **Response Times**
   - Health check: < 100ms
   - Login: < 500ms
   - Chat message: < 5s (depends on AI)

2. **Load Testing**
   - Use tools like Apache Bench or wrk
   - Test concurrent requests
   - Monitor backend logs

## Security Testing

1. **JWT Tokens**
   - Verify token expiration
   - Test token refresh
   - Check invalid token handling

2. **OAuth**
   - Test OAuth callback handling
   - Verify state parameter validation
   - Check token exchange

3. **Input Validation**
   - Test SQL injection attempts
   - Verify XSS protection
   - Check CSRF protection

## Next Steps

1. ✅ Database setup complete
2. ✅ Dependencies installed
3. ✅ Services running
4. ⏳ Complete browser testing
5. ⏳ Test mobile app
6. ⏳ Test desktop app
7. ⏳ Performance optimization
8. ⏳ Production deployment

