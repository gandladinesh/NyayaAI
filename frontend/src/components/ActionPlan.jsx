// Helper function to safely parse JSON with validation
function safeParseJSON(jsonStr, fieldName = "data") {
  if (!jsonStr) return [];
  
  try {
    const parsed = typeof jsonStr === "string" ? JSON.parse(jsonStr) : jsonStr;
    // Ensure parsed result is an array
    return Array.isArray(parsed) ? parsed : [];
  } catch (e) {
    console.warn(`Failed to parse ${fieldName}:`, e);
    return [];
  }
}

// Helper to validate step object structure
function isValidStep(step) {
  return (
    step &&
    typeof step === "object" &&
    (typeof step.instruction === "string" || typeof step.step === "number")
  );
}

// Helper to validate document is a string
function isValidDoc(doc) {
  return typeof doc === "string" && doc.trim().length > 0;
}

export default function ActionPlan({
  actionPlanSteps = [],
  complaintProcedure,
  escalationAuthority,
  sourceNote,
}) {
  // Validate actionPlanSteps is an array
  const validSteps = Array.isArray(actionPlanSteps) ? actionPlanSteps : [];
  
  // Safe parse procedure steps with validation
  let parsedSteps = [];
  if (complaintProcedure?.procedure_steps_json) {
    parsedSteps = safeParseJSON(
      complaintProcedure.procedure_steps_json,
      "procedure_steps_json"
    ).filter(isValidStep);
  }

  // Safe parse required documents with validation
  let parsedDocs = [];
  if (complaintProcedure?.required_docs_json) {
    parsedDocs = safeParseJSON(
      complaintProcedure.required_docs_json,
      "required_docs_json"
    ).filter(isValidDoc);
  }

  // Early exit if no valid data to display
  if (!validSteps.length && !complaintProcedure) return null;

  return (
    <div className="result-card action-plan-card">
      <div className="card-top-meta">
        <div className="result-label">CITIZEN ACTION PLAN & PROCEDURES</div>
        <span className="authority-level-badge">OFFICIAL WORKFLOW</span>
      </div>

      <h2 className="action-plan-title">Step-by-Step Action Roadmap</h2>

      {/* Ordered Action Steps */}
      {validSteps.length > 0 && (
        <div className="action-steps-timeline">
          {validSteps.map((stepText, index) => (
            <div key={index} className="action-step-item">
              <div className="step-circle">{index + 1}</div>
              <div className="step-content">
                <p className="step-text">{stepText}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Detailed Official Complaint Procedure if available */}
      {complaintProcedure && (
        <div className="complaint-procedure-box">
          <div className="procedure-header">
            <h3>Official Complaint Filing Procedure</h3>
            {complaintProcedure.complaint_method && (
              <span className="procedure-method-badge">
                Method: {complaintProcedure.complaint_method.replace(/_/g, " ").toUpperCase()}
              </span>
            )}
          </div>

          <div className="procedure-meta-grid">
            {complaintProcedure.time_limit && (
              <div className="proc-meta-item">
                <span className="proc-meta-label">⏱ Statutory Time Limit:</span>
                <span className="proc-meta-value">{complaintProcedure.time_limit}</span>
              </div>
            )}
            {complaintProcedure.fee && (
              <div className="proc-meta-item">
                <span className="proc-meta-label">💳 Official Fee:</span>
                <span className="proc-meta-value">{complaintProcedure.fee}</span>
              </div>
            )}
            {complaintProcedure.format_required && (
              <div className="proc-meta-item">
                <span className="proc-meta-label">📋 Format Required:</span>
                <span className="proc-meta-value">{complaintProcedure.format_required}</span>
              </div>
            )}
          </div>

          {/* Show fallback message if no procedure data available */}
          {parsedSteps.length === 0 && parsedDocs.length === 0 && (
            <div className="procedure-fallback-notice">
              <p>
                Detailed filing instructions and required documents for this complaint procedure are not yet available. 
                Please contact the authority directly or visit their official website for complete information.
              </p>
            </div>
          )}

          {/* Procedure Steps List */}
          {parsedSteps.length > 0 && (
            <div className="procedure-steps-list">
              <h4>Filing Instructions</h4>
              <ol className="instructions-ol">
                {parsedSteps.map((s, idx) => (
                  <li key={idx} className="instruction-li">
                    <strong>Step {typeof s.step === "number" ? s.step : idx + 1}:</strong>{" "}
                    {s.instruction || s.text || "(no instruction provided)"}
                    {s.notes && <p className="step-subnote">{s.notes}</p>}
                  </li>
                ))}
              </ol>
            </div>
          )}

          {/* Required Documents Checklist */}
          {parsedDocs.length > 0 && (
            <div className="required-docs-checklist">
              <h4>Required Documents & Evidence</h4>
              <ul className="docs-ul">
                {parsedDocs.map((doc, idx) => (
                  <li key={idx} className="doc-li">
                    <span className="doc-check">✓</span>
                    <span>{doc}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {complaintProcedure.source_url && (
            <div className="procedure-source-footer">
              <span>Verified from: </span>
              <a
                href={complaintProcedure.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="procedure-link"
              >
                {complaintProcedure.source_url} ↗
              </a>
            </div>
          )}
        </div>
      )}

      {/* Escalation Path Notification */}
      {escalationAuthority && (
        <div className="escalation-alert-box">
          <div className="escalation-icon">⚡</div>
          <div className="escalation-text">
            <strong>Next Escalation Authority:</strong> If the primary forum fails to decide within statutory timelines or delivers an adverse decision, you have the right to escalate to <strong>{escalationAuthority.authority_name}</strong>.
          </div>
        </div>
      )}

      {sourceNote && (
        <div className="action-plan-disclaimer">
          <small>{sourceNote}</small>
        </div>
      )}
    </div>
  );
}
