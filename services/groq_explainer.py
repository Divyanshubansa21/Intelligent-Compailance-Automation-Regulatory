"""
Groq API Integration for AI explanations
Provides human-readable explanations of compliance violations
"""

import os
from groq import Groq
import logging

logger = logging.getLogger(__name__)

class GroqComplianceExplainer:
    """Uses Groq API to generate explanations for compliance violations"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "mixtral-8x7b-32768"
        self.api_ready = self.client is not None
        if not self.api_ready:
            logger.warning("Groq API key is not configured. AI explanations will use fallback text.")
    
    def generate_explanation(self, violations, risk_score):
        """
        Generate AI-powered explanation for compliance violations.
        Returns a tuple (explanation_text, used_ai).
        """
        if not violations:
            return "All compliance checks passed. ✓", False
        
        if not self.api_ready:
            return self._fallback_explanation(violations, risk_score), False
        
        prompt = self._create_prompt(violations, risk_score)
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                max_tokens=280,
                temperature=0.25,
                top_p=0.95
            )

            explanation = self._extract_response_text(response)
            if not explanation:
                raise ValueError("Empty AI response")
            return explanation, True
        except Exception as exc:
            logger.error(f"Groq API error: {exc}. Falling back to rule-based explanation.")
            return self._fallback_explanation(violations, risk_score), False
    
    def _extract_response_text(self, response):
        """Extract readable text from Groq response"""
        if not response or not hasattr(response, 'choices'):
            return ""
        
        choice = response.choices[0]
        if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
            return choice.message.content.strip()
        if hasattr(choice, 'content'):
            return choice.content.strip()
        if isinstance(choice, dict):
            return (choice.get('message', {}).get('content') or choice.get('content') or "").strip()
        return ""
    
    def _create_prompt(self, violations, risk_score):
        """Create a prompt for Groq API"""
        violations_text = "\n".join([f"- {v}" for v in violations])
        
        prompt = (
            "You are a compliance expert working for a financial regulation team. "
            "Review the compliance violations below and provide a concise, professional summary. "
            "Explain the likely operational impact, the risk level, and the next corrective action in plain business language. "
            "Use no numbered list and keep the response under 3 sentences.\n\n"
            "Violations:\n"
            f"{violations_text}\n\n"
            f"Risk Score: {risk_score}/100\n\n"
            "If all checks are compliant, respond with a positive confirmation message."
        )
        
        return prompt
    
    def _fallback_explanation(self, violations, risk_score):
        """Provide rule-based explanation when API is unavailable"""
        num_violations = len(violations)
        risk_label = 'HIGH' if risk_score > 50 else 'MEDIUM' if risk_score > 0 else 'LOW'
        
        explanation = (
            f"Compliance issues detected ({num_violations} violation{'s' if num_violations != 1 else ''}). "
            f"Risk level is {risk_label} with a score of {risk_score}/100. "
            "Review the following issues and correct them before proceeding: "
            + "; ".join(violations)
        )
        
        return explanation

