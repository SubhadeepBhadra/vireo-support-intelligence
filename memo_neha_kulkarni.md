# Memorandum

**To:** Neha Kulkarni, Support Operations Manager  
**From:** Subhadeep Bhadra, Operations & Analytics Lead  
**Date:** 29 September 2026  
**Subject:** SLA Breach Attribution, Shift Roster Analysis, and Cost Recovery  

---

Neha,

You asked for a weekly breach report broken down by agent and shift so you could speak with the people breaching our first-response targets. 

Before generating that report, I ran an audit across all 11,200 unique tickets and roster history from the past 18 months. The numbers tell a very different story than what shows up on the standard helpdesk dashboard: **our morning chat agents are not underperforming. They are taking the blame for an unstaffed night queue.**

### 1. What is actually happening at 06:00 IST

When the Indore night shift was restructured at the end of June 2025, overnight coverage dropped from 5 agents to zero. However, our website widget continued to offer 24x7 chat with a 15-minute response target.

Every night, roughly 70 to 80 customer chats arrive between 22:00 and 06:00 IST. With no one logged in, these tickets sit in queue for 4 to 8 hours.

When the morning team logs in at 06:00 IST:
1. They open their queues to dozens of tickets that have already breached their SLA hours ago.
2. They pick them up and send replies quickly—averaging about 4 minutes of handle time.
3. Because our helpdesk logs the breach against the *resolving* agent rather than the creation timestamp, every one of those tickets is counted as a failure against the morning agent.

Out of 2,440 total breaches recorded over the 18 months, **1,566 (64.2%) happened because the ticket arrived during the night shift when no one was working.**

If we pull morning agents into 1-on-1s over these numbers, we will penalize the exact people who are clearing the overnight backlog every day. It explains why the morning team is demoralized—they start every shift already underwater.

```
Customer sends chat at 01:30 IST (Queue unstaffed)
  │
  ▼ [Waits 4.5 hours in queue — 15 min SLA expires at 01:45]
Morning agent logs in at 06:00 IST
  │
  ▼ [Agent replies at 06:04 IST — 4 min handle time]
Helpdesk logs a 274-minute breach against the Morning Agent ❌
```

### 2. Why SLA credit costs tripled in the P&L

Arjun noted that our SLA credit line tripled since last summer. 

Under Support Policy §3, every breached ticket automatically issues a Rs 350 store credit to the customer. Prior to July 2025, our breach payouts were roughly Rs 35,000 to Rs 40,000 a quarter. Once the night shift was removed, quarterly credits jumped to over Rs 1,95,000. 

In total, we have paid out **Rs 8.54 Lakhs** in SLA credits over 18 months—and more than **Rs 5.48 Lakhs** of that was directly caused by the overnight queue gap. The June restructuring was meant to be cost-neutral, but the surge in SLA credits erased those savings.

### 3. Additional financial leakages discovered

While matching ticket logs with order numbers and unit costs, I found two other policy issues that need immediate operational fixes:

1. **Duplicate Refund + Replacement (Double-Dipping):**  
   Policy §5 states customers should never receive both a refund and a replacement for the same order. We have **95 orders** where agents issued both a cash refund and an RMA replacement. This cost us **Rs 4,37,418** in unrecovered product cost, shipping, and cash payouts.
2. **Goodwill Limit Overrides:**  
   Policy §5 caps goodwill at Rs 500 without Team Lead sign-off. We found **45 tickets** under reason code `GW-OTHER` where payouts exceeded Rs 500 (some up to Rs 5,699), totaling **Rs 1,38,605** in excess unapproved credits.
3. **Bot Misrouting & Hand-offs:**  
   Our intake bot misclassifies technical issues regularly, causing **1,129 internal team transfers** across the period. At our standard rate of Rs 305 per transfer, this added **Rs 3,44,345** in re-handling friction.

### 4. Proposed Plan (Zero New Headcount)

With the Q4 headcount freeze in place, we cannot hire our way out of this. Fortunately, we don't need to:

| Step | Action | Impact |
| :--- | :--- | :--- |
| **1. Rebalance 3 Roster Slots** | Shift 3 agents from the Bengaluru Day shift (currently 17 agents) to Indore Night shift (22:00–06:00 IST) dedicated to chat triage. | Eliminates ~85% of overnight chat breaches. Saves ~Rs 1.4 Lakhs per quarter in SLA credits. |
| **2. Fix Helpdesk Reporting Logic** | Update our weekly dashboard to measure first-response time against shift start times rather than penalizing resolving agents for overnight lag. | Gives an accurate view of agent handle time and lifts morning team morale immediately. |
| **3. Hard-Stop Validation Rules** | Add a validation check in the helpdesk so an agent cannot process a refund if a replacement RMA is active on the same order_id, and lock `GW-OTHER` above Rs 500 without TL credentials. | Stops Rs 5.76 Lakhs in annual leakage immediately. |

---

### Next Steps

I have set up a working prototype dashboard (`app.py`) that demonstrates the corrected SLA attribution, monitors double-dipping in real time, and provides an auto-triage assistant to draft initial responses.

Let me know when you have 15 minutes this week so we can review the shift numbers together before we update the roster.
