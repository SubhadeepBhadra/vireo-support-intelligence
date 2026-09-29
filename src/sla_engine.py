"""
SLA Engine & Breach Attribution Analysis
Decomposes SLA breaches into queue arrival backlog (unstaffed night shift) vs true agent handle time.
"""

import pandas as pd
import numpy as np

def calculate_sla_metrics(tickets_df):
    """
    Computes standard vs fair SLA breach metrics.
    """
    df = tickets_df.copy()
    
    # 1. Standard Breach (as reported by helpdesk API)
    # Target: Chat 15m, Voice 120m, Social 240m, Email 480m
    
    # 2. Queue Wait vs In-Shift Response Time
    # If a ticket arrived during Night Shift (22:00 to 06:00 IST) and was answered in Morning Shift (06:00 to 14:00 IST):
    # The queue wait time prior to shift start (06:00 IST) is system latency due to unstaffed night shift.
    
    def compute_fair_handle_time(row):
        creation_ist = row['created_at_ist']
        resp_ist = row['first_response_at_ist']
        if pd.isnull(creation_ist) or pd.isnull(resp_ist):
            return np.nan, False
            
        creation_shift = row['creation_shift']
        resp_shift = row['response_shift']
        
        # If created during night (22:00 - 06:00) and responded in morning:
        if creation_shift == 'Night' and resp_shift == 'Morning':
            # Morning shift starts at 06:00 AM on the response date (or creation date + 1)
            shift_start = resp_ist.replace(hour=6, minute=0, second=0, microsecond=0)
            if resp_ist >= shift_start:
                in_shift_response_mins = max(0.0, (resp_ist - shift_start).total_seconds() / 60.0)
            else:
                in_shift_response_mins = (resp_ist - creation_ist).total_seconds() / 60.0
            is_fair_breach = in_shift_response_mins > row['sla_target_mins']
            return in_shift_response_mins, is_fair_breach
            
        # If created during day/morning, standard handle time
        total_mins = (resp_ist - creation_ist).total_seconds() / 60.0
        return total_mins, total_mins > row['sla_target_mins']
        
    fair_results = df.apply(compute_fair_handle_time, axis=1)
    df['in_shift_response_mins'] = [r[0] for r in fair_results]
    df['is_fair_breach'] = [r[1] for r in fair_results]
    
    # Flag tickets where morning agent is unfairly blamed for overnight queue arrival
    df['is_unjustly_attributed_breach'] = (df['is_breach'] == True) & (df['creation_shift'] == 'Night') & (df['agent_shift'] == 'Morning')
    
    return df

def generate_breach_summary(df):
    """
    Generates summary tables for reporting and dashboards.
    """
    summary = {
        'total_tickets': len(df),
        'total_breaches': int(df['is_breach'].sum()),
        'overall_breach_rate': float(df['is_breach'].mean()),
        'sla_credits_inr': float(df['is_breach'].sum() * 350),
        'unjust_morning_breaches': int(df['is_unjustly_attributed_breach'].sum()),
        'unjust_breach_credit_inr': float(df['is_unjustly_attributed_breach'].sum() * 350),
        'fair_breaches': int(df['is_fair_breach'].sum()),
        'fair_breach_rate': float(df['is_fair_breach'].mean()),
    }
    
    # Channel summary
    channel_summary = df.groupby('channel').agg(
        tickets=('ticket_id', 'count'),
        standard_breaches=('is_breach', 'sum'),
        standard_breach_rate=('is_breach', 'mean'),
        fair_breaches=('is_fair_breach', 'sum'),
        fair_breach_rate=('is_fair_breach', 'mean'),
        median_first_response_mins=('first_response_mins', 'median')
    ).reset_index()
    
    # Shift summary
    shift_summary = df.groupby(['creation_shift', 'agent_shift']).agg(
        tickets=('ticket_id', 'count'),
        breaches=('is_breach', 'sum'),
        breach_rate=('is_breach', 'mean')
    ).reset_index()
    
    return summary, channel_summary, shift_summary
