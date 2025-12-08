# Frontend - Resume Processing Pipeline UI

React + Vite frontend for the Resume Processing Pipeline.

## Features

- 📤 **Upload Resumes** - Drag & drop or select PDF/Image/DOCX files
- 📊 **Job Status** - Real-time job status tracking
- 👁️ **Preview** - View generated resume previews
- 🚀 **Deploy** - Deploy generated portfolios to Vercel
- 📝 **Logs** - View processing logs and AI interactions

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The frontend runs on `http://localhost:3001` and proxies API requests to `http://localhost:8000`.

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Axios** - HTTP client

