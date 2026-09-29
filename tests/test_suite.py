"""
Unit and Integration Test Suite for Vireo Support Intelligence
"""

import unittest
import os
import sys
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from data_loader import load_and_preprocess_data
from sla_engine import calculate_sla_metrics, generate_breach_summary
from leakage_detector import audit_policy_compliance
from classifier import TicketClassifier
from responder import ResponseGenerator

class TestVireoSupportIntelligence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_and_preprocess_data()
        cls.tickets = cls.data['tickets']
        
    def test_deduplication(self):
        # Ensure duplicate ticket IDs are properly resolved
        self.assertEqual(self.tickets['ticket_id'].duplicated().sum(), 0)
        self.assertEqual(len(self.tickets), 11200)

    def test_csat_cleaning(self):
        # 0s must be converted to NaN
        self.assertFalse((self.tickets['csat_clean'] == 0).any())
        self.assertTrue(self.tickets['csat_clean'].dropna().between(1, 5).all())

    def test_sla_targets(self):
        # Verify correct SLA target assignment
        chat_sla = self.tickets[self.tickets['channel'] == 'chat']['sla_target_mins'].iloc[0]
        voice_sla = self.tickets[self.tickets['channel'] == 'voice']['sla_target_mins'].iloc[0]
        social_sla = self.tickets[self.tickets['channel'] == 'social']['sla_target_mins'].iloc[0]
        email_sla = self.tickets[self.tickets['channel'] == 'email']['sla_target_mins'].iloc[0]
        
        self.assertEqual(chat_sla, 15)
        self.assertEqual(voice_sla, 120)
        self.assertEqual(social_sla, 240)
        self.assertEqual(email_sla, 480)

    def test_sla_engine_calculation(self):
        tickets_with_sla = calculate_sla_metrics(self.tickets)
        summary, _, _ = generate_breach_summary(tickets_with_sla)
        self.assertEqual(summary['total_breaches'], 2440)
        self.assertGreater(summary['unjust_morning_breaches'], 1500)

    def test_leakage_detector(self):
        audit = audit_policy_compliance(self.data)
        self.assertEqual(audit['double_dipping']['count'], 95)
        self.assertAlmostEqual(audit['double_dipping']['total_leakage_inr'], 437418.0, places=1)
        self.assertEqual(audit['goodwill_violations']['count'], 45)

    def test_classifier_prediction(self):
        clf = TicketClassifier()
        clf.train(self.tickets)
        pred = clf.predict("pairing is not working with my phone, bluetooth disconnects")
        self.assertEqual(pred['category'], 'Connectivity')
        self.assertGreater(pred['confidence'], 0.5)

    def test_response_generator(self):
        gen = ResponseGenerator()
        res = gen.generate_draft("I want a refund and also send me a replacement immediately", "Returns & Refunds")
        self.assertIn("Hello", res['draft_response'])
        self.assertGreater(len(res['policy_warnings']), 0)
        self.assertTrue(any("double-dipping" in w.lower() or "dual resolution" in w.lower() for w in res['policy_warnings']))

if __name__ == '__main__':
    unittest.main()
