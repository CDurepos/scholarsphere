# ScholarSphere Frontend

React + Vite frontend application for ScholarSphere, a platform to connect Maine Faculty for research collaboration.

## Features

- **Landing Page**: Forces users to choose between Login or Signup
- **Login Flow**: Simple username/password authentication
- **Multi-Step Signup Flow**:
  1. **Step 1**: Name and institution check
  2. **Step 2a** (if exists): "Does this look right?" - review and edit existing faculty data
  2. **Step 2b** (if new): Collect additional information (email, title, department, etc.)
  3. **Step 3**: Create credentials (username & password)
- **Dashboard**: Main application page after successful login

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Landing.jsx      # Landing page (Login/Signup choice)
│   │   ├── Login.jsx        # Login form
│   │   ├── Signup.jsx       # Multi-step signup orchestrator
│   │   ├── SignupStep1.jsx  # Name and institution
│   │   ├── SignupStep2Exists.jsx  # Review/edit existing data
│   │   ├── SignupStep2New.jsx      # Collect new user data
│   │   ├── SignupStep3.jsx  # Credentials setup
│   │   └── Dashboard.jsx    # Main dashboard
│   ├── services/
│   │   └── api.js           # API service with placeholder endpoints
│   ├── App.jsx             # Main app with routing
│   └── main.jsx            # Entry point
└── package.json
```

## API Endpoints (Placeholder)

All API endpoints are documented in `src/services/api.js` with inline comments describing:
- Request method and path
- Request body structure
- Response structure
- Example responses

### Key Endpoints:

1. **POST /api/faculty/check** - Check if faculty exists
2. **POST /api/faculty/create** - Create new faculty member
3. **PUT /api/faculty/:faculty_id** - Update existing faculty
4. **POST /api/auth/register** - Register credentials
5. **POST /api/auth/login** - Login
6. **GET /api/institutions** - Get list of institutions

## Getting Started

### Install Dependencies

```bash
npm install
```

### Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173` (or the next available port).

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Authentication Flow

1. User lands on `/` (Landing page)
2. User chooses Login or Signup
3. **Login**: Username/password → Dashboard
4. **Signup**: 
   - Step 1: Name/Institution → Check if exists
   - Step 2a (exists): Review/edit → Step 3
   - Step 2b (new): Collect info → Step 3
   - Step 3: Credentials → Redirect to Login

## State Management

Currently using:
- React `useState` for component-level state
- `localStorage` for authentication tokens and faculty data
- React Router for navigation

## Next Steps

1. Replace placeholder API endpoints with actual backend URLs
2. Implement proper authentication context/state management
3. Add error handling and loading states
4. Implement protected routes with token validation
5. Add form validation and better UX feedback
