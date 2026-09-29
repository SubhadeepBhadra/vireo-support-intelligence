"""
AI-Assisted Response Generator & Policy Safeguard Engine
Generates compliant, context-aware first responses to clear support queues instantly while preventing policy violations.
"""

import re

RESPONSE_TEMPLATES = {
    'Delivery & Shipping': (
        "Hello {name},\n\n"
        "Thank you for contacting Vireo Audio Support. I understand you're inquiring about your shipment (Order #{order_id}). "
        "I have checked our logistics tracking system, and our delivery team is actively coordinating with the courier partner. "
        "We will provide a live tracking update within the next 2 hours.\n\n"
        "Best regards,\n{agent_name}\nVireo Support Team"
    ),
    'Returns & Refunds': (
        "Hello {name},\n\n"
        "Thank you for reaching out regarding your return/refund for Order #{order_id}. "
        "Under Vireo's support policy, return pickups are completed within 24-48 hours, and refunds are processed to your original payment method immediately upon passing QC inspection. "
        "I am routing your request directly to our Returns Desk to expedite this for you.\n\n"
        "Best regards,\n{agent_name}\nVireo Support Team"
    ),
    'Charging & Battery': (
        "Hello {name},\n\n"
        "Thank you for contacting Vireo Audio Support. I am sorry to hear you're experiencing charging issues with your {product_name}. "
        "Let's try a quick reset: please place both earbuds in the charging case, ensure the charging pins are clean, and connect the case to a 5V/1A power source for 30 minutes. "
        "If the LED indicator still does not respond, our Tier 2 Warranty team will immediately arrange a certified inspection and replacement under your 1-year warranty.\n\n"
        "Best regards,\n{agent_name}\nVireo Support Team"
    ),
    'Connectivity': (
        "Hello {name},\n\n"
        "Thank you for reaching out to Vireo Support. Let's get your {product_name} connected. "
        "Please turn off Bluetooth on all nearby devices, press and hold the button on your device for 10 seconds to enter pairing mode (rapid blinking LED), and select '{product_name}' in your phone's Bluetooth menu. "
        "Please let me know if it pairs successfully.\n\n"
        "Best regards,\n{agent_name}\nVireo Support Team"
    ),
    'Billing & Payments': (
        "Hello {name},\n\n"
        "Thank you for contacting Vireo Support. I understand you have a query regarding billing for Order #{order_id}. "
        "I have flagged this with our Billing & Finance desk to verify the transaction details with our payment gateway. "
        "Any duplicate or erroneous deductions will be automatically reversed to your source account within 3-5 business days.\n\n"
        "Best regards,\n{agent_name}\nVireo Support Team"
    ),
    'Warranty & Repair': (
        "Hello {name},\n\n"
        "Thank you for contacting Vireo Audio. Your {product_name} is covered under our official manufacturer warranty. "
        "I have initiated a warranty validation ticket for our Tier 2 Escalations & Warranty specialists. "
        "Please share a brief 5-second video or photo showing the fault so our certified team can authorize a doorstep replacement.\n\n"
        "Best regards,\n{agent_name}\nVireo Support Team"
    ),
    'Default': (
        "Hello {name},\n\n"
        "Thank you for contacting Vireo Audio Support. I have received your message regarding {product_name} and our team is actively reviewing your request. "
        "We are committed to resolving this promptly. A specialist from our team will follow up shortly with resolution details.\n\n"
        "Best regards,\n{agent_name}\nVireo Support Team"
    )
}

class ResponseGenerator:
    def __init__(self):
        pass

    def generate_draft(self, customer_message, category, customer_name="Customer", order_id="N/A", product_name="Vireo Product", agent_name="Support Team"):
        template = RESPONSE_TEMPLATES.get(category, RESPONSE_TEMPLATES['Default'])
        response = template.format(
            name=customer_name or "Customer",
            order_id=order_id or "N/A",
            product_name=product_name or "Vireo Product",
            agent_name=agent_name or "Support Team"
        )
        
        # Policy Guardrail Warnings
        policy_warnings = []
        c_lower = customer_message.lower()
        if 'refund' in c_lower and 'replace' in c_lower:
            policy_warnings.append("POLICY ALERT (§5): Customer mentions both refund and replacement. Dual resolution (double-dipping) is strictly prohibited. Escalate to TL if both requested.")
        if 'goodwill' in c_lower or 'compensation' in c_lower:
            policy_warnings.append("POLICY ALERT (§5): Goodwill credits are strictly capped at Rs 500 per ticket and require Team Lead approval.")
            
        return {
            'draft_response': response,
            'policy_warnings': policy_warnings,
            'sla_target_guidance': "Aim to send initial response within SLA (Chat: 15m, Voice: 2h, Social: 4h, Email: 8h)."
        }
