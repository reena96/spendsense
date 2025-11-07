# Epic 8: End-User Dashboard & Experience

**Goal:** Build consumer-facing dashboard and chat interface that enables end users (bank customers) to explore their financial behavioral patterns, understand their persona assignment, receive personalized educational recommendations, and interact with an AI coach for guidance. Implement complete user journeys from onboarding through ongoing engagement.

**Context:** This epic implements the end-user experience designed in `docs/ux/ux-journey-*.md` files. It leverages existing backend APIs from Epics 1-5 (profiles, signals, personas, recommendations, guardrails) and provides a consumer-friendly interface distinct from the operator dashboard (Epic 6).

**Dependencies:**
- Epic 1 (Data Foundation) ✅ Complete
- Epic 2 (Behavioral Signals) ✅ Complete
- Epic 3 (Persona Assignment) ✅ Complete
- Epic 4 (Recommendations) ✅ Complete (Stories 4.1-4.3)
- Epic 5 (Guardrails) ✅ Complete
- Backend APIs: All required endpoints already exist

**Backend APIs Available (No New Backend Work Required):**
- `GET /api/profile/{user_id}` - Persona with rationale
- `GET /api/signals/{user_id}` - All behavioral signals (30d/180d)
- `GET /api/signals/{user_id}/{signal_type}` - Specific signal details
- `GET /api/recommendations/{user_id}` - Personalized recommendations
- `POST /api/consent` - User consent management
- `GET /api/consent/{user_id}` - Consent status

---

## Story 8.1: User Onboarding Flow

**UX Reference:** `docs/ux/ux-journey-1-onboarding.md`

As an **end user**,
I want **a guided onboarding experience that explains SpendSense, obtains my consent, reveals my persona, and orients me to the dashboard**,
so that **I understand how the system works, feel in control of my data, and know how to explore my financial patterns**.

### Acceptance Criteria

