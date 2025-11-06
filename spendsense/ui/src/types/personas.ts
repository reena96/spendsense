/**
 * TypeScript types for Persona Assignment Review (Story 6.3)
 */

export interface PersonaDefinition {
  persona_id: string;
  display_name: string;
  description: string;
  educational_focus: string;
  priority_rank: number;
  criteria: Record<string, any>;
  icon: string;
  color: string;
}

export interface QualifyingPersona {
  persona_id: string;
  persona_name: string;
  priority_rank: number;
  match_evidence: Record<string, any>;
}

export interface PersonaAssignment {
  assignment_id: string;
  time_window: string;
  assigned_persona_id: string;
  assigned_persona_name: string;
  assigned_at: string;
  priority_rank: number | null;
  qualifying_personas: QualifyingPersona[];
  prioritization_reason: string;
  confidence_level: number | null;
  is_override: boolean;
}

export interface PersonaChangeHistoryItem {
  changed_at: string;
  time_window: string;
  previous_persona: string;
  previous_persona_name: string;
  new_persona: string;
  new_persona_name: string;
  reason: string;
  is_override: boolean;
}

export interface PersonaAssignmentsResponse {
  user_id: string;
  user_name: string;
  assignments: {
    "30d"?: PersonaAssignment;
    "180d"?: PersonaAssignment;
  };
  change_history: PersonaChangeHistoryItem[];
}

export interface PersonaOverrideRequest {
  new_persona_id: string;
  justification: string;
  time_window: "30d" | "180d";
}

export interface PersonaOverrideResponse {
  assignment_id: string;
  user_id: string;
  old_persona: string;
  new_persona: string;
  operator_id: string;
  justification: string;
  assigned_at: string;
}
