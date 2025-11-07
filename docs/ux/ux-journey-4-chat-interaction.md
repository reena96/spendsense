# User Journey 4: Chat Interaction Patterns

**SpendSense End-User Experience**
**Flow:** Ask Question → Receive Explanation → Follow-up Questions
**Version:** 1.0
**Last Updated:** November 3, 2025

---

## Overview

### Context
User wants to ask questions about their financial data, personas, signals, or recommendations. Chat is always accessible and context-aware.

### Entry Points
1. **Proactive greeting** during onboarding (Step 5d of tour)
2. **"Ask Chat" button** from signal detail view
3. **"Ask Chat" button** from recommendation detail
4. **Direct click** on chat sidebar (web) or chat tab (mobile)
5. **Quick action** from dashboard

### User Goals
- Get plain-language explanations of financial concepts
- Understand specific data points and patterns
- Ask follow-up questions without repeating context
- Receive personalized guidance based on their data
- Learn without feeling judged

### Business Goals
- Provide conversational, plain-language financial education
- Maintain context across conversation threads
- Cite specific user data in responses
- Guide users to relevant tools/resources
- Never provide regulated financial advice (enforce guardrails)
- Build trust through helpful, accurate responses

### Emotional Goals
- **Primary:** Supported and understood
- **Secondary:** Confident and informed
- **Tone:** Friendly coach, not judgmental advisor

---

## Chat Entry & Initial State

### Platform-Specific Layout

**Web (Desktop/Tablet, ≥1024px):**
- **Persistent sidebar:** 40% width on right side
- **Always visible** when viewport ≥1024px
- **Collapsible** on tablets (768-1023px) → Floating widget
- **Sticky:** Scrolls with page, always accessible
- **Header:** "SpendSense Coach" with online status indicator

**Mobile (<768px):**
- **Dedicated tab:** Bottom tab navigation (5 tabs)
- **Icon:** 💬 Chat (with notification badge if unread)
- **Full screen** when active
- **Background notifications** when in other tabs

### Initial Chat State (Empty/First Use)

```
┌─────────────────────────────────┐
│  💬 SpendSense Coach       [●] │
│  ───────────────────────────── │
│                                 │
│  [Avatar]                       │
│                                 │
│  Hi! I'm your SpendSense coach. │
│  I can help you understand your │
│  financial patterns and answer  │
│  questions about your data.     │
│                                 │
│  What would you like to know?   │
│                                 │
│  [Quick Start Buttons]:         │
│  • Explain my persona           │
│  • Why is my utilization high?  │
│  • How can I save more?         │
│  • What are these signals?      │
│                                 │
│  ───────────────────────────── │
│  [Type a message...]       [→] │
└─────────────────────────────────┘
```

### Chat Header Features
- **Title:** "SpendSense Coach"
- **Status:** "● Online" (green dot)
- **Actions:**
  - Minimize (web): Collapse to floating widget
  - Clear conversation: Reset chat history
  - Settings: Toggle sound, notifications

---

## Step-by-Step Flow

### Step 1: User Initiates Conversation

**Input Methods:**

**A. Click Quick Start Button**
- Pre-defined question (e.g., "Explain my persona")
- Button text populates as user message
- Chat immediately responds

**B. Type Freeform Question**
- Character limit: 500 characters
- Press Enter or click → to send
- Typing indicator shows while processing

**C. Voice Input (Future Enhancement)**
- Click microphone icon
- Speak question
- Transcribed to text, then sent

**Message Send Behavior:**
- User message appears in bubble (right-aligned, cyan background)
- Input field clears
- Chat shows "typing..." indicator
- Response appears after 1-3 seconds

---

### Step 2: Chat Responds with Context-Aware Answer

Chat maintains context and knows:
- What screen/feature user is viewing
- User's specific data (persona, signals, values)
- Previous questions in conversation
- Time window selected (if viewing signal)

