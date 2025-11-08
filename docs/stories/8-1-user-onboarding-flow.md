# Story 8.1: User Onboarding Flow

Status: drafted

## Story

As an **end user**,
I want **a guided onboarding experience that explains SpendSense, obtains my consent, reveals my persona, and orients me to the dashboard**,
so that **I understand how the system works, feel in control of my data, and know how to explore my financial patterns**.

## Acceptance Criteria

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

## Tasks / Subtasks

- [ ] Task 1: Create Welcome Screen component (AC: #1)
  - [ ] Create `frontend/src/components/onboarding/WelcomeScreen.tsx`
  - [ ] Implement headline "Welcome to SpendSense"
  - [ ] Add 3 value proposition icons and text
  - [ ] Add "Get Started" button (cyan #0891b2, primary style)
  - [ ] Add "Learn more" link that opens modal
  - [ ] Create "How It Works" modal component with dismissable overlay
  - [ ] Apply cyan-50 background and minimal clean layout
  - [ ] Make responsive for mobile (<768px) and desktop (≥1024px)
  - [ ] Test keyboard navigation (Tab, Enter)

- [ ] Task 2: Create Consent Screen component (AC: #2)
  - [ ] Create `frontend/src/components/onboarding/ConsentScreen.tsx`
  - [ ] Implement headline "Before we begin, here's what happens next"
  - [ ] Add transparent data usage explanation (180 days, patterns, persona, recs)
  - [ ] Create "What We DON'T Do" section with ❌ icon bullets
  - [ ] Create "Your Controls" section with ✅ icon bullets
  - [ ] Add consent checkbox (unchecked by default, properly labeled)
  - [ ] Add disclaimer text below checkbox (gray, readable)
  - [ ] Implement "I Consent & Continue" button (disabled state when unchecked)
  - [ ] Implement "Not Now" secondary button (gray style)
  - [ ] Wire button states to checkbox (enable on check, disable on uncheck)
  - [ ] Ensure 48x48px touch targets for mobile
  - [ ] Test keyboard navigation and screen reader compatibility

- [ ] Task 3: Implement consent backend integration (AC: #6)
  - [ ] Wire "I Consent & Continue" button to call `POST /api/consent`
  - [ ] Pass `user_id`, `consent_status: true`, `timestamp` in request body
  - [ ] Handle success response: store consent status in state
  - [ ] Handle error responses (e.g., user already consented)
  - [ ] Wire "Not Now" button to exit flow (redirect to bank dashboard placeholder)
  - [ ] Store user_id in localStorage/sessionStorage after consent
  - [ ] Add loading spinner during API call
  - [ ] Test with existing consent API endpoint

- [ ] Task 4: Create Processing/Loading Screen component (AC: #3)
  - [ ] Create `frontend/src/components/onboarding/ProcessingLoader.tsx`
  - [ ] Implement animated spinner (cyan accent color #06b6d4)
  - [ ] Create rotating status messages (2-3 sec intervals):
    - "Analyzing your transaction patterns..."
    - "Detecting behavioral signals..."
    - "Identifying your financial persona..."
    - "Generating personalized recommendations..."
  - [ ] Trigger `GET /api/profile/{user_id}` on mount
  - [ ] Show spinner for expected 5-10 seconds
  - [ ] Handle successful response: extract persona and recommendations
  - [ ] Transition to Persona Reveal on success

- [ ] Task 5: Implement error handling for Processing Screen (AC: #3, #7)
  - [ ] Detect insufficient data error (< 30 days history) from API response
  - [ ] Show error screen: "⚠️ We need at least 30 days of transaction history..."
  - [ ] Add recovery options: "Notify Me When Ready" | "Return to [Bank]"
  - [ ] Detect system errors (timeout, 500 errors) from API
  - [ ] Show error screen: "Something went wrong on our end..."
  - [ ] Add recovery options: "Try Again" | "Contact Support"
  - [ ] Wire "Try Again" to retry `GET /api/profile/{user_id}`
  - [ ] Test error scenarios with mock API responses
  - [ ] Add timeout handling (30 seconds max wait)

- [ ] Task 6: Create Persona Reveal Screen component (AC: #4)
  - [ ] Create `frontend/src/components/onboarding/PersonaReveal.tsx`
  - [ ] Display large persona icon/illustration (persona-specific)
  - [ ] Render headline: "Your Financial Persona: [Persona Name]"
  - [ ] Render persona description (from API response)
  - [ ] Create "Why This Persona" section with 2-3 signal citations from API
  - [ ] Mask account numbers (show last 4 digits only)
  - [ ] Create "What This Means" section with 3 educational focus areas
  - [ ] Add "Explore My Dashboard" CTA button (cyan primary)
  - [ ] Add "Learn about other personas" link
  - [ ] Create modal showing all 6 personas (dismissable)
  - [ ] Test persona-specific content for all 6 personas
  - [ ] Ensure non-judgmental, empowering tone in all copy

- [ ] Task 7: Create Dashboard Tour component (AC: #5)
  - [ ] Create `frontend/src/components/onboarding/DashboardTour.tsx`
  - [ ] Implement interactive tooltip system (5 steps):
    - Step 1 (5a): Tooltip pointing to Persona Card
    - Step 2 (5b): Tooltip pointing to Behavioral Signals section
    - Step 3 (5c): Tooltip pointing to Recommendations feed
    - Step 4 (5d): Tooltip pointing to Chat sidebar/tab + send greeting message
    - Step 5 (5e): Tooltip pointing to Settings icon
  - [ ] Add Next/Back buttons on each tooltip
  - [ ] Add progress indicator "Step X of 5" on each tooltip
  - [ ] Add "Skip Tour" link (always visible)
  - [ ] Add "Finish Tour" button on final step (5e)
  - [ ] Implement spotlight effect (highlighted element bright, rest dimmed 80%)
  - [ ] Wire tour completion to localStorage (don't show again)
  - [ ] Add "Restart Tour" option in Help menu
  - [ ] Test keyboard navigation through tour

- [ ] Task 8: Implement onboarding routing and navigation (AC: #6)
  - [ ] Create onboarding route structure:
    - `/onboarding/welcome` → WelcomeScreen
    - `/onboarding/consent` → ConsentScreen
    - `/onboarding/processing` → ProcessingLoader
    - `/onboarding/persona` → PersonaReveal
    - `/dashboard?tour=true` → Dashboard with tour overlay
  - [ ] Implement auto-navigation between steps:
    - Welcome → Consent (on "Get Started")
    - Consent → Processing (on "I Consent")
    - Processing → Persona Reveal (on success)
    - Persona Reveal → Dashboard Tour (on "Explore Dashboard")
  - [ ] Add returning user logic:
    - Check for existing consent on app load (`GET /api/consent/{user_id}`)
    - If has_consent=true, skip to /dashboard directly
    - Show toast: "Welcome back! [Persona Name]"
  - [ ] Test browser back button behavior
  - [ ] Test page refresh handling (restart flow if consent not granted)

- [ ] Task 9: Implement mobile responsive design (AC: #6)
  - [ ] Test all 5 onboarding screens on mobile (<768px):
    - Welcome: Vertical stack, full-width button
    - Consent: Scrollable, sticky CTA buttons at bottom
    - Processing: Centered (same as web)
    - Persona Reveal: Vertical stack, scrollable
    - Tour: Bottom sheet tooltips with upward arrows
  - [ ] Ensure 48x48px touch targets for all interactive elements
  - [ ] Test on iOS Safari and Android Chrome
  - [ ] Test landscape orientation
  - [ ] Verify swipe gestures don't conflict with tour navigation

- [ ] Task 10: Implement accessibility features (AC: #9)
  - [ ] Verify WCAG AA color contrast (≥4.5:1) for all text
  - [ ] Test full keyboard navigation (Tab, Enter, Esc):
    - Welcome → Consent → Processing → Persona → Tour
    - All buttons, links, checkboxes keyboard-accessible
  - [ ] Add ARIA labels for all interactive elements
  - [ ] Implement ARIA live regions for status announcements:
    - Processing status messages announced
    - Error messages announced
    - Persona reveal announced
  - [ ] Add focus indicators (cyan outline, visible)
  - [ ] Test with screen reader (VoiceOver/NVDA)
  - [ ] Add `prefers-reduced-motion` support (disable animations if set)
  - [ ] Verify proper heading hierarchy (h1 → h2 → h3)

- [ ] Task 11: Implement success metrics tracking (AC: #8)
  - [ ] Track consent rate:
    - Event: User reaches consent screen (Step 2)
    - Event: User clicks "I Consent" (success)
    - Event: User clicks "Not Now" (decline)
  - [ ] Track completion rate:
    - Event: User starts onboarding (Step 1)
    - Event: User completes tour (Step 5 done)
  - [ ] Track tour completion:
    - Event: Tour started (Step 5 begins)
    - Event: Tour completed (all 5 steps done)
    - Event: Tour skipped (clicked "Skip Tour")
  - [ ] Track time to dashboard:
    - Start timer on Step 1
    - End timer on Step 5 completion
  - [ ] Log all events to console (MVP) or analytics service
  - [ ] Create analytics utils module for event tracking

- [ ] Task 12: Add persona-specific content variations (AC: #4)
  - [ ] Create persona content config file with 6 persona variants:
    - High Utilization Manager: description, signals, focus areas
    - Variable Income Budgeter: description, signals, focus areas
    - Subscription-Heavy Spender: description, signals, focus areas
    - Savings Builder: description, signals, focus areas
    - Cash Flow Optimizer: description, signals, focus areas
    - Young Professional: description, signals, focus areas
  - [ ] Create persona icon/illustrations (6 unique icons)
  - [ ] Wire persona content to API response (persona_name field)
  - [ ] Test persona reveal with mock data for all 6 personas
  - [ ] Verify all copy is non-judgmental and empowering

- [ ] Task 13: Write comprehensive unit tests (AC: #1-10)
  - [ ] Create `frontend/src/components/onboarding/__tests__/WelcomeScreen.test.tsx`
  - [ ] Test welcome screen renders correctly
  - [ ] Test "Get Started" button navigation
  - [ ] Test "Learn more" modal opens and closes
  - [ ] Create `frontend/src/components/onboarding/__tests__/ConsentScreen.test.tsx`
  - [ ] Test checkbox enables "I Consent" button
  - [ ] Test "Not Now" button behavior
  - [ ] Test consent API integration (mock)
  - [ ] Create `frontend/src/components/onboarding/__tests__/ProcessingLoader.test.tsx`
  - [ ] Test rotating status messages
  - [ ] Test API call on mount
  - [ ] Test error handling (insufficient data, system error)
  - [ ] Create `frontend/src/components/onboarding/__tests__/PersonaReveal.test.tsx`
  - [ ] Test persona content rendering
  - [ ] Test signal citations with masked account numbers
  - [ ] Test "Explore Dashboard" navigation
  - [ ] Create `frontend/src/components/onboarding/__tests__/DashboardTour.test.tsx`
  - [ ] Test tour navigation (Next/Back)
  - [ ] Test "Skip Tour" functionality
  - [ ] Test tour completion tracking
  - [ ] Test keyboard navigation
  - [ ] Test accessibility (screen reader labels)

- [ ] Task 14: Integration testing and documentation (AC: #1-10)
  - [ ] Test full onboarding flow end-to-end:
    - Start at /onboarding/welcome
    - Complete all 5 steps
    - Verify consent API called
    - Verify profile API called
    - Verify landing on dashboard with tour
    - Verify tour completion tracked
  - [ ] Test returning user flow:
    - Mock existing consent
    - Verify skip to dashboard
    - Verify no tour shown
  - [ ] Test error scenarios:
    - Insufficient data error → recovery path
    - System error → retry works
  - [ ] Test mobile responsiveness (all breakpoints)
  - [ ] Test accessibility compliance (full keyboard nav + screen reader)
  - [ ] Document onboarding flow in component README
  - [ ] Create Storybook stories for all 5 screens (optional)

## Dev Notes

### Architecture Patterns and Constraints

**From Epic 8 PRD:**
- Frontend: React 18 + TypeScript
- Build: Vite for dev server
- Styling: TailwindCSS with "Balanced Calm" theme (cyan #0891b2 primary)
- Routing: React Router
- Data fetching: React Query for API caching
- State: React Context or Zustand for UI state

**From UX Journey 1:**
- 5-step flow: Welcome → Consent → Processing → Persona → Tour
- Consent: Explicit opt-in (unchecked by default)
- Processing: 5-10 second expected duration
- Persona Reveal: Transparent rationale with specific signal citations
- Tour: 5 interactive tooltips with skip option
- Error handling: Insufficient data (<30 days) and system errors
- Returning users: Skip directly to dashboard if already consented

**Backend APIs Available:**
- `POST /api/consent` - Record user consent
- `GET /api/consent/{user_id}` - Check consent status
- `GET /api/profile/{user_id}` - Get persona, signals, recommendations (triggers processing)

**Key Requirements:**
- WCAG AA accessibility compliance
- Mobile-first responsive design (breakpoints: 768px, 1024px)
- Keyboard navigation for all interactions
- Screen reader support with ARIA labels
- Non-judgmental, empowering tone in all copy
- Specific data citations (masked account numbers)
- Success metrics tracking (consent rate, completion rate, tour rate, time)

### Project Structure Notes

**New Files to Create:**
- `frontend/src/components/onboarding/WelcomeScreen.tsx` - Step 1 component
- `frontend/src/components/onboarding/ConsentScreen.tsx` - Step 2 component
- `frontend/src/components/onboarding/ProcessingLoader.tsx` - Step 3 component
- `frontend/src/components/onboarding/PersonaReveal.tsx` - Step 4 component
- `frontend/src/components/onboarding/DashboardTour.tsx` - Step 5 component
- `frontend/src/components/onboarding/HowItWorksModal.tsx` - Welcome modal
- `frontend/src/components/onboarding/AllPersonasModal.tsx` - Persona comparison modal
- `frontend/src/config/personaContent.ts` - Persona-specific copy (6 variants)
- `frontend/src/utils/analytics.ts` - Event tracking utilities
- `frontend/src/routes/OnboardingRoutes.tsx` - Onboarding routing
- `frontend/src/components/onboarding/__tests__/` - Test files for all components
- `frontend/src/hooks/useOnboarding.ts` - Onboarding state management hook
- `frontend/src/hooks/useConsent.ts` - Consent API integration hook

**Files to Reference:**
- Existing operator dashboard frontend code for patterns (React + TypeScript + Tailwind)
- `spendsense/api/main.py` - Backend API endpoints
- `docs/ux/ux-journey-1-onboarding.md` - Complete UX specification
- `docs/ux/ux-design-specification.md` - Design system (colors, typography, spacing)
- `docs/prd/epic-8-end-user-dashboard-experience.md` - PRD with acceptance criteria

**Dependencies:**
- React Router (routing)
- React Query (API data fetching)
- TailwindCSS (styling)
- Intro.js / React Joyride / Driver.js (tour library, or custom implementation)
- @testing-library/react (testing)
- @testing-library/jest-dom (test assertions)
- axios or fetch (HTTP requests)

### Testing Standards Summary

**From Epic 8 PRD:**
- Test framework: Vitest or Jest with React Testing Library
- Coverage target: ≥10 tests per story
- Test types:
  1. Unit tests: Component rendering and behavior
  2. Integration tests: API calls and navigation
  3. Accessibility tests: Keyboard nav + screen reader
  4. Responsive tests: Mobile and desktop layouts

**Test Categories:**
1. Welcome Screen: Rendering, navigation, modal
2. Consent Screen: Checkbox state, button enabling, API call
3. Processing Screen: Loading states, error handling, API integration
4. Persona Reveal: Content rendering, persona variations
5. Dashboard Tour: Tooltip navigation, skip/complete, localStorage
6. Routing: Navigation between steps, returning user logic
7. Accessibility: Keyboard nav, ARIA labels, screen reader
8. Responsive: Mobile (<768px), tablet (768-1023px), desktop (≥1024px)

### Learnings from Previous Story

**From Story 7.6 (Evaluation Report Generation):**
- This story was in Epic 7 (Evaluation), not frontend work
- Epic 7 focused on backend evaluation metrics
- No direct frontend patterns to reuse

**From Epic 6 (Operator Dashboard):**
- Epic 6 built an operator-facing React dashboard
- Used React + TypeScript + TailwindCSS stack
- Established component patterns and API integration with React Query
- Created auth/routing patterns
- Stories 6.1-6.6 implemented operator features (not end-user features)

**From Epic 5 (Guardrails):**
- Consent management backend built in Story 5.1
- `POST /api/consent` endpoint available
- `GET /api/consent/{user_id}` endpoint available
- Consent data model includes: user_id, consent_status, timestamp

**Integration Points:**
- Consent API (Epic 5) - backend ready, frontend needs to integrate
- Profile API (Epic 3) - persona assignment backend ready
- Recommendation API (Epic 4) - recommendations backend ready
- Operator dashboard (Epic 6) - provides React/Tailwind patterns to follow

**Technical Patterns to Follow:**
- Use React Query for API calls (as established in Epic 6)
- Use TailwindCSS for styling (consistent with operator dashboard)
- Use TypeScript with strict types
- Use React Router for routing
- Use component composition (small, focused components)
- Use custom hooks for reusable logic (useConsent, useOnboarding)

**First Story in Epic 8:**
- No previous end-user frontend stories
- This is the foundation for all subsequent Epic 8 stories
- Establish component patterns that Stories 8.2-8.6 will follow
- Create routing structure that Stories 8.2-8.6 will extend

### References

- [Source: docs/prd/epic-8-end-user-dashboard-experience.md#Story-8.1] - Story 8.1 acceptance criteria
- [Source: docs/ux/ux-journey-1-onboarding.md] - Complete onboarding UX specification
- [Source: docs/ux/ux-design-specification.md] - Design system (colors, typography, spacing)
- [Source: docs/architecture.md] - Frontend tech stack
- [Source: spendsense/api/main.py] - Backend API endpoints
- [Source: docs/stories/5-1-consent-management-system.md] - Consent API specification
- [Source: docs/stories/3-2-persona-matching-engine.md] - Persona assignment logic
- [Source: docs/stories/4-1-educational-content-catalog.md] - Recommendations structure

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

<!-- Will be filled in by dev agent -->

### Debug Log References

<!-- Will be filled in by dev agent -->

### Completion Notes List

<!-- Will be filled in by dev agent during implementation -->

### File List

<!-- Will be filled in by dev agent:
NEW: List new files created
MODIFIED: List files modified
DELETED: List files deleted (if any)
-->

## Change Log

**2025-11-07 - v1.0 - Story Drafted**
- Initial story creation from Epic 8 PRD
- Epic 8.1: First story in end-user dashboard epic (onboarding flow)
- 14 task groups with 80+ subtasks
- Comprehensive onboarding flow: Welcome → Consent → Processing → Persona → Tour
- 5 main UI components built (WelcomeScreen, ConsentScreen, ProcessingLoader, PersonaReveal, DashboardTour)
- Backend integration: Consent API and Profile API
- Persona-specific content for all 6 personas
- Full accessibility compliance (WCAG AA, keyboard nav, screen reader)
- Mobile-first responsive design (breakpoints: 768px, 1024px)
- Success metrics tracking (consent rate, completion rate, tour rate, time)
- Error handling for insufficient data and system errors
- Returning user logic (skip onboarding if already consented)
- Interactive dashboard tour with 5 tooltips and skip option
- Status: drafted (ready for story-context workflow)
