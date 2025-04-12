# RAG System Frontend

This is the frontend for the RAG (Retrieval Augmented Generation) system. It's built with React, Vite, and Material-UI.

## Features

- Chat interface for anonymous users, registered users, and admins
- User authentication (login/register)
- Chat history for registered users
- Knowledge base management for admins
- Multilingual support (Vietnamese and English)
- Responsive design for all devices
- Dark/light theme support

## Tech Stack

- React 18
- TypeScript
- Vite
- Material-UI
- React Router
- i18next for internationalization
- Axios for API requests
- PM2 for production deployment

## Development

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

### Building for Production

```bash
# Build the app
npm run build

# Preview the production build
npm run preview
```

## Docker

The application can be run using Docker:

```bash
# Build and run with Docker Compose
docker-compose up -d
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
VITE_API_URL=http://localhost:6868/api
VITE_DEFAULT_LANGUAGE=vi
```

## Project Structure

- `src/components`: Reusable UI components
- `src/pages`: Application pages
- `src/contexts`: React contexts for state management
- `src/services`: API services
- `src/i18n`: Internationalization setup
- `src/types`: TypeScript type definitions
- `src/hooks`: Custom React hooks
- `src/utils`: Utility functions
