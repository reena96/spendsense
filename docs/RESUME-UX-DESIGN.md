# Resume UX Design - Copy/Paste Prompt

Use this prompt to resume the SpendSense UX design workflow in a new session.

---

## 📋 Prompt to Copy/Paste:

```
I'm resuming the UX design workflow for SpendSense, a financial education AI platform.

**Project Context:**
SpendSense is a B2B financial wellness platform for financial institutions. It uses transaction data to detect behavioral patterns, assign users to educational personas, and deliver personalized financial education through a transparent, explainable AI system.

**What's Been Completed (Phase 1):**
I've already completed the first phase of UX design work. All decisions are documented in:
`/Users/reena/gauntletai/spendsense/docs/ux-design-specification.md`

Please read this specification document first to understand:
- Design system selected: shadcn/ui v2.0 (React 18 + TypeScript + Tailwind + Vite)
- Visual foundation: "Balanced Calm" color theme (cyan #0891b2), complete typography and spacing system
- Design directions chosen:
  - Web: Split-Screen Companion (#2) + Card Gallery (#4)
  - Mobile: Card Gallery (#4) + Bottom Tab Navigation (#6)
- Chat implementation strategy (normalized data, inverted list patterns)
- Core UX principles and emotional goals (Empowered + Supported)

**Interactive Assets Already Created:**
- Color theme explorer: `/Users/reena/gauntletai/spendsense/docs/ux-color-themes.html`
- Design direction mockups: `/Users/reena/gauntletai/spendsense/docs/ux-design-directions.html`

**What Needs to be Done Next:**
I need to continue with Phase 2, starting with Section 8.1 Priority 1 from the specification document:

**Priority 1: User Journey Design**
Design the key user journeys for the end-user Dashboard + Chat interface:
1. Onboarding journey (consent → persona reveal → dashboard tour)
2. Signal exploration journey (click signal → view details → ask chat for explanation)
3. Recommendation flow (view recommendation → understand rationale → take action)
4. Chat interaction patterns (ask question → receive explanation → follow-up questions)

For each journey, I need:
- Step-by-step flow with screens/states
- Decision points and branching logic
- Error/edge cases and recovery paths
- Success states and next actions
- Mermaid diagrams showing the complete flow

**Design Constraints:**
- Must work on both web (desktop/tablet) and mobile
- Chat is always accessible (persistent sidebar on desktop, dedicated tab on mobile)
- Follow the "Empowered + Supported" emotional design principle
- Maintain non-judgmental, educational tone throughout
- Use Balanced Calm color theme and shadcn/ui components

**Target Users:**
End consumers using SpendSense through their financial institution. They want to:
- Understand their financial behavioral patterns (credit utilization, subscriptions, savings, income stability)
- Learn why they were assigned a specific persona
- Receive personalized educational recommendations
- Improve their financial habits without feeling judged

**Technical Context:**
- Backend API provides: personas, behavioral signals, recommendations with rationales
- Chat is AI-powered with contextual awareness (knows what user is viewing)
- All recommendations include "because" rationales citing specific data
- System enforces strict tone guardrails (no shaming language)

Please help me design these user journeys, documenting each flow with clear steps, decision points, and visual diagrams. Update the ux-design-specification.md document as we complete each journey.

Ready to start with the Onboarding Journey?
```

---

## 🎯 Alternative Shorter Prompt (If Context is Limited):

```
Resume UX design for SpendSense end-user interface.

**Phase 1 Complete:** Design system, visual foundation, design directions selected.
**Reference:** Read `/Users/reena/gauntletai/spendsense/docs/ux-design-specification.md`

**Next Task:** Design user journeys (Priority 1):
1. Onboarding journey
2. Signal exploration journey
3. Recommendation flow
4. Chat interaction patterns

Document each journey with step-by-step flows, decision points, error handling, and Mermaid diagrams. Use the "Empowered + Supported" design principle, Balanced Calm theme (#0891b2), and shadcn/ui components.

Ready to start with Onboarding Journey?
```

---

## 💡 Tips for Resuming:

1. **Start Fresh:** Open a new Claude Code session
2. **Copy Prompt:** Use the full prompt above for best results
3. **Reference Files:** The AI will read the specification document automatically
4. **Interactive:** Be ready to provide feedback on journey designs
5. **Iterate:** User journeys often need 2-3 rounds of refinement

---

## 📂 Files to Reference:

- **UX Specification:** `/Users/reena/gauntletai/spendsense/docs/ux-design-specification.md`
- **PRD:** `/Users/reena/gauntletai/spendsense/docs/prd.md`
- **Architecture:** `/Users/reena/gauntletai/spendsense/docs/architecture.md`
- **Color Themes:** `/Users/reena/gauntletai/spendsense/docs/ux-color-themes.html`
- **Design Mockups:** `/Users/reena/gauntletai/spendsense/docs/ux-design-directions.html`

---

## ✅ Expected Outcome:

After completing all user journeys, you'll have:
- Documented flows for all key user interactions
- Mermaid diagrams visualizing each journey
- Decision points and branching logic mapped
- Error handling and edge cases defined
- Updated ux-design-specification.md with Section 8 complete

Then proceed to Priority 2 (Component Library), Priority 3 (UX Patterns), Priority 4 (Responsive Strategy), and Priority 5 (Finalization).

---

**Last Updated:** November 3, 2025
**Phase:** 1 Complete, 2 In Progress
**Completion:** ~50%
