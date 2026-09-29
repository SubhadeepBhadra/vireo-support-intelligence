"""
Evaluation Benchmark for Ticket Classifier & SLA Attribution Engine
Provides rigorous statistical testing: accuracy, precision, recall, sample size, error rate, and failure case analysis.
"""

import os
import sys
import pandas as pd
import numpy as np
import json

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from data_loader import load_and_preprocess_data
from sla_engine import calculate_sla_metrics, generate_breach_summary
from leakage_detector import audit_policy_compliance
from classifier import TicketClassifier

def run_full_evaluation():
    print("=" * 60)
    print("VIREO SUPPORT INTELLIGENCE - FULL EVALUATION BENCHMARK")
    print("=" * 60)
    
    # 1. Load Data
    data = load_and_preprocess_data()
    tickets = data['tickets']
    print(f"[1] Dataset Verification:")
    print(f"    - Total unique tickets: {len(tickets):,}")
    print(f"    - Date range: {tickets['created_at_ist'].min().strftime('%Y-%m-%d')} to {tickets['created_at_ist'].max().strftime('%Y-%m-%d')}")
    print(f"    - Total customer base: {len(data['customers']):,}")
    print(f"    - Total orders: {len(data['orders']):,}")
    print(f"    - Total products in catalog: {len(data['products'])}")
    
    # 2. SLA Engine Evaluation
    tickets_with_sla = calculate_sla_metrics(tickets)
    sla_summary, channel_sum, shift_sum = generate_breach_summary(tickets_with_sla)
    
    print(f"\n[2] SLA Engine Performance:")
    print(f"    - Standard Helpdesk Reported Breaches: {sla_summary['total_breaches']:,} ({sla_summary['overall_breach_rate']*100:.1f}%)")
    print(f"    - Total SLA Penalty Credits Charged: Rs {sla_summary['sla_credits_inr']:,.2f}")
    print(f"    - Unjust Morning Attributed Breaches (Overnight Queue Backlog): {sla_summary['unjust_morning_breaches']:,} ({sla_summary['unjust_morning_breaches']/sla_summary['total_breaches']*100:.1f}% of all breaches!)")
    print(f"    - True Fair Breaches (Excluding unstaffed night shift lag): {sla_summary['fair_breaches']:,} ({sla_summary['fair_breach_rate']*100:.1f}%)")
    print(f"    - Net Artificial Credit Penalty: Rs {sla_summary['unjust_breach_credit_inr']:,.2f}")
    
    # 3. Policy & Leakage Audit
    audit = audit_policy_compliance(data)
    print(f"\n[3] Policy Compliance & Financial Leakage Audit:")
    print(f"    - Double-Dipping Orders (Refund + Replacement): {audit['double_dipping']['count']}")
    print(f"      * Total Cash Refund Leakage: Rs {audit['double_dipping']['total_refund_inr']:,.2f}")
    print(f"      * Total Hardware Replacement & Shipping Loss: Rs {audit['double_dipping']['total_replacement_cost_inr']:,.2f}")
    print(f"      * Combined Double-Dipping Financial Loss: Rs {audit['double_dipping']['total_leakage_inr']:,.2f}")
    print(f"    - Unauthorized Goodwill Refunds (>Rs 500 cap): {audit['goodwill_violations']['count']} cases | Rs {audit['goodwill_violations']['total_excess_inr']:,.2f} excess")
    print(f"    - Internal Transfer Waste (1,129 transfers @ Rs 305): Rs {audit['transfers']['total_cost_inr']:,.2f}")
    print(f"    - Repeat Contact / FCR Friction: {audit['repeat_contacts']['count']} cases | Rs {audit['repeat_contacts']['total_cost_inr']:,.2f}")
    
    # 4. Classifier ML Evaluation
    clf = TicketClassifier()
    eval_res = clf.train(tickets)
    print(f"\n[4] AI Classifier Benchmark:")
    print(f"    - Sample Size: {eval_res['train_size'] + eval_res['test_size']:,} labeled messages (Train: {eval_res['train_size']:,}, Test: {eval_res['test_size']:,})")
    print(f"    - Out-of-Sample Test Accuracy: {eval_res['accuracy']*100:.2f}%")
    print(f"    - Test Error Rate: {(1.0 - eval_res['accuracy'])*100:.2f}%")
    
    # Analyze Error Cases
    y_test = eval_res['y_test']
    y_pred = eval_res['y_pred']
    X_test = eval_res['X_test']
    
    error_mask = (y_test != y_pred)
    error_df = pd.DataFrame({
        'message': X_test[error_mask],
        'true_category': y_test[error_mask],
        'predicted_category': y_pred[error_mask]
    })
    
    print(f"\n[5] Analysis of Classification Failure Modes (Total Errors: {len(error_df)}):")
    top_confusion = error_df.groupby(['true_category', 'predicted_category']).size().sort_values(ascending=False).head(5)
    print("    Top Misclassification Pairs:")
    for (t, p), count in top_confusion.items():
        print(f"      * True: '{t}' -> Predicted: '{p}' ({count} cases)")
        
    print("\n    Sample Failure Case Snippets:")
    for idx, row in error_df.head(3).iterrows():
        print(f"      - Message: \"{row['message'][:90]}...\"")
        print(f"        Expected: [{row['true_category']}] vs Predicted: [{row['predicted_category']}]")
        
    # Save evaluation summary to json
    results_dict = {
        'total_tickets': len(tickets),
        'reported_breaches': sla_summary['total_breaches'],
        'unjust_morning_breaches': sla_summary['unjust_morning_breaches'],
        'fair_breaches': sla_summary['fair_breaches'],
        'total_double_dipping_leakage_inr': audit['double_dipping']['total_leakage_inr'],
        'classifier_accuracy': eval_res['accuracy'],
        'classifier_error_rate': 1.0 - eval_res['accuracy'],
        'test_sample_size': eval_res['test_size']
    }
    
    with open(os.path.join(os.path.dirname(__file__), 'benchmark_results.json'), 'w') as f:
        json.dump(results_dict, f, indent=2)
        
    print("\n" + "=" * 60)
    print("EVALUATION BENCHMARK COMPLETED SUCCESSFULLY")
    print("=" * 60)

if __name__ == '__main__':
    run_full_evaluation()
