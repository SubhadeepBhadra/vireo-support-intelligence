"""
Vireo Support Intelligence - Command Line Interface (CLI) & Launcher
Runs audits, evaluates models, triages individual tickets, exports leakages, or launches the web dashboard.
"""

import argparse
import sys
import os
import subprocess
import webbrowser
import socket
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, os.path.join(script_dir, 'src'))

from data_loader import load_and_preprocess_data
from sla_engine import calculate_sla_metrics, generate_breach_summary
from leakage_detector import audit_policy_compliance
from classifier import TicketClassifier
from responder import ResponseGenerator

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port=8501, max_tries=10):
    for p in range(start_port, start_port + max_tries):
        if not is_port_in_use(p):
            return p
    return start_port

def launch_dashboard(port=8501):
    if is_port_in_use(port):
        url = f"http://localhost:{port}"
        print(f"\n✅ Streamlit server is already actively running on {url}!")
        print(f"🌐 Opening dashboard in browser: {url}\n")
        webbrowser.open(url)
        return

    port = find_available_port(port)
    url = f"http://localhost:{port}"
    app_path = os.path.join(script_dir, "app.py")
    print(f"⚡ Starting Streamlit Web Dashboard on {url}...")
    
    def open_browser():
        time.sleep(1.5)
        print(f"🌐 Opening browser: {url}")
        webbrowser.open(url)
        
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    cmd = [
        sys.executable, "-m", "streamlit", "run", app_path,
        "--server.port", str(port),
        "--server.headless", "false"
    ]
    try:
        subprocess.run(cmd, cwd=script_dir)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped.")

def main():
    parser = argparse.ArgumentParser(description="Vireo Support Intelligence Tool")
    parser.add_argument('--dashboard', action='store_true', help="Launch the interactive Web Dashboard and open browser")
    parser.add_argument('--audit', action='store_true', help="Run full SLA and policy compliance audit in terminal")
    parser.add_argument('--triage', type=str, help="Triage and draft response for a customer message text")
    parser.add_argument('--evaluate', action='store_true', help="Run ML benchmark on ticket dataset")
    parser.add_argument('--export-leakages', type=str, help="Export double-dipping leakage list to CSV file")
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        print("No arguments provided. Launching web dashboard by default...")
        launch_dashboard()
        return

    if args.dashboard:
        launch_dashboard()
        return
        
    data = load_and_preprocess_data()
    tickets_sla = calculate_sla_metrics(data['tickets'])
    data['tickets_sla'] = tickets_sla
    
    if args.audit:
        print("=== VIREO AUDIT & SLA ATTRIBUTION SUMMARY ===")
        summary, channel_sum, _ = generate_breach_summary(tickets_sla)
        audit = audit_policy_compliance(data)
        
        print(f"Total Unique Tickets: {summary['total_tickets']:,}")
        print(f"Reported Helpdesk Breaches: {summary['total_breaches']:,} ({summary['overall_breach_rate']*100:.1f}%) | SLA Penalty Charged: Rs {summary['sla_credits_inr']:,.2f}")
        print(f"Unjust Morning Attributed Breaches (Night Backlog): {summary['unjust_morning_breaches']:,} ({summary['unjust_morning_breaches']/summary['total_breaches']*100:.1f}%)")
        print(f"True In-Shift Breaches: {summary['fair_breaches']:,} ({summary['fair_breach_rate']*100:.1f}%)")
        print(f"Double-Dipping Leakage (Refund + Replacement): {audit['double_dipping']['count']} orders | Rs {audit['double_dipping']['total_leakage_inr']:,.2f}")
        print(f"Unauthorized Goodwill Refunds (>Rs 500): {audit['goodwill_violations']['count']} cases | Rs {audit['goodwill_violations']['total_excess_inr']:,.2f}")
        print(f"Internal Transfer Waste (1,129 transfers): Rs {audit['transfers']['total_cost_inr']:,.2f}")
        
    if args.evaluate:
        clf = TicketClassifier()
        res = clf.train(tickets_sla)
        print(f"Classifier Accuracy: {res['accuracy']*100:.2f}% (Test Sample: {res['test_size']:,})")
        
    if args.triage:
        clf = TicketClassifier()
        clf.train(tickets_sla)
        gen = ResponseGenerator()
        pred = clf.predict(args.triage)
        draft = gen.generate_draft(args.triage, pred['category'])
        
        print("\n=== TRIAGE RESULT ===")
        print(f"Predicted Category: {pred['category']}")
        print(f"Routing Destination: {pred['team']}")
        print(f"Confidence: {pred['confidence']*100:.1f}%")
        print("\n=== DRAFT RESPONSE ===")
        print(draft['draft_response'])
        if draft['policy_warnings']:
            print("\n=== POLICY WARNINGS ===")
            for w in draft['policy_warnings']:
                print(f"  [!] {w}")
                
    if args.export_leakages:
        audit = audit_policy_compliance(data)
        audit['double_dipping']['orders_df'].to_csv(args.export_leakages, index=False)
        print(f"Exported {len(audit['double_dipping']['orders_df'])} double-dipping records to {args.export_leakages}")

if __name__ == '__main__':
    main()
