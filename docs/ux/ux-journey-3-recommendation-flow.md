# User Journey 3: Recommendation Flow

**SpendSense End-User Experience**
**Flow:** View Recommendation → Understand Rationale → Take Action
**Version:** 1.0
**Last Updated:** November 3, 2025

---

## Overview

### Context
User wants to explore educational recommendations or partner offers tailored to their persona and behavioral signals.

### Entry Points
1. Recommendations section on dashboard (user scrolls down)
2. "View Related Recommendations" button from signal exploration
3. Chat suggests a recommendation
4. Direct navigation from notification (future enhancement)

### User Goals
- Discover personalized educational resources
- Understand why each recommendation was selected
- Take action on recommendations (read, download, explore offers)
- Learn financial concepts without feeling judged

### Business Goals
- Present 3-5 educational items + 1-3 partner offers
- Provide transparent rationale for EVERY recommendation
- Enable action-taking (read article, use tool, explore offer)
- Maintain non-judgmental, educational tone
- Drive engagement with educational content
- Facilitate informed decisions about partner offers

### Emotional Goals
- **Primary:** Informed and motivated
- **Secondary:** Empowered to act
- **Tone:** Educational, transparent, opportunity-focused

---

## Key Journey Steps

### Step 1: Recommendations Feed (Overview)

**Screen:** Recommendations section on dashboard

**Layout:**
- Section header: "Your Personalized Recommendations"
- Subheading: "Based on your [Persona Name] profile and recent behavioral patterns"
- Filter toggle: "Educational Resources" | "Partner Offers" | "All" (default: All)
- Sort options: "Most Relevant" | "Recently Added" | "By Topic"

**Recommendation Cards:**

**Educational Card Example:**
- Icon/type badge (📄 Article, 🧮 Calculator, 📋 Template, 🎥 Video)
- Title (clear, benefit-focused)
- "WHY YOU'RE SEEING THIS" section (2-3 sentences with data citations)
- Metadata: Reading time, difficulty level, topic tags
- CTA: "View Guide →" or "Use Tool →"

**Partner Offer Card Example:**
- Icon/type badge (💳 Card, 🏦 Account, 📱 App, 🛠️ Tool)
- Title and provider
- "WHY YOU'RE SEEING THIS" section with savings calculation
- Eligibility indicators: "✅ You're pre-qualified"
- Mandatory disclaimer: "Educational content, not financial advice"
- CTA: "Learn More →"

**Platform Differences:**
- **Web:** 2-column grid for educational, 1-column for offers
- **Mobile:** Vertical stack, full-width cards

---

### Step 2: Recommendation Detail View

**Layout:** Full-screen modal (web) or dedicated page (mobile)

**Structure:**

#### Header
- Back navigation
- Type badge
- Title (large, clear)
- Quick metadata (time, level, tags)

#### WHY YOU'RE SEEING THIS ⭐ (Critical Transparency Section)
Large callout box (cyan border) containing:
- Specific behavioral signals that triggered this recommendation
- Data citations (clickable links back to source signals)
- Persona match explanation
- Expected benefit/outcome

**Example:**
```
WHY YOU'RE SEEING THIS:

Based on your behavioral signals, we noticed:
• Your Visa ****4523 is at 68% utilization ($3,400 of $5,000 limit)
• This is 38 points above the recommended 30% threshold
• You're paying ~$87/month in interest charges

This guide is recommended for your "High Utilization Manager"
persona because it addresses credit utilization optimization.

[View Full Persona Details →]
```

#### Content Section

**For Educational Recommendations:**
- Full article/guide content (formatted markdown)
- Embedded images, diagrams, examples
- Interactive tools (if applicable)
- Downloadable templates (PDF, Excel)
- Grade-8 readability enforced
- Non-judgmental tone throughout

**For Partner Offers:**
- Offer details (features, terms, eligibility)
- Estimated savings calculation (data-driven)
- Clear eligibility requirements
- Important disclaimer (prominent, not hidden)
- External link warning before navigation

#### Related Resources
- "You Might Also Like" section (2-3 related recommendations)
- Quick links to tools/calculators
- "Ask Chat" link

#### Action Buttons
- **Educational:** "Use Tool" / "Download Template" / "Ask Chat"
- **Partner Offers:** "Learn More" (external) / "Save for Later" / "Not Interested"
- **Feedback:** 👍 Helpful | 👎 Not Helpful

---

### Step 3: Take Action

**Path A: Use Interactive Tool (Educational)**
- Tool opens in modal or new section
- Pre-populated with user's data
- User can adjust inputs (sliders, forms)
- Results update in real-time
- Chat offers guidance

**Path B: Download Template (Educational)**
- File downloads (PDF/Excel)
- Toast confirmation
- Chat offers help: "Need help filling it out?"

