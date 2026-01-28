# VMC Bridge - Frontend

React-based frontend application for VMC Bridge vulnerability management platform.

## 🚀 Quick Start

### Option 1: Use Root Start Script (Recommended)
```powershell
# From project root - starts backend, worker, and frontend
.\start-all.ps1
```

### Option 2: Run Frontend Only

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

3. **Open in browser**
   ```
   http://localhost:5173
   ```

**Note**: Backend API must be running on port 8000 for full functionality.

## 🏗️ Project Structure

```
Frontend/
├── components/
│   ├── Layout.tsx           # Main layout wrapper
│   ├── Sidebar.tsx          # Navigation sidebar
│   └── SkeletonLoader.tsx   # Loading skeletons
├── contexts/
│   ├── AuthContext.tsx      # Authentication state
│   └── ToastContext.tsx     # Toast notifications
├── pages/
│   ├── Login.tsx            # Login page
│   ├── Signup.tsx           # Registration page
│   ├── Dashboard.tsx        # Main dashboard
│   ├── ScanUpload.tsx       # Scan upload page
│   ├── Vulnerabilities.tsx  # Vulnerability list
│   ├── Reports.tsx          # Detailed reports
│   └── Settings.tsx         # User settings
├── services/
│   └── api.ts               # API client & types
├── App.tsx                  # Root component
├── index.tsx                # Entry point
├── types.ts                 # TypeScript types
├── index.css                # Global styles
├── package.json             # Dependencies
├── vite.config.ts           # Vite configuration
├── tailwind.config.js       # Tailwind CSS config
└── tsconfig.json            # TypeScript config
```

## ✨ Features

### Current Features
- ✅ **Authentication** - Login/Signup with JWT
- ✅ **Dashboard** - Real-time security metrics
- ✅ **Scan Upload** - Drag-and-drop file upload
- ✅ **Vulnerability Management** - View, filter, search
- ✅ **Detailed Reports** - Comprehensive vulnerability reports
- ✅ **Responsive Design** - Works on desktop, tablet, mobile
- ✅ **Dark Theme** - Modern dark UI
- ✅ **Skeleton Loaders** - Better perceived performance
- ✅ **Toast Notifications** - User feedback
- ✅ **Real-time Updates** - Auto-refresh data

### Pages

#### 1. **Login/Signup**
- User authentication
- JWT token management
- Form validation

#### 2. **Dashboard**
- Security metrics overview
- Vulnerability counts by severity
- Recent scans feed
- Latest findings table
- Visual charts (coming soon)

#### 3. **Scan Upload**
- Drag-and-drop file upload
- Upload progress tracking
- Recent uploads table
- Job status monitoring
- File validation (format, size)

#### 4. **Vulnerabilities**
- Searchable vulnerability list
- Filter by severity (Critical, High, Medium, Low)
- Filter by status (Open, In Progress, Resolved)
- Detailed side panel
- Pagination support
- Asset information

#### 5. **Reports**
- Detailed vulnerability view
- CVE information with NVD links
- CVSS scores and vectors
- Remediation guidance
- Asset details
- Print/PDF export (coming soon)

#### 6. **Settings**
- User preferences
- System configuration
- (Coming soon)

## 🎨 Tech Stack

- **Framework**: React 18.2
- **Language**: TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Icons**: Material Symbols
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Routing**: React Router v6
- **State Management**: React Context API

## 🔧 Configuration

### Environment Variables

The frontend connects to the backend API. Update the API base URL in `services/api.ts` if needed:

```typescript
const API_BASE_URL = 'http://127.0.0.1:8000';
```

For production, set this to your production API URL.

### API Client

The `services/api.ts` file contains:
- TypeScript interfaces for all data types
- API client class with all endpoints
- JWT token management
- Error handling

Example usage:
```typescript
import { apiClient } from './services/api';

// Login
const { access_token } = await apiClient.login(email, password);

// Upload scan
const scan = await apiClient.uploadScan(file, onProgress);

// List vulnerabilities
const { items, total } = await apiClient.listVulnerabilities({
  severity: 'critical',
  limit: 50
});
```