### Response Patterns (5 Types)

---

#### **Pattern 1: Explaining Persona Assignment**

**Trigger:** User asks "Explain my persona" or similar

**Response Structure:**
```
You're assigned to the 'High Utilization Manager' persona.
Here's why:

Based on your transaction data, I noticed:
• Your Visa ****4523 is at 68% utilization ($3,400 / $5,000)
• This is 38 points above the recommended 30% threshold
• You're paying approximately $87/month in interest

This persona focuses on helping you:
✓ Understand credit utilization and its impact
✓ Explore strategies to lower your balance
✓ Potentially improve your credit score

Want to see specific recommendations for your situation?

[Quick Reply Buttons]:
• Show me recommendations
• How do I lower utilization?
• Why does 30% matter?
```

**Key Elements:**
- Persona name and description
- Specific data citations (transparent)
- Benefit-focused framing
- Quick replies for common follow-ups

---

#### **Pattern 2: Explaining Behavioral Signal**

**Trigger:** User asks about specific signal (e.g., "Why is my credit utilization high?")

**Response Structure:**
```
Great question! Your utilization is at 68%, which is above
the recommended 30%. Here's the breakdown:

📊 Your Current Status:
• Visa ****4523: $3,400 / $5,000 (68%) 🔴
• Mastercard ****8901: $450 / $2,000 (23%) 🟢
• Overall utilization: 62%

Credit bureaus recommend <30% because:
1. High utilization signals financial stress
2. It can lower your credit score by 20-40 points
3. Lenders view it as a risk factor

To reach 30% on your Visa, you'd need to pay down to ~$1,500.

Want to explore paydown strategies?

[Quick Reply Buttons]:
• Yes, show me strategies
• How long would that take?
• View detailed breakdown
```

**Key Elements:**
- Direct answer to question
- Data breakdown (specific numbers)
- Educational explanation (why it matters)
- Actionable insight (what to do)
- Quick replies for next steps

---

#### **Pattern 3: Recommendation Clarification**

**Trigger:** User asks about specific recommendation (e.g., "Is the balance transfer card right for me?")

**Response Structure:**
```
Good question! Let me break down whether this makes sense
for your situation:

✅ Potential Benefits:
• Save $1,464 in interest over 18 months
• 0% APR gives breathing room to pay down debt
• You're pre-qualified based on your credit profile

⚠️ Important Considerations:
• 3% balance transfer fee ($102 upfront)
• Need to pay off before 18 months ends
• If you keep charging on old card, could increase debt

💡 My Take:
This could work if you:
• Can commit to paying $200/month (debt-free in 17 months)
• Stop using current card for new purchases
• Have a plan to avoid new debt

Want me to show you a paydown calculator with your numbers?

[Quick Reply Buttons]:
• Yes, show calculator
• What are the risks?
• Show me alternatives
```

**Key Elements:**
- Pros and cons (balanced view)
- Specific to user's situation
- "My Take" section (personalized guidance)
- Action-oriented follow-ups

---

#### **Pattern 4: How-To / Educational Query**

**Trigger:** User asks "how" questions (e.g., "How can I save more?")

**Response Structure:**
```
Great goal! Based on your data, I see a few opportunities:

💰 Subscription Optimization:
You have 7 active subscriptions ($124/month). Some overlap:
• Netflix ($15.99) + Hulu ($12.99) — consolidate?
• Adobe Creative Cloud ($54.99) — use all features?

Potential savings: $20-40/month = $240-480/year

🏦 Automate Savings:
You get paid biweekly ($2,500). Auto-transfer just $100
per paycheck = $2,600/year saved.

📊 Your Current Savings:
• Emergency fund: 2.5 months ($12,500)
• Goal: 6 months ($30,000)
• Gap: $17,500

Which opportunity would you like to explore first?

[Quick Reply Buttons]:
• Review my subscriptions
• Set up auto-savings plan
• See savings strategies
```

