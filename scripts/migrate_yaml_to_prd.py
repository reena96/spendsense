#!/usr/bin/env python3
"""
Migrate recommendations.yaml from persona-based to PRD flat structure.

This script:
1. Reads current persona-based YAML
2. Converts to flat list with personas[], triggering_signals[], type fields
3. Maps category → type
4. Infers triggering_signals from personalization templates
5. Outputs PRD-compliant YAML
"""

import yaml
import re
from typing import Dict, List, Any

# Category to Type mapping
CATEGORY_TO_TYPE = {
    "education": "article",
    "action": "template",  # Action items often need templates/checklists
    "tip": "article",
    "insight": "calculator",  # Insights often involve calculations
}

# Infer signals from personalization templates
def infer_signals_from_template(template: str) -> List[str]:
    """Extract signal types from template placeholders."""
    if not template:
        return []

    signals = set()

    # Find all {placeholder} patterns
    placeholders = re.findall(r'\{([a-z_0-9]+)\}', template)

    for placeholder in placeholders:
        if 'credit' in placeholder or 'utilization' in placeholder:
            signals.add('credit_utilization')
        if 'savings' in placeholder or 'emergency' in placeholder:
            signals.add('savings_balance')
        if 'subscription' in placeholder:
            signals.add('subscription_count')
        if 'income' in placeholder:
            signals.add('income_stability')

    return sorted(list(signals))

# Infer signals from recommendation ID/title/description
def infer_signals_from_content(rec_id: str, title: str, desc: str) -> List[str]:
    """Infer signals from content keywords."""
    content = f"{rec_id} {title} {desc}".lower()
    signals = set()

    if any(word in content for word in ['credit', 'utilization', 'debt', 'payoff', 'apr']):
        signals.add('credit_utilization')
    if any(word in content for word in ['savings', 'emergency', 'fund', 'hysa']):
        signals.add('savings_balance')
    if any(word in content for word in ['subscription', 'recurring', 'cancel', 'audit']):
        signals.add('subscription_count')
    if any(word in content for word in ['income', 'variable', 'biweekly', 'paycheck']):
        signals.add('income_stability')

    return sorted(list(signals))

def migrate_yaml(input_file: str, output_file: str):
    """Migrate YAML from persona-based to flat structure."""

    # Read current YAML
    with open(input_file, 'r') as f:
        data = yaml.safe_load(f)

    # Extract recommendations from persona-based structure
    flat_recommendations = []

    for persona_id, recommendations in data['recommendations'].items():
        for rec in recommendations:
            # Map category to type
            rec_type = CATEGORY_TO_TYPE.get(rec['category'], 'article')

            # Infer signals
            template_signals = infer_signals_from_template(
                rec.get('personalization_template', '')
            )
            content_signals = infer_signals_from_content(
                rec['id'],
                rec['title'],
                rec['description']
            )

            # Combine signals (prefer template, fallback to content)
            triggering_signals = template_signals if template_signals else content_signals

            # Create new structure
            migrated_rec = {
                'id': rec['id'],
                'type': rec_type,
                'title': rec['title'],
                'description': rec['description'],
                'personas': [persona_id],  # Single persona for now (will merge duplicates later)
                'triggering_signals': triggering_signals,
                'category': rec['category'],
                'priority': rec['priority'],
                'difficulty': rec['difficulty'],
                'time_commitment': rec['time_commitment'],
                'estimated_impact': rec['estimated_impact'],
            }

            # Optional fields
            if rec.get('content_url'):
                migrated_rec['content_url'] = rec['content_url']
            if rec.get('personalization_template'):
                migrated_rec['personalization_template'] = rec['personalization_template']

            flat_recommendations.append(migrated_rec)

    # Create output structure
    output_data = {
        'educational_content': flat_recommendations
    }

    # Write new YAML
    with open(output_file, 'w') as f:
        # Add header comment
        f.write("# Educational Content Catalog (PRD-Compliant)\n")
        f.write("#\n")
        f.write("# Structure per Epic 4 PRD Story 4.1:\n")
        f.write("# - type: Content format (article/template/calculator/video)\n")
        f.write("# - personas: List of applicable persona IDs\n")
        f.write("# - triggering_signals: Behavioral signals that trigger this recommendation\n")
        f.write("#\n")
        f.write("# Signal types:\n")
        f.write("# - credit_utilization: High credit card utilization\n")
        f.write("# - savings_balance: Low savings or emergency fund\n")
        f.write("# - subscription_count: High subscription spending\n")
        f.write("# - income_stability: Irregular or variable income\n")
        f.write("#\n\n")

        yaml.dump(output_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"✅ Migrated {len(flat_recommendations)} recommendations")
    print(f"   Input:  {input_file}")
    print(f"   Output: {output_file}")

    # Print statistics
    types = {}
    for rec in flat_recommendations:
        types[rec['type']] = types.get(rec['type'], 0) + 1

    print(f"\n📊 Type Distribution:")
    for rec_type, count in sorted(types.items()):
        print(f"   {rec_type}: {count}")

if __name__ == "__main__":
    input_file = "spendsense/config/recommendations.yaml"
    output_file = "spendsense/config/recommendations_prd.yaml"

    migrate_yaml(input_file, output_file)
    print(f"\n✅ Migration complete! Review {output_file} before replacing original.")
