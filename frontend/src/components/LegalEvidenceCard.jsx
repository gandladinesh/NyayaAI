export default function LegalEvidenceCard({
  provision,
  applicableCentralLaws = [],
  applicableStateLaws = [],
}) {
  const hasLaws = applicableCentralLaws.length > 0 || applicableStateLaws.length > 0;
  if (!provision && !hasLaws) return null;

  return (
    <div className="result-card legal-evidence-card">
      <div className="card-top-meta">
        <div className="result-label">APPLICABLE STATUTORY FRAMEWORK & EVIDENCE</div>
        <span className="authority-level-badge">VERIFIED STATUTES</span>
      </div>

      {hasLaws && (
        <div className="statutes-list-section">
          {applicableCentralLaws.length > 0 && (
            <div className="law-group">
              <h4>Applicable Central / Parliamentary Acts</h4>
              <ul className="laws-list">
                {applicableCentralLaws.map((law, idx) => (
                  <li key={idx} className="law-item">
                    <span className="law-bullet">⚖</span>
                    <span className="law-title">{law}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {applicableStateLaws.length > 0 && (
            <div className="law-group">
              <h4>Applicable State Enactments</h4>
              <ul className="laws-list">
                {applicableStateLaws.map((law, idx) => (
                  <li key={idx} className="law-item">
                    <span className="law-bullet">🏛</span>
                    <span className="law-title">{law}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {provision && (
        <div className="provision-detail-section">
          <div className="provision-header">
            <h3>{provision.reference_number}</h3>
            <span className="provision-act">{provision.act}</span>
          </div>

          <div className="legal-text-container">
            <div className="legal-text-header">
              <span className="section-subtitle">EXACT VERIFIED LEGAL TEXT</span>
              <span className="exact-text-tag">Statutory Source</span>
            </div>
            <blockquote className="exact-legal-quote">
              {provision.exact_text}
            </blockquote>
          </div>

          {provision.ai_explanation && (
            <div className="ai-explanation-container">
              <div className="ai-explanation-header">
                <span className="section-subtitle">PLAIN LANGUAGE EXPLANATION</span>
                <span className="ai-tag">AI Generated Summary</span>
              </div>
              <p className="ai-explanation-body">{provision.ai_explanation}</p>
              <p className="ai-disclaimer">
                Note: This explanation is prepared in simple language for citizen awareness and is not the official statutory wording.
              </p>
            </div>
          )}

          <div className="card-footer-meta">
            <div className="verification-badge verified">
              ✓ {provision.verification_status || "VERIFIED"}
            </div>
            {provision.official_citation && (
              <span className="official-citation-tag">
                Citation: {provision.official_citation}
              </span>
            )}
            {provision.source_url && (
              <a
                href={provision.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="source-verify-link"
              >
                View official text ↗
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