**Key Elements:**
- Multiple actionable opportunities
- Specific calculations (personalized)
- Prioritized by potential impact
- User chooses path forward

---

#### **Pattern 5: Comparison / What-If Questions**

**Trigger:** User asks comparative questions (e.g., "What if I increase my credit limit instead of paying down?")

**Response Structure:**
```
Interesting strategy! Let me compare both approaches:

📈 Option 1: Request Credit Limit Increase
• Current: $5,000 limit, $3,400 balance = 68%
• If increased to $8,000: same balance = 43% ✓
• Pros: No payment required, instant utilization drop
• Cons: Hard inquiry (temporary score dip), doesn't reduce debt

💵 Option 2: Pay Down Balance
• Pay down to $1,500 (30% of current $5,000 limit)
• Need to pay off: $1,900
• Pros: Reduces debt, saves interest, improves score long-term
• Cons: Requires cash, takes time

🎯 Hybrid Approach:
Many people do BOTH:
1. Request limit increase → immediate utilization improvement
2. Continue paying balance → long-term debt reduction

At $200/month payments, you'd reach 30% in ~10 months.

Want to see a detailed paydown timeline?

[Quick Reply Buttons]:
• Show me the calculator
• How do I request limit increase?
• What's better for my score?
```

**Key Elements:**
- Side-by-side comparison
- Pros and cons for each option
- Hybrid suggestion (creative solution)
- Follow-up resources

---

### Step 3: User Asks Follow-Up Questions

**Conversation Context Maintenance:**

Chat remembers:
- What signal/recommendation user was viewing
- Questions already asked
- User's specific data and values
- Conversation thread context

**Example Multi-Turn Conversation:**

```
User: "Why is my utilization high?"

Chat: [Explains with data: 68%, $3,400/$5,000]

User: "How long to pay it down?"

Chat: "At your current minimum of $68/month, about 5 years
and $1,800 in interest.

But if you increased to:
• $150/month → 2 years, $600 interest
• $200/month → 1.5 years, $400 interest
• $300/month → 11 months, $250 interest

Want an interactive calculator to adjust numbers?"

User: "Yes"

Chat: "Great! Opening Debt Paydown Calculator...
[Calculator opens with pre-filled data]

I've filled in your Visa ****4523:
• Balance: $3,400
• APR: 18.99%
• Current min: $68

Try the 'Monthly Payment' slider to see how different
amounts affect timeline and interest. Need help?"

User: "What if I can only pay $100/month?"

Chat: [Recalculates] "At $100/month:
• Payoff: 3.5 years
• Total interest: $900
• Saves $900 vs. minimum payments

That's a solid middle ground! Save this as your plan?"
```

**Context Switching:**

If user changes topic:
```
User: [Discussing credit utilization]
      "What about my subscriptions?"

Chat: "Sure, happy to switch gears! Let's look at your
subscriptions.

You have 7 active totaling $124/month (3% of income):
[Lists subscriptions]

What would you like to know?"
```

---

### Step 4: Chat Guides to Resources/Actions

**Proactive Tool Suggestions:**

```
Based on your question, the Debt Paydown Calculator would
be helpful. Want me to open it with your data pre-filled?

[Quick Replies]:
• Yes, open calculator
• No, just explain it
• Show written guide instead
```

**Linking to Recommendations:**

```
This sounds like our 'Credit Utilization 101' guide covers
in detail. It includes:
• Step-by-step strategies
• Real examples
• Downloadable worksheets

[Button]: View Guide →
```

**Transitioning to Signal Detail:**

```
Want to see a detailed breakdown with charts and trends?

[Button]: View Credit Utilization Details →

I'll still be here if you have questions!
```

---

### Step 5: Chat Session Continuation & Exit

**Session Persistence:**
- Chat history saved across sessions
- User can scroll up to see previous messages
- Timestamps for older messages ("2 hours ago", "Yesterday")

