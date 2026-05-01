"""
Compliance Rule Engine
Validates transactions against compliance rules
"""

class ComplianceValidator:
    """Validates transactions against compliance rules"""
    
    VALID_GST_RATES = [5, 12, 18, 28]
    HIGH_RISK_THRESHOLD = 100000
    
    def __init__(self):
        self.violations = []
        self.risk_score = 0
    
    def validate_email(self, email):
        """Check if email contains @ symbol"""
        if "@" not in email:
            self.violations.append("Invalid email format (must contain @)")
            return False
        return True
    
    def validate_amount(self, amount):
        """Check if transaction amount is high risk"""
        try:
            amount = float(amount)
            if amount > self.HIGH_RISK_THRESHOLD:
                self.violations.append(f"High transaction amount: ${amount:,.2f} (exceeds ${self.HIGH_RISK_THRESHOLD:,})")
                return False
        except (ValueError, TypeError):
            self.violations.append("Invalid transaction amount")
            return False
        return True
    
    def validate_gst(self, gst):
        """Check if GST rate is valid"""
        try:
            gst = float(gst)
            if gst not in self.VALID_GST_RATES:
                valid_rates = ", ".join(str(x) for x in self.VALID_GST_RATES)
                self.violations.append(f"Invalid GST rate: {gst}% (must be one of: {valid_rates})")
                return False
        except (ValueError, TypeError):
            self.violations.append("Invalid GST format")
            return False
        return True
    
    def validate(self, customer_email, transaction_amount, gst):
        """
        Validate a transaction against all compliance rules
        Returns: (is_compliant, violations_list, risk_score)
        """
        self.violations = []
        self.risk_score = 0
        
        # Validate each field
        email_valid = self.validate_email(customer_email)
        amount_valid = self.validate_amount(transaction_amount)
        gst_valid = self.validate_gst(gst)
        
        # Calculate risk score based on violations
        # Each violation adds points: 25 points per violation
        num_violations = len(self.violations)
        self.risk_score = min(100, num_violations * 25)
        
        is_compliant = (email_valid and amount_valid and gst_valid)
        
        return is_compliant, self.violations, self.risk_score
    
    def get_risk_level(self, risk_score):
        """Determine risk level from score"""
        if risk_score == 0:
            return "Low"
        elif risk_score <= 50:
            return "Medium"
        else:
            return "High"
    
    def get_compliance_status(self, is_compliant):
        """Return compliance status string"""
        return "✓ Compliant" if is_compliant else "✗ Non-Compliant"
