"""
Vireo Support Intelligence - Executive Dashboard & Operations Hub
Streamlit Application providing deep operational diagnostics, SLA attribution audit, leakage detection, and AI triage.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from data_loader import load_and_preprocess_data
from sla_engine import calculate_sla_metrics, generate_breach_summary
from leakage_detector import audit_policy_compliance
from classifier import TicketClassifier
from responder import ResponseGenerator

st.set_page_config(
    page_title="Vireo Support Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .kpi-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #38bdf8;
    }
    .metric-label {
        font-size: 13px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-delta-bad {
        color: #f87171;
        font-size: 13px;
        font-weight: 600;
    }
    .metric-delta-good {
        color: #4ade80;
        font-size: 13px;
        font-weight: 600;
    }
    .highlight-box {
        background-color: #1e1b4b;
        border-left: 4px solid #6366f1;
        padding: 16px;
        border-radius: 4px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_data():
    raw_data = load_and_preprocess_data()
    raw_data['tickets_sla'] = calculate_sla_metrics(raw_data['tickets'])
    raw_data['audit'] = audit_policy_compliance(raw_data)
    return raw_data

@st.cache_resource
def get_models(tickets):
    clf = TicketClassifier()
    clf.train(tickets)
    gen = ResponseGenerator()
    return clf, gen

data = get_data()
tickets = data['tickets_sla']
audit = data['audit']
clf, gen = get_models(tickets)

summary, channel_sum, shift_sum = generate_breach_summary(tickets)

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/isometric/100/headphones.png", width=60)
st.sidebar.title("Vireo Audio Ops")
st.sidebar.caption("Support Desk Intelligence & Recovery Platform")

nav = st.sidebar.radio(
    "Navigation",
    ["📊 Executive Overview", "🔍 SLA Breach Attribution Audit", "🚨 Financial Leakage Sentinel", "🤖 AI Triage & Response Simulator", "📈 Shift & ROI Simulator"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 Operational Health")
st.sidebar.metric("Unique Tickets Analyzed", f"{len(tickets):,}")
st.sidebar.metric("Annualized SLA Loss", f"Rs {summary['sla_credits_inr']*(12/18):,.0f}")
st.sidebar.metric("Identified Financial Waste", f"Rs {(audit['double_dipping']['total_leakage_inr'] + audit['goodwill_violations']['total_excess_inr'] + audit['transfers']['total_cost_inr']):,.0f}")

# 1. EXECUTIVE OVERVIEW
if nav == "📊 Executive Overview":
    st.title("Executive Intelligence Dashboard")
    st.markdown("### Comprehensive Diagnostic of Support Operations & Financial Leakage")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="kpi-card">
            <div class="metric-label">Reported SLA Breaches</div>
            <div class="metric-value">2,440 <span style="font-size:16px; color:#f87171;">(21.8%)</span></div>
            <div class="metric-delta-bad">Charged: Rs 8.54 Lakhs</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="kpi-card">
            <div class="metric-label">Unjust Morning Attributions</div>
            <div class="metric-value">1,566 <span style="font-size:16px; color:#38bdf8;">(64.2%)</span></div>
            <div class="metric-delta-good">Caused by Night Queue Lag</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="kpi-card">
            <div class="metric-label">Double-Dipping Leakage</div>
            <div class="metric-value">Rs 4.37 Lakhs</div>
            <div class="metric-delta-bad">95 Duplicate Orders</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown("""
        <div class="kpi-card">
            <div class="metric-label">Net Addressable Recovery</div>
            <div class="metric-value">Rs 12.8 Lakhs/yr</div>
            <div class="metric-delta-good">Zero New Hiring Required</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="highlight-box">
        <h4>⚡ Key Finding for Executive Leadership</h4>
        <p><strong>The Morning Team is NOT failing.</strong> 64.2% of all recorded breaches (1,566 tickets) are overnight chat/email requests arriving between 22:00 and 06:00 IST when zero agents are rostered. Morning agents open their screens to already-expired tickets, answer them in an average of 4 minutes, but get dinged for an 8-hour breach due to helpdesk timestamp attribution flaw.</p>
    </div>
    """, unsafe_allow_html=True)

    # Charts
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Monthly SLA Penalty Credits in P&L")
        monthly_trend = tickets.groupby('created_month').agg(
            breaches=('is_breach', 'sum'),
            credits=('is_breach', lambda x: x.sum() * 350)
        ).reset_index()
        fig_trend = px.bar(
            monthly_trend, x='created_month', y='credits',
            labels={'created_month': 'Month', 'credits': 'SLA Store Credits (INR)'},
            color_discrete_sequence=['#ef4444']
        )
        june_idx = monthly_trend[monthly_trend['created_month'] == '2025-06'].index
        if len(june_idx) > 0:
            fig_trend.add_vline(x=june_idx[0] + 0.5, line_dash="dash", line_color="#38bdf8", annotation_text="Indore Night Shift Eliminated (June 2025)", annotation_position="top left")
        fig_trend.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_r:
        st.subheader("Breach Rate by Ticket Creation Shift")
        shift_channel = pd.crosstab(tickets['channel'], tickets['creation_shift'], values=tickets['is_breach'], aggfunc='mean') * 100
        fig_shift = px.bar(
            shift_channel, barmode='group',
            labels={'value': 'Breach Rate (%)', 'channel': 'Support Channel'},
            color_discrete_sequence=['#3b82f6', '#10b981', '#f59e0b']
        )
        fig_shift.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig_shift, use_container_width=True)

# 2. SLA BREACH ATTRIBUTION AUDIT
elif nav == "🔍 SLA Breach Attribution Audit":
    st.title("SLA Breach Attribution Audit")
    st.markdown("### Debunking the Morning Shift Myth & Uncovering True Queue Dynamics")
    
    st.write("Vireo's standard helpdesk report attributes breaches to the **resolving agent**. When tickets arrive overnight with 0 night staff, morning agents pick up breached tickets and bear 100% of the statistical blame.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Hourly Arrival vs Breach Rate (IST)")
        hourly = tickets.groupby('creation_hour_ist').agg(
            arrivals=('ticket_id', 'count'),
            breach_rate=('is_breach', lambda x: x.mean() * 100)
        ).reset_index()
        fig_hourly = go.Figure()
        fig_hourly.add_trace(go.Bar(x=hourly['creation_hour_ist'], y=hourly['arrivals'], name='Arrivals', marker_color='#64748b'))
        fig_hourly.add_trace(go.Scatter(x=hourly['creation_hour_ist'], y=hourly['breach_rate'], name='Breach %', yaxis='y2', line=dict(color='#ef4444', width=3)))
        fig_hourly.update_layout(
            template="plotly_dark",
            xaxis=dict(title="Hour of Day (IST)"),
            yaxis=dict(title="Total Ticket Volume"),
            yaxis2=dict(title="Breach Rate (%)", overlaying='y', side='right', range=[0, 100]),
            height=380
        )
        st.plotly_chart(fig_hourly, use_container_width=True)
        
    with col_b:
        st.subheader("Reported Breaches vs Fair In-Shift Breaches")
        comp_df = pd.DataFrame({
            'Category': ['Standard Helpdesk Report', 'Fair Attribution (In-Shift Only)'],
            'Breach Count': [summary['total_breaches'], summary['fair_breaches']],
            'SLA Credit Penalty (INR)': [summary['sla_credits_inr'], summary['fair_breaches'] * 350]
        })
        fig_comp = px.bar(
            comp_df, x='Category', y='SLA Credit Penalty (INR)',
            color='Category', color_discrete_sequence=['#ef4444', '#10b981'],
            text_auto=True
        )
        fig_comp.update_layout(template="plotly_dark", height=380, showlegend=False)
        st.plotly_chart(fig_comp, use_container_width=True)

    st.subheader("Agent-by-Agent Fair Performance Matrix")
    agent_perf = tickets.groupby(['agent_id', 'agent_name', 'agent_shift']).agg(
        total_resolved=('ticket_id', 'count'),
        reported_breaches=('is_breach', 'sum'),
        fair_breaches=('is_fair_breach', 'sum'),
        avg_csat=('csat_clean', 'mean')
    ).reset_index()
    agent_perf['unfair_penalty_count'] = agent_perf['reported_breaches'] - agent_perf['fair_breaches']
    agent_perf = agent_perf.sort_values(by='unfair_penalty_count', ascending=False)
    st.dataframe(agent_perf, use_container_width=True)

# 3. FINANCIAL LEAKAGE SENTINEL
elif nav == "🚨 Financial Leakage Sentinel":
    st.title("Financial Leakage Sentinel")
    st.markdown("### Detecting Double-Dipping, Unauthorized Goodwill, and Transfer Waste")
    
    tab1, tab2, tab3 = st.tabs(["Duplicate Refund + Replacement", "Goodwill Cap Violations (>Rs 500)", "Transfer & Routing Waste"])
    
    with tab1:
        st.subheader(f"Double-Dipping Audit: {audit['double_dipping']['count']} Violating Orders")
        st.error(f"Total Direct Financial Leakage: Rs {audit['double_dipping']['total_leakage_inr']:,.2f} (Refund: Rs {audit['double_dipping']['total_refund_inr']:,.2f} | Replacement + Logistics: Rs {audit['double_dipping']['total_replacement_cost_inr']:,.2f})")
        st.dataframe(audit['double_dipping']['orders_df'][['order_id', 'sku', 'product_name', 'total_refund', 'unit_cost_inr', 'total_leakage_inr', 'ticket_ids']], use_container_width=True)
        
    with tab2:
        st.subheader(f"Goodwill Policy Overrides: {audit['goodwill_violations']['count']} Cases")
        st.warning(f"Total Excess Unauthorized Payouts: Rs {audit['goodwill_violations']['total_excess_inr']:,.2f}")
        st.dataframe(audit['goodwill_violations']['violations_df'][['ticket_id', 'agent_id', 'refund_amount_inr', 'excess_amount_inr', 'category', 'agent_notes']], use_container_width=True)
        
    with tab3:
        st.subheader("Internal Hand-Off & Misrouting Waste")
        st.info(f"Total Transfers: {audit['transfers']['total_transfers']} across 18 months @ Rs 305/transfer = Rs {audit['transfers']['total_cost_inr']:,.2f}")
        st.dataframe(audit['transfers']['category_breakdown'], use_container_width=True)

# 4. AI TRIAGE & RESPONSE SIMULATOR
elif nav == "🤖 AI Triage & Response Simulator":
    st.title("AI Intent Classifier & Response Drafter")
    st.markdown("### Real-time Ticket Categorization, Policy Enforcement, and Instant Drafts")
    
    sample_queries = [
        "Select a sample or type your own below...",
        "My pulse 2 earbuds arrived yesterday and won't turn on or take charge in the case",
        "Where is my order VR895588? It's been 5 days since dispatch and tracking hasn't updated",
        "I was charged twice on my credit card for the nexa smartwatch order",
        "Sound is crackling and distorted in the left earbud when bass hits",
        "I want a full refund and also send me a replacement piece immediately"
    ]
    
    selected_sample = st.selectbox("Quick Test Samples:", sample_queries)
    custom_msg = st.text_area("Customer Opening Message:", value="" if selected_sample == sample_queries[0] else selected_sample, height=100)
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        cust_name = st.text_input("Customer Name:", value="Rahul Sharma")
    with col_c2:
        order_num = st.text_input("Order ID:", value="VR902341")
    with col_c3:
        prod_name = st.text_input("Product Name:", value="Pulse 2 Earbuds")
        
    if st.button("⚡ Run AI Triage & Draft Response", type="primary"):
        if not custom_msg.strip():
            st.warning("Please enter a customer message.")
        else:
            pred = clf.predict(custom_msg)
            draft_res = gen.generate_draft(
                customer_message=custom_msg,
                category=pred['category'],
                customer_name=cust_name,
                order_id=order_num,
                product_name=prod_name,
                agent_name="Priya Raman"
            )
            
            st.markdown("---")
            col_res1, col_res2 = st.columns([1, 2])
            with col_res1:
                st.subheader("🎯 Triage & Routing")
                st.metric("Predicted Category", pred['category'])
                st.metric("Target Destination Team", pred['team'])
                st.metric("Confidence Score", f"{pred['confidence']*100:.1f}%")
                
            with col_res2:
                st.subheader("📝 AI-Generated Draft Response")
                st.text_area("Ready-to-Send Response (Editable)", value=draft_res['draft_response'], height=200)
                
                if draft_res['policy_warnings']:
                    for w in draft_res['policy_warnings']:
                        st.error(w)
                else:
                    st.success("✅ Clean Policy Check: No compliance flags detected.")

# 5. SHIFT & ROI SIMULATOR
elif nav == "📈 Shift & ROI Simulator":
    st.title("Operational Shift & ROI Simulator")
    st.markdown("### Model Financial Savings from Roster Realignment & AI Auto-Triage")
    
    st.write("Adjust operational levers to calculate immediate quarterly financial recovery without hiring new headcount.")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        reallocated_night_agents = st.slider("Reallocate Day/Morning Agents to Night Shift (22:00-06:00):", min_value=0, max_value=6, value=3)
        ai_auto_triage_adoption = st.slider("AI Auto-Triage & Instant Routing Adoption Rate (%):", min_value=0, max_value=100, value=75)
        double_dip_enforcement = st.checkbox("Enable Automated Double-Dipping Sentinel", value=True)
        goodwill_cap_enforcement = st.checkbox("Strict Goodwill Rs 500 Cap Guardrail", value=True)
        
    with col_s2:
        st.subheader("Simulated Quarterly Financial Impact")
        
        # Base numbers per quarter:
        q_tickets = 2250
        base_q_breaches = 565
        base_q_sla_credit = base_q_breaches * 350 # ~197,750
        
        # Night recovery impact
        night_breach_reduction_pct = min(0.85, reallocated_night_agents * 0.25)
        prevented_night_breaches = int(base_q_breaches * 0.64 * night_breach_reduction_pct)
        sla_savings_q = prevented_night_breaches * 350
        
        # Transfer savings
        q_transfers = 188
        transfer_savings_q = (q_transfers * (ai_auto_triage_adoption / 100.0) * 0.7) * 305
        
        # Double dipping savings
        dd_savings_q = (437418 / 6.0) if double_dip_enforcement else 0
        
        # Goodwill savings
        gw_savings_q = (138605 / 6.0) if goodwill_cap_enforcement else 0
        
        total_q_savings = sla_savings_q + transfer_savings_q + dd_savings_q + gw_savings_q
        
        st.metric("SLA Penalty Credit Reduction", f"Rs {sla_savings_q:,.0f} / quarter")
        st.metric("Transfer Cost Savings", f"Rs {transfer_savings_q:,.0f} / quarter")
        st.metric("Policy Leakage Prevention", f"Rs {(dd_savings_q + gw_savings_q):,.0f} / quarter")
        st.markdown(f"### 💰 Total Quarterly Net Recovery: <span style='color:#4ade80;'>Rs {total_q_savings:,.0f}</span>", unsafe_allow_html=True)
        st.markdown(f"#### 📅 Annualized Net Recovery: <span style='color:#38bdf8;'>Rs {total_q_savings * 4:,.0f}</span>", unsafe_allow_html=True)