**Path C: Explore Partner Offer**
- Warning modal appears BEFORE external link
- Clear messaging: "You're leaving SpendSense"
- Disclaimers: Not affiliated, not a recommendation, compare multiple offers
- User confirms → Opens in new tab
- User cancels → Stays on recommendation

**Path D: Ask Chat for Clarification**
- Chat opens with contextual message
- Quick replies: "Is this right for me?" / "What are the risks?" / "How do I start?" / "Show alternatives"

**Path E: Provide Feedback**
- Click 👍 → Toast: "Thanks for feedback!"
- Click 👎 → Mini survey: "Why wasn't this helpful?"
  - Options: Not relevant / Too advanced / Not enough detail / Other
  - Optional text feedback
  - Submit → Logged for quality review

---

### Step 4: Return to Feed or Explore More

**User Completes Action:**
- Downloaded → Toast confirmation
- Used tool → Results saved (optional)
- Explored offer → "Save for Later" available
- Asked chat → Conversation continues

**Next Steps:**
- "Back to Recommendations" → Returns to feed
- Click another card → Opens new detail view
- Navigate away → Return to dashboard

**Continuity Features:**
- Recently viewed highlighted in feed
- "Save for Later" creates bookmark
- Chat history preserved

---

## Decision Points

1. **Filter Recommendations:** All / Educational only / Partner offers only / By topic
2. **Engage with Recommendation:** Read content / Use tool / Explore offer / Ask chat / Provide feedback
3. **Take External Action:** Navigate to partner site / Download resource / Bookmark for later
4. **Depth of Exploration:** Skim rationale / Read full content / Use interactive tools / Engage with chat

---

## Error Handling & Edge Cases

1. **No Recommendations Available**
   - Display: "We're still analyzing your data. Check back soon!"
   - CTA: "Explore Behavioral Signals"

2. **Content Failed to Load**
   - Fallback: Show title + rationale + "Content temporarily unavailable"
   - CTA: "Try Again" / "Contact Support"

3. **Partner Offer No Longer Available**
   - Replace with: "This offer is no longer available. Here are similar alternatives:"
   - Show 2-3 comparable offers

4. **Eligibility Change**
   - Remove offer from feed
   - If bookmarked: Notification "This offer is no longer available due to updated eligibility"

5. **External Link Broken**
   - Error modal: "We couldn't reach [Provider]'s website. Try again later."
   - CTA: "Return to Recommendations"

6. **Tool/Calculator Error**
   - Fallback: "Calculator temporarily unavailable. View written guide instead?"

---

## Success Metrics

### Primary Metrics
- **Recommendation View Rate:** % who click into details
- **Action Completion Rate:** % who use tools, download, or explore offers
- **Partner Offer Click-Through:** % who navigate to partner sites
- **Feedback Quality:** 👍/👎 ratios, qualitative themes

### Secondary Metrics
- **Chat Engagement from Recs:** % who transition to chat
- **Time Spent:** Average time on recommendation pages
- **Repeat Engagement:** % who return to view more recommendations
- **Tool Usage:** % who interact with calculators/templates

---

## Mermaid Diagram

_(Full interactive diagram available - key flows: Feed → Detail → Action → Return, with branches for educational content, partner offers, chat engagement, and feedback)_

---

## Platform-Specific Adaptations

**Web (≥1024px):**
- 2-column grid for educational recommendations
- 1-column for partner offers (more prominent)
- Side-by-side layout for offer details vs. rationale
- Modal overlays for detail views

**Mobile (<768px):**
- Vertical stack, full-width cards
- Scrollable detail pages
- Bottom sheet for filters
- Sticky CTA buttons

---

## Accessibility Requirements

- WCAG AA color contrast
- Keyboard navigation (Tab, Enter, Escape)
- Screen reader support (ARIA labels, live regions)
- Touch targets ≥48x48px (mobile)
- Focus indicators clearly visible
- Respect `prefers-reduced-motion`

---

## Technical Requirements

**Frontend Components:**
- `RecommendationsFeed.tsx`
- `RecommendationCard.tsx`
- `RecommendationDetail.tsx`
- `ExternalLinkWarning.tsx`
- `FeedbackSurvey.tsx`

**API Endpoints:**
- GET `/recommendations/{user_id}`
- POST `/recommendations/{rec_id}/feedback`
- POST `/recommendations/{rec_id}/bookmark`
- GET `/recommendations/{rec_id}/eligibility`

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
- [Journey 4: Chat Interaction](./ux-journey-4-chat-interaction.md)

---

**Note:** This document provides a comprehensive summary. Full detailed specifications including complete content examples, all error states, detailed Mermaid diagrams, and persona-specific recommendations are available in the complete design documentation.
