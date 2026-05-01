"""
Intelligent Compliance Automation System
A full-stack Flask application for transaction compliance validation,
risk scoring, and AI-powered explanations using Groq API.
"""

import os
import csv
import io
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from database.db import get_connection, init_db
from services.compliance_rules import ComplianceValidator
from services.groq_explainer import GroqComplianceExplainer
from services.csv_processor import CSVProcessor

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-this")

# Initialize database
init_db()

# Initialize services
validator = ComplianceValidator()
explainer = GroqComplianceExplainer()
csv_processor = CSVProcessor()


# ==================== AUTHENTICATION HELPERS ====================

def login_required(f):
    """Decorator to require user login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_user_by_id(user_id):
    """Retrieve user from database by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def user_exists(username, email):
    """Check if user already exists"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
    result = cursor.fetchone()
    conn.close()
    return result is not None


# ==================== ROUTES: AUTHENTICATION ====================

@app.route("/")
def home():
    """Home page with hero section and About details"""
    return render_template('home.html')


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """User signup page"""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        # Validation
        errors = []
        if not username:
            errors.append("Username is required")
        elif len(username) < 3:
            errors.append("Username must be at least 3 characters")
        
        if not email or "@" not in email:
            errors.append("Valid email is required")
        
        if not password:
            errors.append("Password is required")
        elif len(password) < 6:
            errors.append("Password must be at least 6 characters")
        
        if password != confirm_password:
            errors.append("Passwords do not match")
        
        if user_exists(username, email):
            errors.append("Username or email already exists")
        
        if errors:
            return render_template("signup.html", errors=errors)
        
        # Create user
        conn = get_connection()
        cursor = conn.cursor()
        hashed_password = generate_password_hash(password)
        
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, hashed_password)
            )
            conn.commit()
            return redirect(url_for('login') + "?message=Account created successfully. Please login.")
        except Exception as e:
            errors.append(f"Database error: {str(e)}")
            return render_template("signup.html", errors=errors)
        finally:
            conn.close()
    
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login page"""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        if not username or not password:
            return render_template("login.html", error="Username and password are required")
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        
        return render_template("login.html", error="Invalid username or password")
    
    message = request.args.get("message")
    return render_template("login.html", message=message)


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    """Forgot password - password reset"""
    if request.method == "POST":
        action = request.form.get("action")
        email = request.form.get("email", "").strip()
        
        if action == "verify":
            # Step 1: Verify email exists
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            conn.close()
            
            if not user:
                return render_template("forgot_password.html", 
                    error="No account found with this email address")
            
            # Show password reset form
            return render_template("forgot_password.html", 
                show_reset_form=True, 
                email=email)
        
        elif action == "reset":
            # Step 2: Reset password
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")
            
            if not new_password or not confirm_password:
                return render_template("forgot_password.html", 
                    show_reset_form=True,
                    email=email,
                    error="Password fields cannot be empty")
            
            if new_password != confirm_password:
                return render_template("forgot_password.html", 
                    show_reset_form=True,
                    email=email,
                    error="Passwords do not match")
            
            if len(new_password) < 6:
                return render_template("forgot_password.html", 
                    show_reset_form=True,
                    email=email,
                    error="Password must be at least 6 characters")
            
            # Update password in database
            conn = get_connection()
            cursor = conn.cursor()
            hashed_password = generate_password_hash(new_password)
            cursor.execute(
                "UPDATE users SET password = ? WHERE email = ?",
                (hashed_password, email)
            )
            conn.commit()
            conn.close()
            
            return redirect(url_for('login') + "?message=Password reset successful. Please login with your new password.")
    
    return render_template("forgot_password.html")


@app.route("/logout")
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('login'))


# ==================== ROUTES: MAIN APPLICATION ====================

