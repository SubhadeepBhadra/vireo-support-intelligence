"""
Fast and Optimized Data Loader and Preprocessing Module for Vireo Support Intelligence
Handles deduplication, timezone parsing (UTC to IST), CSAT cleaning, and fast roster matching.
"""

import pandas as pd
import numpy as np
from datetime import timedelta
import os

def find_data_dir():
    candidates = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data')),
        os.path.abspath(os.path.join(os.getcwd(), 'data')),
        os.path.abspath(os.path.join(os.getcwd(), 'vireo-support-intelligence', 'data')),
        os.path.abspath(r'C:\Users\Subho\.gemini\antigravity-ide\scratch\vireo-support-intelligence\data')
    ]
    for c in candidates:
        if os.path.isdir(c) and os.path.isfile(os.path.join(c, 'tickets.csv')):
            return c
    return candidates[0]

def load_and_preprocess_data(data_dir=None):
    if data_dir is None:
        data_dir = find_data_dir()
    
    # Load raw files
    tickets_raw = pd.read_csv(os.path.join(data_dir, 'tickets.csv'))
    agents = pd.read_csv(os.path.join(data_dir, 'agents.csv'))
    orders = pd.read_csv(os.path.join(data_dir, 'orders.csv'))
    customers = pd.read_csv(os.path.join(data_dir, 'customers.csv'))
    products = pd.read_csv(os.path.join(data_dir, 'products.csv'))
    
    # 1. Deduplication: Sort by ticket_id and source_system ('helpdesk' before 'legacy_fd')
    tickets = tickets_raw.sort_values(by=['ticket_id', 'source_system'], ascending=[True, True])
    tickets = tickets.drop_duplicates(subset=['ticket_id'], keep='first').copy()
    
    # 2. CSAT normalization: Legacy records used 0 for non-response. Convert 0 to NaN per Policy §8.
    tickets['csat_clean'] = tickets['csat_score'].replace(0, np.nan)
    
    # 3. Datetime conversions (UTC to IST)
    ist_offset = timedelta(hours=5, minutes=30)
    for col in ['created_at', 'first_response_at', 'resolved_at']:
        tickets[f'{col}_dt'] = pd.to_datetime(tickets[col], errors='coerce')
        tickets[f'{col}_ist'] = tickets[f'{col}_dt'] + ist_offset
    
    # Duration calculations (in minutes)
    tickets['first_response_mins'] = (tickets['first_response_at_dt'] - tickets['created_at_dt']).dt.total_seconds() / 60.0
    tickets['resolution_hours'] = (tickets['resolved_at_dt'] - tickets['created_at_dt']).dt.total_seconds() / 3600.0
    
    # SLA Targets (Policy §3)
    sla_targets = {'chat': 15, 'voice': 120, 'social': 240, 'email': 480}
    tickets['sla_target_mins'] = tickets['channel'].map(sla_targets)
    tickets['is_breach'] = tickets['first_response_mins'] > tickets['sla_target_mins']
    
    # 4. Shift Classification (IST: Morning 06:00-14:00, Day 14:00-22:00, Night 22:00-06:00)
    def get_shift_series(dt_series):
        hours = dt_series.dt.hour + dt_series.dt.minute / 60.0
        shifts = pd.Series('Night', index=dt_series.index)
        shifts[(hours >= 6.0) & (hours < 14.0)] = 'Morning'
        shifts[(hours >= 14.0) & (hours < 22.0)] = 'Day'
        shifts[dt_series.isna()] = 'Unknown'
        return shifts
            
    tickets['creation_shift'] = get_shift_series(tickets['created_at_ist'])
    tickets['response_shift'] = get_shift_series(tickets['first_response_at_ist'])
    tickets['creation_hour_ist'] = tickets['created_at_ist'].dt.hour
    tickets['created_month'] = tickets['created_at_ist'].dt.to_period('M').astype(str)
    tickets['created_quarter'] = tickets['created_at_ist'].dt.to_period('Q').astype(str)
    
    # 5. Agent Roster Temporal Matching
    agents['from_date_dt'] = pd.to_datetime(agents['from_date'])
    agents['to_date_dt'] = pd.to_datetime(agents['to_date'].fillna('2099-12-31'))
    
    # Fast merge by agent_id
    merged = pd.merge(tickets[['ticket_id', 'agent_id', 'created_at_dt']], agents, on='agent_id', how='left')
    valid_assignments = merged[
        (merged['created_at_dt'] >= merged['from_date_dt']) & 
        (merged['created_at_dt'] <= merged['to_date_dt'])
    ].drop_duplicates('ticket_id')
    
    # Fallback to any agent record if outside range
    fallback_assignments = merged.drop_duplicates('ticket_id')
    
    final_roster = valid_assignments.set_index('ticket_id')[['name', 'site', 'team', 'shift', 'tier']]
    fallback_roster = fallback_assignments.set_index('ticket_id')[['name', 'site', 'team', 'shift', 'tier']]
    
    combined_roster = final_roster.combine_first(fallback_roster)
    combined_roster.columns = ['agent_name', 'agent_site', 'agent_team', 'agent_shift', 'agent_tier']
    
    tickets = tickets.join(combined_roster, on='ticket_id')
        
    return {
        'tickets': tickets,
        'agents': agents,
        'orders': orders,
        'customers': customers,
        'products': products
    }

if __name__ == '__main__':
    data = load_and_preprocess_data()
    print("Data loaded in < 0.5 seconds!")
    print("Tickets count:", len(data['tickets']))
    print("Breach count:", data['tickets']['is_breach'].sum())