## 🎯 Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Type check
npm run type-check
```

## 🎨 Styling

### Tailwind CSS

The project uses Tailwind CSS with a custom dark theme:

**Color Palette**:
- `background`: #12151A (dark background)
- `surface`: #1A1D23 (cards, panels)
- `border`: #283039 (borders, dividers)
- `primary`: #1169D4 (blue accent)
- `danger`: #DC2626 (red for critical)
- `success`: #10B981 (green for success)

**Custom Classes**:
- `custom-scroll`: Styled scrollbars
- Various semantic color utilities

### Material Symbols

Icons are from Google's Material Symbols:
```tsx
<span className="material-symbols-outlined">dashboard</span>
```

## 🔐 Authentication Flow

1. User logs in via `/login`
2. Backend returns JWT access token + refresh token
3. Frontend stores tokens in memory (AuthContext)
4. All API requests include `Authorization: Bearer <token>`
5. On 401 error, attempt token refresh
6. If refresh fails, redirect to login

**Security Features**:
- Tokens stored in memory (not localStorage)
- Automatic token refresh
- Protected routes with auth guard
- Session timeout handling

## 📱 Responsive Design

The UI is fully responsive:

- **Desktop** (1024px+): Full sidebar, multi-column layouts
- **Tablet** (768px-1023px): Collapsible sidebar, 2-column layouts
- **Mobile** (< 768px): Bottom navigation, single column

## 🧪 Testing

```bash
# Run tests (when configured)
npm run test

# Run E2E tests (when configured)
npm run test:e2e
```

## 🚀 Production Build

### Build for Production

```bash
npm run build
```

This creates an optimized build in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

### Deploy

The `dist/` folder can be deployed to:
- **Vercel**: `vercel deploy`
- **Netlify**: Drag & drop `dist/` folder
- **AWS S3 + CloudFront**: Upload to S3
- **Nginx**: Serve `dist/` as static files

Example Nginx config:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /path/to/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

## 🐛 Troubleshooting

### Cannot connect to backend

**Error**: `Network Error` or `Failed to fetch`

**Solution**:
1. Verify backend is running: `http://127.0.0.1:8000/health`
2. Check CORS settings in backend `main.py`
3. Verify API_BASE_URL in `services/api.ts`

### Build errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf .vite
npm run dev
```

### TypeScript errors

```bash
# Run type check
npm run type-check

# Common fix: update types
npm install --save-dev @types/react @types/react-dom
```

### Port 5173 already in use

```bash
# Kill process (macOS/Linux)
lsof -ti:5173 | xargs kill -9

# Kill process (Windows)
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Or use different port
npm run dev -- --port 3000
```

## 📦 Key Dependencies

```json
{
  "react": "^18.2.0",
  "react-router-dom": "^6.20.0",
  "axios": "^1.6.0",
  "recharts": "^2.10.0",
  "tailwindcss": "^3.3.0"
}
```

## 🎯 Performance Optimizations

- ✅ Code splitting with React.lazy()
- ✅ Skeleton loaders for perceived performance
- ✅ Optimized re-renders with React.memo()
- ✅ Debounced search inputs
- ✅ Pagination for large lists
- ✅ Vite for fast builds and HMR

## 🔄 State Management

The app uses React Context API for global state:

### AuthContext
- User authentication state
- Login/logout functions
- Token management
- Auto-refresh logic

### ToastContext
- Global toast notifications
- Success/error/info messages
- Auto-dismiss after 3s

## 📚 Additional Resources

- [Main README](../README.md) - Overall project documentation
- [Backend README](../Backend/README.md) - Backend setup
- [Project Overview](../PROJECT_OVERVIEW.md) - Complete project description
- [Production Checklist](../PRODUCTION_READINESS_CHECKLIST.md) - Deployment guide

## 🤝 Contributing

1. Follow React best practices
2. Use TypeScript for type safety
3. Follow Tailwind CSS utility-first approach
4. Add proper error handling
5. Test on multiple screen sizes

## 📄 License

MIT License - See LICENSE file for details
