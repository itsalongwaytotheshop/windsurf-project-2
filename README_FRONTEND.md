# Noise Estimator Frontend & Backend

A Next.js frontend with FastAPI backend for the noise estimation calculator.

## Quick Start

### Prerequisites
- Python 3.13+ with virtual environment
- Node.js 18+
- npm

### Running the Application

The easiest way to start both servers is with the provided script:

```bash
./start_app.sh
```

This will start:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

### Manual Startup

If you prefer to start the servers manually:

1. **Start the backend:**
```bash
source venv/bin/activate
python backend_server.py
```

2. **Start the frontend (in a new terminal):**
```bash
cd frontend
npm run dev
```

## Using the Application

1. Open http://localhost:3000 in your browser
2. Fill in the calculation parameters:
   - **Assessment Type**: Choose between Distance Based or Full Estimator
   - **Calculation Mode**: Scenario, Noisiest Plant, or Individual Plant
   - **Environment Approach**: Use representative noise environment or provide custom background
   - **Time Period**: Day, Evening, or Night
   - **Propagation Type**: Rural, Urban, Hard Ground, Soft Ground, or Mixed
   - **Noise Category**: Select the appropriate noise category
   - **Scenario**: Choose the work scenario (if in scenario mode)
   - **Distance**: Enter receiver distance (for full estimator mode)
   - **Background Level**: Provide custom background (if using user-supplied approach)

3. Click "Calculate Noise Level" to see results

## Features

- **Real-time Calculation**: Instant noise level calculations
- **Impact Assessment**: Shows if the location is affected, highly affected, or not affected
- **Mitigation Measures**: Displays standard and additional mitigation measures based on impact
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Built with Next.js and shadcn/ui components

## API Endpoints

- `GET /` - API status
- `GET /health` - Health check
- `POST /calculate` - Perform noise calculation

## Development

### Frontend
- Built with Next.js 15
- Styled with Tailwind CSS
- Components from shadcn/ui
- TypeScript for type safety

### Backend
- FastAPI framework
- CORS enabled for localhost:3000
- Integrates with the Python noise estimator module

## Troubleshooting

1. **Backend not starting**: Ensure the virtual environment is activated and all dependencies are installed
2. **Frontend errors**: Check that Node.js is up to date and run `npm install` in the frontend directory
3. **CORS errors**: Make sure both servers are running and the backend is on port 8000
4. **Calculation errors**: Check the backend console for detailed error messages
