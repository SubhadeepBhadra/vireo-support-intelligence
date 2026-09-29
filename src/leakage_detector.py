"""
Leakage Detector and Policy Compliance Auditor
Identifies duplicate refund + replacement violations, unauthorized goodwill payouts, and misrouted transfers.
"""

import pandas as pd
import numpy as np

def audit_policy_compliance(data):
    tickets = data['tickets']
    orders = data['orders']
    products = data['products']
    
    # 1. Double Dipping: Customer received BOTH refund and replacement for the same order
    # Join orders with products to get unit_cost_inr and product_name
    orders_enriched = orders.merge(products[['sku', 'product_name', 'unit_cost_inr', 'retail_price_inr']], on='sku', how='left')
    
    # Aggregate tickets by order_id
    ticket_order_summary = tickets.groupby('order_id').agg(
        ticket_ids=('ticket_id', lambda x: list(x)),
        total_refund=('refund_amount_inr', 'sum'),
        has_replacement=('replacement_issued', lambda x: (x == 'Y').any()),
        agents=('agent_id', lambda x: list(x.dropna())),
        categories=('category', lambda x: list(x.dropna()))
    ).reset_index()
    
    double_dipping_orders = ticket_order_summary[
        (ticket_order_summary['total_refund'] > 0) & 
        (ticket_order_summary['has_replacement'] == True)
    ].copy()
    
    double_dipping_orders = double_dipping_orders.merge(orders_enriched, on='order_id', how='left')
    double_dipping_orders['replacement_logistics_cost'] = 340.0
    double_dipping_orders['replacement_total_cost'] = double_dipping_orders['unit_cost_inr'] + double_dipping_orders['replacement_logistics_cost']
    double_dipping_orders['total_leakage_inr'] = double_dipping_orders['total_refund'] + double_dipping_orders['replacement_total_cost']
    
    # 2. Goodwill Cap Violations (Policy §5: GW-OTHER capped at Rs 500)
    gw_tickets = tickets[tickets['refund_reason_code'] == 'GW-OTHER'].copy()
    gw_violations = gw_tickets[gw_tickets['refund_amount_inr'] > 500.0].copy()
    gw_violations['excess_amount_inr'] = gw_violations['refund_amount_inr'] - 500.0
    
    # 3. Internal Transfers & Misrouting Costs (Policy §4: Rs 305 per transfer)
    transfer_tickets = tickets[tickets['transfers'] > 0].copy()
    total_transfers = tickets['transfers'].sum()
    total_transfer_cost = total_transfers * 305.0
    
    # Category transfer rates
    category_transfers = tickets.groupby('category').agg(
        total_tickets=('ticket_id', 'count'),
        transfers=('transfers', 'sum'),
        avg_transfers=('transfers', 'mean')
    ).sort_values(by='transfers', ascending=False).reset_index()
    
    # 4. FCR & Repeat Contact Cost
    tickets_sorted = tickets.sort_values(by=['customer_id', 'created_at_dt']).copy()
    tickets_sorted['prev_resolved_at'] = tickets_sorted.groupby('customer_id')['resolved_at_dt'].shift(1)
    tickets_sorted['prev_category'] = tickets_sorted.groupby('customer_id')['category'].shift(1)
    tickets_sorted['days_since_prev_resolve'] = (tickets_sorted['created_at_dt'] - tickets_sorted['prev_resolved_at']).dt.total_seconds() / (24 * 3600)
    
    channel_costs = {'chat': 210, 'email': 260, 'voice': 520, 'social': 240}
    tickets_sorted['channel_cost'] = tickets_sorted['channel'].map(channel_costs)
    repeat_contacts = tickets_sorted[
        (tickets_sorted['days_since_prev_resolve'] >= 0) & 
        (tickets_sorted['days_since_prev_resolve'] <= 30) & 
        (tickets_sorted['category'] == tickets_sorted['prev_category'])
    ].copy()
    
    return {
        'double_dipping': {
            'count': len(double_dipping_orders),
            'total_refund_inr': float(double_dipping_orders['total_refund'].sum()),
            'total_replacement_cost_inr': float(double_dipping_orders['replacement_total_cost'].sum()),
            'total_leakage_inr': float(double_dipping_orders['total_leakage_inr'].sum()),
            'orders_df': double_dipping_orders
        },
        'goodwill_violations': {
            'count': len(gw_violations),
            'total_excess_inr': float(gw_violations['excess_amount_inr'].sum()),
            'violations_df': gw_violations
        },
        'transfers': {
            'total_transfers': int(total_transfers),
            'total_cost_inr': float(total_transfer_cost),
            'category_breakdown': category_transfers
        },
        'repeat_contacts': {
            'count': len(repeat_contacts),
            'total_cost_inr': float(repeat_contacts['channel_cost'].sum()),
            'df': repeat_contacts
        }
    }
