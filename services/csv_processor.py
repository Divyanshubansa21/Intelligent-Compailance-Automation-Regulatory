"""
CSV Processing service
Handles CSV file upload, validation, and report generation
"""

import csv
import io
from services.compliance_rules import ComplianceValidator

class CSVProcessor:
    """Process CSV files for compliance validation"""
    
    def process_csv(self, file_stream):
        """
        Process CSV file and validate each row
        Returns list of validation results
        """
        try:
            # Read CSV file
            if isinstance(file_stream, bytes):
                file_stream = io.StringIO(file_stream.decode('utf-8'))
            elif hasattr(file_stream, 'stream'):
                file_stream = io.StringIO(file_stream.read().decode('utf-8'))
            
            reader = csv.DictReader(file_stream)
            
            if reader.fieldnames is None:
                return None, "Invalid CSV format"
            
            required_fields = {'Customer Email', 'Transaction Amount', 'GST'}
            missing_fields = required_fields - set(reader.fieldnames)
            
            if missing_fields:
                return None, f"Missing required columns: {', '.join(missing_fields)}"
            
            results = []
            validator = ComplianceValidator()
            
            for row_num, row in enumerate(reader, start=2):  # Start from 2 (after header)
                try:
                    email = row['Customer Email'].strip()
                    amount = row['Transaction Amount'].strip()
                    gst = row['GST'].strip()
                    
                    is_compliant, violations, risk_score = validator.validate(email, amount, gst)
                    risk_level = validator.get_risk_level(risk_score)
                    
                    results.append({
                        'row': row_num,
                        'email': email,
                        'amount': float(amount) if amount else 0,
                        'gst': float(gst) if gst else 0,
                        'is_compliant': is_compliant,
                        'violations': violations,
                        'risk_score': risk_score,
                        'risk_level': risk_level,
                        'status': validator.get_compliance_status(is_compliant)
                    })
                except Exception as e:
                    results.append({
                        'row': row_num,
                        'email': row.get('Customer Email', 'N/A'),
                        'amount': 'Invalid',
                        'gst': 'Invalid',
                        'is_compliant': False,
                        'violations': [f"Row error: {str(e)}"],
                        'risk_score': 100,
                        'risk_level': 'High',
                        'status': '✗ Non-Compliant'
                    })
            
            return results, None
        
        except Exception as e:
            return None, f"Error processing CSV: {str(e)}"
    
    @staticmethod
    def generate_csv_report(validation_results):
        """Generate CSV report from validation results"""
        if not validation_results:
            return None
        
        output = io.StringIO()
        fieldnames = ['Row', 'Email', 'Amount', 'GST (%)', 'Status', 'Risk Level', 'Violations']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for result in validation_results:
            violations_text = '; '.join(result['violations']) if result['violations'] else 'None'
            writer.writerow({
                'Row': result['row'],
                'Email': result['email'],
                'Amount': f"${result['amount']:,.2f}" if isinstance(result['amount'], (int, float)) else result['amount'],
                'GST (%)': result['gst'] if isinstance(result['gst'], (int, float)) else result['gst'],
                'Status': result['status'],
                'Risk Level': result['risk_level'],
                'Violations': violations_text
            })
        
        return output.getvalue()
