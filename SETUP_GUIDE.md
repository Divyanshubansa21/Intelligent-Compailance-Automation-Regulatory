# 🛡️ Intelligent Compliance Automation System

A professional-grade full-stack web application for intelligent transaction compliance validation, risk scoring, and AI-powered explanations.

## ✨ Features

### 🔐 Security & Authentication
- User registration with email validation
- Secure login with password hashing (werkzeug.security)
- Session-based authentication
- SQLite database for secure user storage
- Password strength requirements

### ✅ Compliance Validation
- **Email Validation**: Must contain "@" symbol
- **Transaction Amount Check**: Flags amounts > $100,000 as high risk
- **GST Validation**: Only accepts 5%, 12%, 18%, or 28%
- Real-time validation feedback
- Detailed violation reporting

### 📊 Risk Scoring System
- Automated risk score calculation (0-100)
- Three-tier risk classification:
  - 🟢 **Low Risk**: Score 0 (No violations)
  - 🟡 **Medium Risk**: Score 25-50 (1-2 violations)
  - 🔴 **High Risk**: Score 75-100 (3+ violations)

### 🤖 AI Integration
- **Groq API Integration**: Generates human-readable explanations
- **Smart Fallback**: Rule-based explanations if API unavailable
- **Secure Configuration**: API key loaded from .env file

### 📁 Batch Processing
- CSV file upload for bulk validation
- Multi-record processing
- Summary statistics
- Detailed results table

### 📥 Report Generation
- Download compliance reports as CSV
- Full transaction history export
- Timestamps and detailed violation tracking

### 🎨 Modern UI/UX
- Dark theme with neon green accents
- Glassmorphism design elements
- Responsive layout (mobile, tablet, desktop)
- Smooth animations and transitions
- Professional cybersecurity dashboard aesthetic

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Flask (Python) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Database** | SQLite3 |
| **Authentication** | Werkzeug Security |
| **AI/ML** | Groq API |
| **Environment** | python-dotenv |

## 📋 Requirements

- Python 3.8+
- pip package manager
- 100MB free disk space

## 🚀 Quick Start

### 1. Initial Setup

```bash
# Clone repository
cd "Intelligent-Compailance-Automation-Regulatory"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Create .env file from template
copy .env.example .env
# OR on macOS/Linux:
# cp .env.example .env

# Edit .env and add your configuration
# Get Groq API key from: https://console.groq.com/
```

**Required variables in .env:**
```
SECRET_KEY=your-random-secret-key-here
GROQ_API_KEY=your-groq-api-key-here
```

### 3. Database Initialization

```bash
# Initialize database
python -c "from database.db import init_db; init_db()"
```

### 4. Run Application

```bash
# Start development server
python app.py

# Application available at: http://localhost:5000
```

## 📖 User Guide

### Creating an Account

1. Navigate to **Signup** page
2. Enter username (3+ characters), email, and password (6+ characters)
3. Confirm password
4. Click **"Create Account →"**
5. Redirected to login page

### Single Transaction Validation

1. Login to dashboard
2. Fill in compliance form:
   - **Customer Email**: Valid email address
   - **Transaction Amount**: Dollar amount
   - **GST Rate**: Select from 5%, 12%, 18%, or 28%
3. Click **"✓ Validate Transaction"**
4. View:
   - Compliance status (Compliant/Non-Compliant)
   - Violations list (if any)
   - Risk level and score
   - AI-powered explanation

### Batch Processing (CSV Upload)

1. Prepare CSV file with columns:
   ```
   Customer Email,Transaction Amount,GST
   john@example.com,50000,18
   jane@example.com,150000,12
   ```

2. In Dashboard:
   - Drag & drop CSV or click upload area
   - View processing results
   - See summary statistics

### Download Reports

1. Click **"📥 Download Report"** button
2. CSV file automatically downloads
3. Contains all validations with:
   - Date/Time
   - Email
   - Amount
   - GST Rate
   - Compliance Status
   - Risk Level
   - Violations

## 📊 Compliance Rules

### Email Validation
- **Rule**: Must contain "@" symbol
- **Violation**: "Invalid email format (must contain @)"

### Transaction Amount
- **Rule**: Maximum amount is $100,000
- **Violation**: "High transaction amount: $X (exceeds $100,000)"

### GST Rate
- **Rule**: Must be exactly 5%, 12%, 18%, or 28%
- **Violation**: "Invalid GST rate: X% (must be one of: 5, 12, 18, 28)"

## 🤖 AI Explanations

### Groq API
- Analyzes violations in business context
- Generates professional recommendations
- Takes risk score into account

### Fallback Mode
- Activates if API unavailable or no key configured
- Provides rule-based explanations
- Shows risk level and required actions

## 🔒 Security Features

