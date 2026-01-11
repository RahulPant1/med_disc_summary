/**
 * Utility functions for issue handling and display
 */

/**
 * Get user-friendly display label for issue types
 * @param {string} type - Issue type from backend
 * @returns {string} User-friendly label with icon
 */
export const getIssueTypeDisplay = (type) => {
  const labels = {
    // Clinical Safety Agent
    'drug_overdose': '💊 Drug Overdose Risk',
    'drug_diagnosis_mismatch': '⚕️ Medication-Diagnosis Mismatch',
    'drug_interaction': '⚠️ Dangerous Drug Interaction',
    'dangerous_polypharmacy': '💊 Polypharmacy Concern',
    'drug_spelling_error': '📝 Drug Name Error',
    'dangerous_abbreviation': '⚠️ Dangerous Abbreviation',
    'abnormal_finding_no_action': '🔬 Untreated Abnormal Finding',
    'missing_critical_diagnosis': '📋 Missing Diagnosis',
    'procedure_mismatch': '🏥 Procedure Documentation Issue',
    'clinical_contradiction': '⚠️ Contradictory Clinical Information',

    // Critical Data Safety Agent
    'timeline_impossible': '📅 Impossible Timeline',
    'date_logic_error': '📅 Date Logic Error',
    'missing_identifier': '🆔 Missing Patient Identifier',
    'missing_critical_section': '📋 Missing Critical Section',
    'test_name_error': '🔬 Test Name Error',
    'age_mismatch': '👤 Age Inconsistency',
  };

  return labels[type] || type;
};

/**
 * Organize issues by severity level
 * @param {Object} results - Results object from backend (keyed by agent name)
 * @returns {Object} Issues organized by severity
 */
export const organizeIssuesBySeverity = (results) => {
  const allIssues = [];

  // Flatten all issues from all agents
  Object.values(results).forEach(agentResult => {
    if (agentResult?.issues) {
      allIssues.push(...agentResult.issues);
    }
  });

  return {
    high: allIssues.filter(i => i.severity === 'HIGH'),
    medium: allIssues.filter(i => i.severity === 'MEDIUM'),
    low: allIssues.filter(i => i.severity === 'LOW'),
    all: allIssues
  };
};

/**
 * Get severity color class for UI
 * @param {string} severity - Severity level (HIGH/MEDIUM/LOW)
 * @returns {Object} Tailwind color classes for the severity
 */
export const getSeverityColors = (severity) => {
  const colors = {
    HIGH: {
      bg: 'bg-red-50',
      border: 'border-red-500',
      text: 'text-red-800',
      badge: 'bg-red-600',
      badgeText: 'text-white',
    },
    MEDIUM: {
      bg: 'bg-orange-50',
      border: 'border-orange-300',
      text: 'text-orange-800',
      badge: 'bg-orange-600',
      badgeText: 'text-white',
    },
    LOW: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-300',
      text: 'text-yellow-800',
      badge: 'bg-yellow-600',
      badgeText: 'text-white',
    },
  };

  return colors[severity] || colors.MEDIUM;
};