**Ending Conversation:**

Chat provides soft exits:
```
Is there anything else I can help you with?

[Quick Replies]:
• Ask another question
• View recommendations
• Return to dashboard
• I'm all set, thanks!
```

**Leaving Chat:**
- **Web:** Click elsewhere, chat sidebar stays visible
- **Mobile:** Navigate to different tab, chat badge shows unread count

**Clearing History:**
- User clicks "Clear Conversation" in settings
- Confirmation modal: "This will delete your chat history. Continue?"
- If confirmed → History cleared, resets to initial state

---

## Chat Features & Patterns

### Quick Reply Buttons
- Max 4 buttons per response
- Common follow-up questions
- Mobile-optimized (thumb-friendly)
- Clicking sends as user message

### Rich Content in Chat

**Embedded Cards:**
```
Here's a summary of your credit utilization:

┌──────────────────────────────────┐
│ 📊 Credit Utilization Summary    │
│                                  │
│ Overall: 62% 🔴                  │
│ ──────────────────────────────── │
│ Visa ****4523                    │
│ $3,400 / $5,000 (68%) 🔴         │
│                                  │
│ Mastercard ****8901              │
│ $450 / $2,000 (23%) 🟢           │
│                                  │
│ [View Full Breakdown →]          │
└──────────────────────────────────┘
```

**Inline Charts:**
- Simple bar/line charts
- Color-coded for quick understanding
- Clickable → Opens full signal detail

**Actionable Links:**
- "View this signal" → Opens signal detail
- "See this recommendation" → Opens rec detail
- "Use this calculator" → Opens tool

### Typing Indicators
- Animated dots: "●●●"
- Shows when chat is "thinking"
- Appears immediately after user sends message

---

## Error Handling

### Chat Unavailable
```
[Banner at top]
⚠️ Chat temporarily unavailable. Trying to reconnect...

[After 10 seconds if still down]
Chat is currently offline. You can still explore
your dashboard and recommendations.

[Dismiss] [Try Again]
```

### Message Failed to Send
```
[User message with warning icon]
User: "Why is my utilization high?" ⚠️

Message failed to send. [Retry] [Dismiss]
```

### Inappropriate Question (Guardrail Triggered)
```
User: "Should I invest in crypto?"

Chat: "I can't provide investment advice or recommend
specific financial products—that's regulated advice
requiring a licensed professional.

What I CAN help with:
• Understanding your behavioral patterns
• Explaining educational concepts
• Guiding you to resources

Want to ask about your transaction data instead?"
```

### Out of Scope Question
```
User: "What's the weather today?"

Chat: "I'm focused on helping with financial data.
I can answer questions about:
• Your assigned persona
• Behavioral signals
• Recommendations
• Financial concepts

What financial question can I help with?"
```

---

## Success Metrics

### Primary Metrics
- **Chat Engagement Rate:** % who interact with chat
- **Conversation Length:** Average turns per session
- **Resolution Rate:** % ending with helpful action taken
- **Guardrail Trigger Rate:** % flagged (goal: <1%)

### Secondary Metrics
- **Transition Rate:** % who move chat → tools/recs
- **Quick Reply Usage:** % using quick reply vs. freeform
- **User Satisfaction:** Thumbs up/down on responses

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-03 | Initial journey document (summary) | Reena |

---

**Related Documents:**
- [Main UX Specification](./ux-design-specification.md)
- [Journey 1: Onboarding](./ux-journey-1-onboarding.md)
- [Journey 2: Signal Exploration](./ux-journey-2-signal-exploration.md)
- [Journey 3: Recommendation Flow](./ux-journey-3-recommendation-flow.md)

---

**Note:** This document provides a comprehensive summary. Full detailed specifications including complete conversation examples, all guardrail scenarios, detailed error handling, Mermaid diagrams, and technical implementation requirements are available in the complete design documentation.
