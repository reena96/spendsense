export interface PersonaContent {
  name: string;
  description: string;
  icon: string;
  focusAreas: string[];
  color: string;
}

export const PERSONA_CONTENT: Record<string, PersonaContent> = {
  'high_utilization_manager': {
    name: 'High Utilization Manager',
    description: "You're actively using credit and could benefit from strategies to optimize utilization and reduce interest costs.",
    icon: '💳',
    focusAreas: [
      'Credit utilization optimization strategies',
      'Debt paydown calculators and timelines',
      'Interest reduction techniques'
    ],
    color: 'orange'
  },
  'variable_income_budgeter': {
    name: 'Variable Income Budgeter',
    description: "Your income varies month-to-month. You'd benefit from flexible budgeting strategies and cash flow planning.",
    icon: '📊',
    focusAreas: [
      'Flexible budgeting frameworks',
      'Cash flow forecasting tools',
      'Variable income management strategies'
    ],
    color: 'purple'
  },
  'subscription_heavy_spender': {
    name: 'Subscription-Heavy Spender',
    description: 'You have multiple active subscriptions. Discover opportunities to audit and optimize your recurring expenses.',
    icon: '📱',
    focusAreas: [
      'Subscription audit checklists',
      'Cost reduction strategies',
      'Subscription management tools'
    ],
    color: 'pink'
  },
  'savings_builder': {
    name: 'Savings Builder',
    description: "You're building financial cushions. Accelerate your progress with targeted savings strategies.",
    icon: '🏦',
    focusAreas: [
      'Emergency fund acceleration techniques',
      'High-yield savings account comparisons',
      'Automated savings plan templates'
    ],
    color: 'green'
  },
  'cash_flow_optimizer': {
    name: 'Cash Flow Optimizer',
    description: 'You have strong liquidity and low debt. Explore advanced optimization strategies.',
    icon: '💰',
    focusAreas: [
      'Advanced cash flow optimization',
      'Investment readiness education',
      'Tax-advantaged savings strategies'
    ],
    color: 'blue'
  },
  'young_professional': {
    name: 'Young Professional',
    description: "You're early in your financial journey. Build strong money habits from the start.",
    icon: '🎯',
    focusAreas: [
      'Foundational money management',
      'Credit building strategies',
      'Budget creation basics'
    ],
    color: 'cyan'
  }
};

export function getPersonaContent(personaKey: string): PersonaContent {
  return PERSONA_CONTENT[personaKey] || PERSONA_CONTENT['young_professional'];
}