### Password Management
- Passwords hashed with werkzeug.security
- Never stored in plain text
- Requirements: 6+ characters

### API Keys
- Loaded from .env file (never hardcoded)
- .env excluded from git (.gitignore)
- Groq API key never exposed in code

### Session Security
- Flask session-based authentication
- Automatic session timeout
- CSRF protection ready

## 📁 Project Structure

```
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore rules
├── database/
│   └── db.py                      # Database initialization & helpers
├── services/
│   ├── compliance_rules.py        # Compliance validation engine
│   ├── groq_explainer.py          # Groq API integration
│   ├── csv_processor.py           # CSV batch processing
│   ├── document_parser.py         # PDF extraction (existing)
│   └── compliance_checker.py      # Similarity checking (existing)
├── templates/
│   ├── base.html                  # Base template with navigation
│   ├── login.html                 # Login page
│   ├── signup.html                # Registration page
│   ├── dashboard.html             # Main dashboard
│   └── error.html                 # Error page
└── static/
    ├── css/
    │   └── style.css              # Dark theme styles
    └── js/
        └── main.js                # Frontend JavaScript
```

## ⚙️ Configuration

### Flask Settings

In `app.py`:
```python
app.secret_key = os.getenv("SECRET_KEY", "change-this")
```

### Debug Mode

To enable debug mode:
```python
app.run(debug=True)  # Already enabled for development
```

For production:
```python
app.run(debug=False)
```

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'groq'"
- Install dependencies: `pip install -r requirements.txt`
- Verify virtual environment is activated

### "sqlite3.OperationalError: database is locked"
- Close other connections to the database
- Delete `compliance.db` and run `python -c "from database.db import init_db; init_db()"`

### "Groq API errors"
- Verify API key is valid in .env
- Check internet connection
- Validate API key from: https://console.groq.com/
- Application continues with fallback if API fails

### Port 5000 already in use
```bash
# Use different port
python app.py --port 5001
```

## 📚 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Home (redirects) |
| `/login` | GET, POST | User login |
| `/signup` | GET, POST | User registration |
| `/logout` | GET | User logout |
| `/dashboard` | GET | Main dashboard |
| `/validate` | POST | Single transaction validation |
| `/upload_csv` | POST | Batch CSV processing |
| `/download_report` | GET | Export compliance report |

## 🎯 Sample Test Data

### Valid Transactions
```
Email: john@example.com
Amount: $50,000
GST: 18%
→ Result: Compliant ✓
```

### Invalid Transactions
```
Email: invalid-email
Amount: $150,000
GST: 15%
→ Result: Non-Compliant ✗ (3 violations)
```

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production
- Use WSGI server (Gunicorn, uWSGI)
- Set `FLASK_ENV=production`
- Use strong `SECRET_KEY`
- Use HTTPS
- Database backups

### Gunicorn Example
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 📝 Sample CSV Format

**compliance_data.csv**
```csv
Customer Email,Transaction Amount,GST
alice@company.com,45000,12
bob@company.com,250000,18
charlie@company.com,80000,5
diana@company.com,99999,28
eve@company.com,100000,12
```

## 🎨 Customization

### Colors
Edit CSS variables in `static/css/style.css`:
```css
:root {
    --color-primary: #00ff88;      /* Neon green */
    --color-primary-dark: #00cc6f;
    --color-secondary: #00d4ff;     /* Cyan */
    /* ... */
}
```

### Compliance Rules
Edit `services/compliance_rules.py`:
```python
VALID_GST_RATES = [5, 12, 18, 28]  # Modify these
HIGH_RISK_THRESHOLD = 100000       # Change threshold
```

### Risk Scoring
Modify risk calculation in `ComplianceValidator.validate()`:
```python
self.risk_score = min(100, num_violations * 25)  # Adjust multiplier
```

## 📞 Support

For issues:
1. Check `app.py` logs for errors
2. Verify `.env` configuration
3. Check database `compliance.db` exists
4. Clear browser cache and cookies

## 📄 License

This project is provided as-is for educational and professional use.

## 🎓 Learning Outcomes

- Flask web development
- SQLite database management
- User authentication & security
- REST API design
- Frontend form handling
- CSS animations & responsive design
- API integration patterns
- Error handling & fallbacks
- CSV file processing
- Environment configuration best practices

## 💡 Future Enhancements

- [ ] Email verification on signup
- [ ] Two-factor authentication
- [ ] Advanced reporting dashboard
- [ ] Transaction history graphs
- [ ] Real-time WebSocket updates
- [ ] API rate limiting
- [ ] Database encryption
- [ ] Audit logging
- [ ] Admin panel
- [ ] Mobile app

---

**Version**: 1.0.0  
**Last Updated**: 2026-05-01  
**Status**: Production Ready ✓
