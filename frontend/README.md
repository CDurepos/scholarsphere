# ScholarSphere Frontend

Written by Clayton Durepos

React + Vite frontend application for ScholarSphere, a platform to connect Maine faculty for research collaboration.

## Project Structure

```
frontend/
├── src/
│   ├── components/          # App-wide reusable components
│   ├── features/            # Page-specific components
│   ├── pages/               # Page components (routes)
│   ├── services/            # API service layer
│   ├── assets/              # Static assets (images, etc.)
│   ├── App.jsx              # Main app component with routing
│   ├── App.css              # Global app styles
│   ├── main.jsx             # Application entry point
│   └── index.css            # Global CSS variables and base styles
└── package.json
```

## Directory Purposes

### `components/` - App-Wide Components

Reusable components used across multiple pages throughout the application.

**Examples:**
- `Header.jsx` - Navigation header with profile dropdown, used on all authenticated pages
- `ConnectionParticles.jsx` - Animated particle background component, used on landing and auth pages

**Characteristics:**
- Shared across multiple pages
- Self-contained with their own styles (CSS modules)
- No page-specific logic

### `features/` - Page-Specific Components

Components that are specific to a particular page or feature, but are complex enough to be extracted into separate files.

**Examples:**
- `signup/SignupSteps.jsx` - Multi-step signup form components (BasicInfoForm, ConfirmationStep, ProfileInfoForm, CredentialsForm)

**Characteristics:**
- Used by a single page or closely related pages
- Contains page-specific business logic
- Organized by feature name (e.g., `signup/`, `recommendations/`)

### `pages/` - Page Components

Top-level page components that correspond to routes in the application.

**Examples:**
- `Dashboard.jsx` - Main dashboard page showing recommendations
- `Landing.jsx` - Landing page with hero section
- `Login.jsx` - Login page
- `Signup.jsx` - Signup page orchestrator
- `Profile.jsx` - Faculty profile page
- `Search/` - Search pages (Faculty, Equipment, Grants, Institutions)

**Characteristics:**
- One component per route
- Each page has its own CSS module (e.g., `Dashboard.module.css`)
- May use components from `components/` and `features/`
- Handle page-level state and routing

### `services/` - API Service Layer

API communication layer that handles all HTTP requests to the backend.

**Files:**
- `api.js` - Contains all API service functions for:
  - Authentication (login, register, refresh, logout)
  - Faculty operations (get, create, update, search)
  - Keywords (search, get, update)
  - Recommendations (generate, get)
  - Search (faculty, keywords, equipment)
  - Institutions (list)

**Characteristics:**
- Centralized API communication
- Handles token management and refresh
- Provides consistent error handling
- Returns promises for async operations

## Styling

The application uses **CSS Modules** for component-scoped styling:

- Each component has a corresponding `.module.css` file
- Styles are imported and used via `styles.className`
- Global styles are in `index.css` (CSS variables, base styles)
- App-wide styles are in `App.css`

**Example:**
```jsx
import styles from './Dashboard.module.css';

function Dashboard() {
  return <div className={styles['dashboard-container']}>...</div>;
}
```

## State Management

- **React `useState`** - Component-level state
- **React `useEffect`** - Side effects and data fetching
- **localStorage** - Persistence for:
  - Authentication tokens (access token)
  - Faculty data
  - User preferences (e.g., dark mode)
- **React Router** - Navigation and route management

## Authentication

Authentication is handled via JWT tokens:

- **Access tokens** - Stored in memory/localStorage, short-lived
- **Refresh tokens** - Stored in HttpOnly cookies, long-lived
- Token refresh happens automatically via `api.js` interceptors
- Protected routes use the `require_auth` pattern (handled by backend)

## Dark Mode

The application supports dark mode:

- Toggle available in the Header dropdown (authenticated users only)
- Preference stored in `localStorage`
- CSS variables in `index.css` switch between light and dark themes
- Uses `:root.dark` selector for dark mode styles