@app.route("/dashboard")
@login_required
def dashboard():
    """Main dashboard page"""
    user = get_user_by_id(session['user_id'])
    
    # Get recent transactions
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM transactions 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 10
    """, (session['user_id'],))
    transactions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # Calculate statistics
    compliant_count = sum(1 for t in transactions if t['is_compliant'])
    high_risk_count = sum(1 for t in transactions if t['risk_level'] == 'High')
    
    stats = {
        'total_transactions': len(transactions),
        'compliant': compliant_count,
        'non_compliant': len(transactions) - compliant_count,
        'high_risk': high_risk_count
    }
    
    return render_template("dashboard.html", user=user, transactions=transactions, stats=stats)


@app.route("/validate", methods=["POST"])
@login_required
def validate():
    """
    API endpoint to validate a single transaction
    Supports both form data and JSON
    """
    try:
        if request.is_json:
            data = request.get_json()
            email = data.get('email', '').strip()
            amount = data.get('amount', '')
            gst = data.get('gst', '')
        else:
            email = request.form.get('email', '').strip()
            amount = request.form.get('amount', '')
            gst = request.form.get('gst', '')
        
        # Validate
        is_compliant, violations, risk_score = validator.validate(email, amount, gst)
        risk_level = validator.get_risk_level(risk_score)
        
        # Get AI explanation
        explanation, used_ai = explainer.generate_explanation(violations, risk_score)
        
        # Store in database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions 
            (user_id, customer_email, amount, gst, is_compliant, risk_level, risk_score, violations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session['user_id'],
            email,
            float(amount) if amount else 0,
            float(gst) if gst else 0,
            is_compliant,
            risk_level,
            risk_score,
            "; ".join(violations) if violations else ""
        ))
        conn.commit()
        transaction_id = cursor.lastrowid
        conn.close()
        
        # Return response
        return jsonify({
            'success': True,
            'transaction_id': transaction_id,
            'email': email,
            'amount': float(amount) if amount else 0,
            'gst': float(gst) if gst else 0,
            'is_compliant': is_compliant,
            'status': validator.get_compliance_status(is_compliant),
            'violations': violations,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'explanation': explanation,
            'ai_used': used_ai
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route("/upload_csv", methods=["POST"])
@login_required
def upload_csv():
    """
    Handle CSV file upload
    Validate multiple transactions at once
    """
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'success': False, 'error': 'Please upload a CSV file'}), 400
        
        # Process CSV
        results, error = csv_processor.process_csv(file.stream)
        
        if error:
            return jsonify({'success': False, 'error': error}), 400
        
        # Store results in database
        conn = get_connection()
        cursor = conn.cursor()
        
        for result in results:
            cursor.execute("""
                INSERT INTO transactions 
                (user_id, customer_email, amount, gst, is_compliant, risk_level, risk_score, violations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session['user_id'],
                result['email'],
                result['amount'],
                result['gst'],
                result['is_compliant'],
                result['risk_level'],
                result['risk_score'],
                "; ".join(result['violations']) if result['violations'] else ""
            ))
        
        conn.commit()
        conn.close()
        
        # Summary statistics
        compliant = sum(1 for r in results if r['is_compliant'])
        high_risk = sum(1 for r in results if r['risk_level'] == 'High')
        
        return jsonify({
            'success': True,
            'message': f"Processed {len(results)} records",
            'total_records': len(results),
            'compliant': compliant,
            'non_compliant': len(results) - compliant,
            'high_risk': high_risk,
            'results': results[:50]  # Return first 50 for preview
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route("/download_report")
@login_required
def download_report():
    """Download compliance report as CSV"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM transactions 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (session['user_id'],))
        transactions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Generate CSV
        output = io.StringIO()
        fieldnames = ['Date', 'Email', 'Amount', 'GST (%)', 'Status', 'Risk Level', 'Violations']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for t in transactions:
            writer.writerow({
                'Date': t['created_at'],
                'Email': t['customer_email'],
                'Amount': f"${t['amount']:,.2f}",
                'GST (%)': t['gst'],
                'Status': 'Compliant ✓' if t['is_compliant'] else 'Non-Compliant ✗',
                'Risk Level': t['risk_level'],
                'Violations': t['violations'] if t['violations'] else 'None'
            })
        
        # Create file
        mem = io.BytesIO()
        mem.write(output.getvalue().encode('utf-8'))
        mem.seek(0)
        
        return send_file(
            mem,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template("error.html", message="Page not found"), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return render_template("error.html", message="Server error"), 500


# ==================== RUN APPLICATION ====================

if __name__ == "__main__":
    app.run(debug=True)