1. **Welcome Screen (Step 1)**
   - Headline: "Welcome to SpendSense"
   - 3 value propositions with icons (📊 patterns, 💡 education, 🔒 control)
   - "Get Started" CTA button (cyan #0891b2)
   - "Learn more" link opens modal with detailed explanation
   - Cyan-50 background, clean minimal layout

2. **Consent Screen (Step 2)**
   - Headline: "Before we begin, here's what happens next"
   - Transparent data usage explanation (180 days, patterns, persona, 3-5 recs)
   - "What We DON'T Do" section with ❌ bullets
   - "Your Controls" section with ✅ bullets
   - Consent checkbox (unchecked by default)
   - Disclaimer text: "This is educational content, not financial advice..."
   - "I Consent & Continue" button (disabled until checked)
   - "Not Now" secondary button

3. **Processing State (Step 3)**
   - Loading animation with progress indicator
   - Rotating status messages: "Analyzing transactions...", "Detecting signals...", "Identifying persona...", "Generating recommendations..."
   - Expected duration: 5-10 seconds
   - Error handling for insufficient data (< 30 days history)
   - Error handling for system errors with "Try Again" option

4. **Persona Reveal Screen (Step 4)**
   - Large persona icon/illustration
   - Headline: "Your Financial Persona: [Persona Name]"
   - Persona description (non-judgmental, empowering)
   - "Why This Persona" section with 2-3 specific signal citations
   - "What This Means" section with 3 educational focus areas
   - "Explore My Dashboard" CTA button
   - "Learn about other personas" link opens modal

5. **Dashboard Tour (Step 5)**
   - Interactive walkthrough with 5 tooltips:
     - 5a: Persona card overview
     - 5b: Behavioral signals section
     - 5c: Recommendations feed
     - 5d: Chat assistant introduction
     - 5e: Settings & controls
   - Next/Back buttons on each tooltip
   - Progress indicator "Step X of 5"
   - "Skip Tour" option available
   - "Finish Tour" completes and dismisses tour
   - Tour can be restarted from Help menu

6. **Integration Requirements**
   - Calls `POST /api/consent` on consent granted
   - Calls `GET /api/profile/{user_id}` for persona assignment
   - Stores user_id in session/localStorage for subsequent views
   - Responsive design: same flow on web and mobile

7. **Error Handling**
   - Returning users (already consented) skip to dashboard directly
   - Insufficient data error shows clear message with recovery path
   - System errors provide "Try Again" and "Contact Support" options
   - Browser close during onboarding clears partial state

8. **Success Metrics Tracked**
   - Consent rate (% completing Step 2)
   - Completion rate (% reaching dashboard)
   - Tour completion rate (% finishing all 5 steps)
   - Average time to dashboard

9. **Accessibility**
   - WCAG AA color contrast
   - Keyboard navigation for all interactive elements
   - Screen reader announcements for state changes
   - 48px minimum touch targets (mobile)

10. **UI Components Built**
    - `<WelcomeScreen />` component
    - `<ConsentModal />` component
    - `<ProcessingLoader />` component
    - `<PersonaReveal />` component
    - `<DashboardTour />` component with tooltip system

---

## Story 8.2: Dashboard Layout & Navigation

**UX Reference:** `docs/ux/ux-design-specification.md` (Sections 3.2, 3.3)

As an **end user**,
I want **a clear, intuitive dashboard layout that adapts to my device and provides easy navigation between sections**,
so that **I can explore my financial data comfortably on any device**.

### Acceptance Criteria

1. **Desktop Layout (≥1024px) - Split-Screen Companion**
   - 60/40 split layout (dashboard left, chat sidebar right)
   - Dashboard content scrolls independently
   - Chat sidebar persistent and always visible
   - Header: SpendSense logo, user name, settings icon
   - Main sections: Persona card, signals grid, recommendations feed

2. **Tablet Layout (768-1023px)**
   - Chat collapses to floating widget (bottom-right corner)
   - Dashboard takes full width
   - Floating chat button with notification badge
   - Click opens chat as bottom sheet overlay

3. **Mobile Layout (<768px) - Bottom Tab Navigation**
   - Bottom navigation bar with 5 tabs:
     - 📊 Dashboard (overview + persona)
     - 📈 Signals (behavioral data)
     - 💡 Tips (recommendations)
     - 💬 Chat (AI coach)
     - ⚙️ More (settings/profile)
   - Fixed bottom position (doesn't scroll)
   - Active tab indicator (cyan fill + icon)
   - 48px minimum touch target size

4. **Persona Card Component**
   - Displays: Persona name, icon, time window toggle
   - "View Details" button opens modal with full rationale
   - Shows primary metric (e.g., "68% utilization" for High Utilization)
   - Visual indicator: color-coded badge (green/yellow/red)

5. **Time Window Toggle**
   - Pill selector: "30-Day View" | "180-Day View" | "Compare Both"
   - Active state: cyan background
   - Updates all dashboard sections when toggled
   - Preference saved to localStorage

6. **Navigation**
   - All sections accessible within 3 clicks (UX requirement)
   - Breadcrumb trail for deep views (Signal > Credit Utilization > Details)
   - Back navigation preserves context and scroll position

7. **Page Layouts**
   - Dashboard (home): Persona card + 4 signal cards + recommendations
   - Signal Detail: Full-screen or modal with back button
   - Recommendation Detail: Full-screen or modal
   - Chat: Sidebar (web) or full-screen tab (mobile)
   - Settings: Full-screen page

8. **Responsive Behavior**
   - Breakpoints: 768px (mobile), 1024px (desktop)
   - Signal cards: 2x2 grid (desktop), vertical stack (mobile)
   - Recommendation cards: 2 columns (desktop), 1 column (mobile)
   - All text scales appropriately

9. **Visual Consistency**
   - Uses "Balanced Calm" color theme (cyan #0891b2 primary)
   - 8px spacing grid throughout
   - Border radius: 8px for cards, 6px for buttons
   - Shadows: md for cards (0 4px 6px rgba(0,0,0,0.07))
   - Typography: System font stack, 16px body text

10. **UI Components Built**
    - `<DashboardLayout />` wrapper with responsive logic
    - `<PersonaCard />` component
    - `<TimeWindowToggle />` component
    - `<BottomTabNavigation />` (mobile)
    - `<Header />` component
    - `<FloatingChatButton />` (tablet)

---

## Story 8.3: Signal Exploration UI

**UX Reference:** `docs/ux/ux-journey-2-signal-exploration.md`

As an **end user**,
I want **to click on any behavioral signal card to see detailed breakdowns, trends, and explanations**,
so that **I can deeply understand my financial patterns and what drives my persona assignment**.

### Acceptance Criteria

1. **Signal Cards (Dashboard View)**
   - 4 signal card types:
     - Credit Utilization: Shows % utilization, color-coded progress bar
     - Subscription Spending: Shows count + monthly cost
     - Savings Pattern: Shows months of coverage, progress to 6-month goal
     - Income Stability: Shows status badge + pattern
   - Each card: Icon, title, summary metric, status badge, clickable
   - Hover state: card elevates slightly (shadow lg)
   - Click transitions to detail view

2. **Signal Detail View - Credit Utilization**
   - Header: Back button, title "Credit Utilization Details", time window toggle
   - Key metrics section:
     - Current balance, credit limit, utilization %, comparison to last period
     - Per-card breakdown with color-coded bars
   - Trend visualization: Line chart showing utilization over time
   - "What This Means" explanation in plain language (grade-8)
   - Related recommendations callout box with links
   - "Ask Chat About This" CTA button

3. **Signal Detail View - Subscriptions**
   - Key metrics: Active count, monthly cost, % of income
   - Subscription list with logos (Netflix, Spotify, etc.)
   - Trend chart: Subscription cost over time
   - Overlap detection: "Netflix + Hulu — consolidate?"
   - Related recommendations: Subscription audit checklist

4. **Signal Detail View - Savings**
   - Key metrics: Current savings, monthly income, months covered
   - Goal progress bar (current vs. 6-month goal)
   - Trend chart: Savings growth over time
   - Interest calculation: "High-yield savings could earn $X more/year"
   - Related recommendations: Emergency fund guide

5. **Signal Detail View - Income**
   - Key metrics: Average monthly income, pattern (biweekly, irregular, etc.)
   - Stability score badge
   - Recent deposit list with dates and amounts
   - Variability indicator (consistent vs. variable)
   - Related recommendations: Budget templates for income pattern

6. **Time Window Comparison**
   - Toggle updates all charts and metrics
   - 30-day: Recent behavior, actionable insights
   - 180-day: Long-term trends, context
   - Comparison metric: "↑ 12% vs. last month" with trend arrow

7. **Interactive Elements**
   - "View Related Recommendations" button filters rec feed
   - "Ask Chat About This" button opens chat with context pre-loaded
   - Charts are interactive: hover shows exact values
   - Click chart data points for drill-down (if time allows)

8. **Backend Integration**
   - Calls `GET /api/signals/{user_id}` for overview
   - Calls `GET /api/signals/{user_id}/credit` for credit detail
   - Calls `GET /api/signals/{user_id}/subscriptions` for subscriptions
   - Calls `GET /api/signals/{user_id}/savings` for savings
   - Calls `GET /api/signals/{user_id}/income` for income

9. **Error Handling**
   - No data for signal: "Not enough data yet. Check back after more transactions."
   - Stale data (>7 days): Warning banner with "Refresh Now" button
   - Insufficient history for 180-day: Disable toggle with tooltip

10. **UI Components Built**
    - `<SignalCard />` component (4 variants)
    - `<SignalDetailModal />` or `<SignalDetailPage />`
    - `<TrendChart />` component (reusable line/bar chart)
    - `<RelatedRecommendations />` callout box
    - `<MetricComparison />` component (with trend arrows)

---

## Story 8.4: Recommendation Feed UI

**UX Reference:** `docs/ux/ux-journey-3-recommendation-flow.md`

As an **end user**,
I want **to browse personalized educational recommendations with clear rationales and take actions like reading, downloading, or exploring partner offers**,
so that **I can learn strategies to improve my financial behavior based on my specific data**.

### Acceptance Criteria

1. **Recommendations Feed (Dashboard View)**
   - Section header: "Your Personalized Recommendations"
   - Filter tabs: "All" | "Education" | "Tools" | "Partner Offers"
   - Card layout: 2 columns (desktop), 1 column (mobile)
   - Each card shows: Icon, title, type badge, short description, CTA button

2. **Recommendation Card Types**
   - **Educational Content**: Articles, guides, templates
     - Badge: "Article" | "Guide" | "Template" | "Calculator"
     - CTA: "Read Guide" or "Download Template"
   - **Partner Offers**: Savings accounts, credit cards, apps
     - Badge: "Partner Offer" + eligibility indicator
     - CTA: "Learn More" (opens detail view)
     - Savings estimate: "Save up to $X/year"

3. **Recommendation Detail View**
   - Full recommendation content or offer details
   - "Why You're Seeing This" section with transparent rationale:
     - "We noticed your Visa ****4523 is at 68% utilization..."
     - Cites specific data signals with masked account numbers
   - For educational content: Full article/guide text or downloadable PDF
   - For partner offers:
     - Eligibility checks passed (checkmarks)
     - Potential savings calculation (data-driven)
     - External link warning: "Leaving SpendSense to explore offer"
     - Disclaimer: "This is not financial advice..."

4. **Rationale Transparency**
   - Every recommendation includes "because" statement
   - Specific data citations: amounts, percentages, account numbers (masked)
   - Plain language (grade-8 readability)
   - Example: "Your 7 subscriptions total $124/month (3.2% of income). This guide helps identify overlap and potential savings of $20-40/month."

5. **Action Buttons**
   - Educational: "Read Guide", "Download Template", "Use Calculator"
   - Partner offers: "Learn More", "See Details"
   - "Ask Chat About This" button on every detail view
   - "This isn't relevant" feedback button (optional)

6. **Filtering and Sorting**
   - Filter by type: All, Education, Tools, Partner Offers
   - Sort by: Relevance (default), Newest, Most Helpful
   - Search bar: Find recommendations by keyword

7. **Feedback Mechanism**
   - Thumbs up/down on each recommendation
   - "Why wasn't this helpful?" dropdown on thumbs down
   - Feedback stored but doesn't remove recommendation immediately

8. **Backend Integration**
   - Calls `GET /api/recommendations/{user_id}` for personalized feed
   - Response includes: Educational items (3-5), partner offers (1-3)
   - Each recommendation includes rationale with signal values

9. **Guardrails Enforcement**
   - All recommendations passed eligibility checks (backend)
   - All rationales validated for tone (non-judgmental, empowering)
   - All partner offers include disclaimer
   - No predatory products shown

10. **UI Components Built**
    - `<RecommendationCard />` component (multiple variants)
    - `<RecommendationDetail />` modal or page
    - `<RationaleSection />` component
    - `<PartnerOfferDetail />` component
    - `<ExternalLinkWarning />` modal
    - `<FeedbackButton />` component

---

## Story 8.5: Chat Interface

**UX Reference:** `docs/ux/ux-journey-4-chat-interaction.md`

As an **end user**,
I want **to ask questions about my financial patterns and get context-aware, plain-language explanations from an AI coach**,
so that **I can understand my data, explore strategies, and get guidance without feeling judged**.

### Acceptance Criteria

1. **Chat UI Layout - Web (≥1024px)**
   - Persistent sidebar (40% width, right side)
   - Header: "SpendSense Coach" + online status indicator (●)
   - Message area: Scrollable, inverted list (newest at bottom)
   - Input field: "Type a message..." with send button (→)
   - Settings icon: Clear conversation, toggle notifications

2. **Chat UI Layout - Mobile (<768px)**
   - Dedicated tab in bottom navigation (💬)
   - Full-screen when active
   - Header: "SpendSense Coach" + back button
   - Notification badge on tab icon when unread messages

3. **Initial State (First Use)**
   - Welcome message: "Hi! I'm your SpendSense coach..."
   - Quick start buttons (4 options):
     - "Explain my persona"
     - "Why is my utilization high?"
     - "How can I save more?"
     - "What are these signals?"

4. **Conversation Patterns (5 Types)**
   - **Pattern 1: Persona Explanation**
     - Responds with persona name, specific data citations, educational focus
     - Quick replies: "Show recommendations", "How do I improve?", "Why does X matter?"
   - **Pattern 2: Signal Exploration**
     - Responds with breakdown, explanation, actionable insight
     - Quick replies: "Yes, show strategies", "How long would that take?", "View breakdown"
   - **Pattern 3: Recommendation Clarification**
     - Responds with pros/cons, user-specific analysis, "My Take" guidance
     - Quick replies: "Show calculator", "What are risks?", "Show alternatives"
   - **Pattern 4: How-To / Educational**
     - Responds with multiple opportunities, calculations, prioritization
     - Quick replies: "Review subscriptions", "Set up auto-savings", "See strategies"
   - **Pattern 5: Comparison / What-If**
     - Responds with side-by-side analysis, pros/cons, hybrid suggestions
     - Quick replies: "Show calculator", "How do I X?", "What's better?"

5. **Context Awareness**
   - Chat knows what screen user is viewing (signal, recommendation, etc.)
   - Pre-loads context when "Ask Chat About This" clicked
   - Remembers conversation history (previous questions)
   - Can reference specific user data (persona, signal values, accounts)

6. **Message Features**
   - User messages: Right-aligned, cyan background bubble
   - AI responses: Left-aligned, white background bubble
   - Typing indicator: Animated dots "●●●" while processing
   - Timestamps on older messages ("2 hours ago", "Yesterday")
   - Quick reply buttons: Up to 4 buttons per response

7. **Rich Content in Chat**
   - Embedded cards: Signal summaries, recommendation previews
   - Inline charts: Simple visualizations
   - Actionable links: "View this signal", "See recommendation", "Use calculator"
   - Color-coded indicators: 🔴 red (needs attention), 🟢 green (good), 🟡 yellow (watch)

8. **Guardrails Enforcement**
   - Won't provide regulated financial advice
   - Responds to inappropriate questions: "I can't provide investment advice..."
   - Out-of-scope questions: "I'm focused on financial data..."
   - Non-judgmental tone always maintained

9. **Backend Integration**
   - Calls `POST /api/chat/message` with user message + context
   - Context includes: current screen, user_id, persona, recent signals
   - Response includes: AI message text, optional quick reply buttons, rich content
   - Calls `GET /api/chat/history/{user_id}` to load previous conversations

10. **UI Components Built**
    - `<ChatSidebar />` (web) or `<ChatTab />` (mobile)
    - `<ChatMessage />` component (user/AI variants)
    - `<QuickReplyButtons />` component
    - `<TypingIndicator />` component
    - `<ChatInputField />` component
    - `<RichContentCard />` for embedded content

**Note:** This story requires new backend implementation:
- `POST /api/chat/message` endpoint (LLM integration)
- `GET /api/chat/history/{user_id}` endpoint (message persistence)
- Chat context management (track what user is viewing)
- LLM prompt engineering with guardrails

---

## Story 8.6: Settings & Consent Management UI

**UX Reference:** `docs/ux/ux-design-specification.md`, `docs/stories/5-1-consent-management-system.md`

As an **end user**,
I want **to manage my consent preferences, adjust settings, and understand my data controls**,
so that **I feel empowered and in control of my financial data**.

### Acceptance Criteria

1. **Settings Page Layout**
   - Header: "Settings" with back button
   - Sections:
     - Account & Privacy
     - Data & Consent
     - Preferences
     - Help & Support
     - About SpendSense

2. **Account & Privacy Section**
   - User name display
   - Persona badge display
   - "View My Data" button (shows what data is stored)
   - "Download My Data" button (export JSON)

3. **Data & Consent Section**
   - Consent status: "Active since [date]" or "Not granted"
   - "What data do we use?" expandable section
   - "Revoke Consent" button (red, destructive action)
   - Confirmation modal on revoke: "This will stop all processing. Continue?"
   - On revoke: Returns to welcome screen, clears stored data

4. **Preferences Section**
   - Default time window: Radio buttons for 30-day | 180-day | Both
   - Notification preferences: Toggle for email updates (if enabled)
   - Theme preference: Light | Dark (future enhancement, not required for MVP)

5. **Help & Support Section**
   - "Restart Dashboard Tour" button (re-launches Step 5 tour)
   - "Frequently Asked Questions" link
   - "Contact Support" link (mailto or support form)
   - "Privacy Policy" link
   - "Terms of Service" link

6. **About SpendSense Section**
   - Version number
   - "How SpendSense Works" link (opens modal)
   - "All Personas Explained" link (shows 6 personas)
   - Credits and acknowledgments

7. **Consent Revocation Flow**
   - Click "Revoke Consent" → Confirmation modal
   - Modal: "Are you sure? This will:
     - Stop all data processing
     - Delete your persona and recommendations
     - Return you to the welcome screen
     - You can opt back in anytime"
   - "Yes, Revoke Consent" | "Cancel" buttons
   - On confirm: Calls `POST /api/consent` with revoke action
   - Redirects to welcome screen with message: "Consent revoked. You can opt back in anytime."

8. **Data Download**
   - Click "Download My Data" → Generates JSON export
   - Includes: Profile, signals, persona assignment, recommendations, consent history
   - Downloads as `spendsense_data_{user_id}_{timestamp}.json`
   - User-friendly format with explanatory comments

9. **Backend Integration**
   - Calls `GET /api/consent/{user_id}` for consent status
   - Calls `POST /api/consent` for revoke action
   - Calls `GET /api/profile/{user_id}` for data export
   - Calls `GET /api/signals/{user_id}` for data export
   - Calls `GET /api/recommendations/{user_id}` for data export

10. **UI Components Built**
    - `<SettingsPage />` component
    - `<ConsentSection />` component
    - `<RevokeConsentModal />` confirmation dialog
    - `<DataExport />` component
    - `<PreferencesForm />` component

---

## Epic 8 Success Metrics

**Engagement Metrics:**
- % of users who complete onboarding (goal: >80%)
- Average time to first interaction (goal: <2 minutes from welcome)
- % of users who explore at least 1 signal detail (goal: >60%)
- % of users who view at least 1 recommendation detail (goal: >50%)
- % of users who interact with chat (goal: >40%)

**User Satisfaction:**
- Thumbs up rate on recommendations (goal: >70%)
- Tour completion rate (goal: >50%)
- Chat conversation length (average turns, goal: 3-5)
- Consent revocation rate (track, goal: <5%)

**Technical Performance:**
- Page load time: <2 seconds for dashboard
- API response time: <500ms for signals/recommendations
- Chat response time: <3 seconds for AI messages
- Mobile responsiveness: Works smoothly on iOS/Android

**Accessibility:**
- WCAG AA compliance: 100% of interactive elements
- Keyboard navigation: All features accessible
- Screen reader compatibility: Full support

---

## Technical Implementation Notes

### Frontend Stack (Already Defined)
- React 18 + TypeScript
- Vite for build/dev server
- TailwindCSS for styling (with "Balanced Calm" theme)
- React Router for navigation
- React Query for data fetching/caching
- Chart library: Recharts or Chart.js for visualizations

### Backend APIs (Mostly Exist)
✅ **Already Built:**
- `GET /api/profile/{user_id}` - Persona assignment
- `GET /api/signals/{user_id}` - All signals
- `GET /api/signals/{user_id}/{type}` - Specific signal
- `GET /api/recommendations/{user_id}` - Recommendations
- `POST /api/consent` - Consent management
- `GET /api/consent/{user_id}` - Consent status

❌ **New Backend Needed (Story 8.5 only):**
- `POST /api/chat/message` - LLM-powered chat responses
- `GET /api/chat/history/{user_id}` - Chat message history

### Responsive Design Strategy
- **Mobile-first approach**: Design for mobile, enhance for desktop
- **Breakpoints**: 768px (mobile/tablet), 1024px (tablet/desktop)
- **Touch targets**: 48x48px minimum on mobile
- **Viewport meta tag**: `<meta name="viewport" content="width=device-width, initial-scale=1">`

### Authentication/Session Management
- User ID stored in localStorage or sessionStorage
- No login required for MVP (users identified by user_id from bank)
- Future: OAuth integration with financial institution SSO

### State Management
- React Query for server state (profiles, signals, recommendations)
- React Context or Zustand for UI state (time window toggle, tour progress)
- localStorage for user preferences

---

## Dependencies and Sequencing

**Recommended Story Order:**
1. **Story 8.1** (Onboarding) - Gets users in the door
2. **Story 8.2** (Dashboard Layout) - Shows data
3. **Story 8.3** (Signal Exploration) - Enables drill-down
4. **Story 8.4** (Recommendations) - Delivers core value
5. **Story 8.6** (Settings/Consent) - User controls
6. **Story 8.5** (Chat) - Requires new backend, can be done last or parallel

**Parallel Work Opportunities:**
- Stories 8.3, 8.4, 8.6 can be developed in parallel after 8.2 is complete
- Story 8.5 requires backend work, can be separate workstream

**Estimated Effort:**
- Story 8.1: 1-2 weeks (5 screens + flows)
- Story 8.2: 1 week (layout system + navigation)
- Story 8.3: 2 weeks (4 signal types + charts)
- Story 8.4: 1-2 weeks (feed + detail views)
- Story 8.5: 2-3 weeks (chat UI + backend integration + LLM)
- Story 8.6: 1 week (settings + consent management)

**Total Epic 8 Estimate:** 8-11 weeks for full-stack team

---

## Alignment with Existing Implementation

**Backend (Already Built):**
- ✅ Epic 1: Synthetic data generation (50-100 users with realistic data)
- ✅ Epic 2: Behavioral signal detection (subscriptions, savings, credit, income)
- ✅ Epic 3: Persona assignment (6 personas with audit logs)
- ✅ Epic 4: Recommendation engine (educational content + partner offers)
- ✅ Epic 5: Guardrails (consent, eligibility, tone validation)
- ✅ Epic 6: Operator dashboard (separate interface for staff)

**Frontend (Partially Built):**
- ✅ Operator UI exists (React + TypeScript + TailwindCSS)
- ✅ Component patterns established
- ✅ API integration patterns established (React Query)
- ❌ End-user UI does not exist (Epic 8 builds this)

**Design System:**
- ✅ Fully specified in `docs/ux/ux-design-specification.md`
- ✅ "Balanced Calm" theme (cyan #0891b2 primary)
- ✅ Typography, spacing, shadows, borders defined
- ✅ Component patterns defined in UX journeys

**Key Difference:**
- **Epic 6** = Operator dashboard (for bank staff to review users)
- **Epic 8** = End-user dashboard (for consumers to explore their own data)

Both use the same backend APIs, but serve different audiences with different UX patterns.

---

## Related Documentation

- **UX Journeys:**
  - `docs/ux/ux-journey-1-onboarding.md` (Story 8.1 reference)
  - `docs/ux/ux-journey-2-signal-exploration.md` (Story 8.3 reference)
  - `docs/ux/ux-journey-3-recommendation-flow.md` (Story 8.4 reference)
  - `docs/ux/ux-journey-4-chat-interaction.md` (Story 8.5 reference)

- **Design System:**
  - `docs/ux/ux-design-specification.md` (Complete visual foundation)
  - `docs/ux-color-themes.html` (Interactive theme explorer)
  - `docs/ux-design-directions.html` (Layout mockups)

- **Backend APIs:**
  - `spendsense/api/main.py` (API endpoints)
  - `docs/architecture.md` (System architecture)

- **Related Epics:**
  - `docs/prd/epic-5-consent-eligibility-tone-guardrails.md` (Consent management)
  - `docs/prd/epic-6-operator-view-oversight-interface.md` (Operator dashboard reference)
