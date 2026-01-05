# Noise Assessment Wizard

A comprehensive noise estimation tool that implements the Transport for NSW Construction and Maintenance Noise Estimator with a modern step-by-step wizard interface.

## Features

- **Step-by-Step Wizard**: Guided assessment with 9 interactive steps
- **17 Work Scenarios**: Extracted from Transport for NSW spreadsheet
- **26 Equipment Types**: For noisiest plant conservative assessment
- **Comprehensive Results**: Including notifications, stakeholder requirements, work hour restrictions, and compliance needs
- **Modern UI**: Built with Next.js, TypeScript, and shadcn/ui components

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Installation

1. Clone the repository
```bash
git clone https://github.com/itsalongwaytotheshop/windsurf-project-2.git
cd windsurf-project-2
```

2. Set up Python environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

3. Install frontend dependencies
```bash
cd frontend
npm install
cd ..
```

### Running the Application

Use the provided startup script:
```bash
./start_app.sh
```

Or manually:

1. Start the backend:
```bash
source venv/bin/activate
python backend_server.py
```

2. Start the frontend (in a new terminal):
```bash
cd frontend
npm run dev
```

3. Open your browser to:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Usage

1. Select assessment type (Distance Based or Full Estimator)
2. Choose calculation mode (Scenario, Noisiest Plant, or Individual Plant)
3. Follow the step-by-step wizard
4. View comprehensive results including:
   - Noise level predictions
   - Notification requirements
   - Stakeholder communication needs
   - Work hour restrictions
   - Compliance requirements
   - Mitigation measures

## Project Structure

```
windsurf-project-2/
├── backend_server.py          # FastAPI backend server
├── noise_estimator/          # Core noise calculation engine
├── frontend/                 # Next.js frontend application
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── app/             # Next.js app router
│   │   └── types/           # TypeScript type definitions
│   └── public/              # Static assets and data files
├── datasets/                 # Noise calculation datasets
├── docs/                    # Documentation and analysis
└── extract_*.py            # Data extraction scripts
```

## Data Sources

This tool uses data from:
- Transport for NSW "Construction and Maintenance Noise Estimator (Roads)"
- EPA Interim Construction Noise Guidelines
- Industry standard equipment sound power levels

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is for educational and demonstration purposes.

## Acknowledgments

- Transport for NSW for the original noise estimator methodology
- EPA NSW for noise guideline references
