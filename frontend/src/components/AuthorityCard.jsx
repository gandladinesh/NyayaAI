export default function AuthorityCard({
  authority,
  isEscalation = false,
  customTitle,
}) {
  if (!authority) return null;

  const levelBadgeLabel = authority.authority_level
    ? `${authority.authority_level.toUpperCase()} JURISDICTION`
    : "OFFICIAL AUTHORITY";

  return (
    <div className={`result-card authority-card ${isEscalation ? "escalation-card" : ""}`}>
      <div className="card-top-meta">
        <div className="result-label">
          {customTitle || (isEscalation ? "ESCALATION AUTHORITY" : "RESPONSIBLE LEGAL AUTHORITY")}
        </div>
        <span className="authority-level-badge">{levelBadgeLabel}</span>
      </div>

      <h2 className="authority-name">{authority.authority_name}</h2>

      {authority.jurisdiction_desc && (
        <div className="authority-section">
          <h4>Jurisdiction Scope</h4>
          <p className="jurisdiction-text">{authority.jurisdiction_desc}</p>
        </div>
      )}

      {authority.official_address && (
        <div className="authority-section">
          <h4>Official Address</h4>
          <p className="address-text">{authority.official_address}</p>
        </div>
      )}

      {(authority.official_website || authority.official_phone || authority.official_email || authority.complaint_url) && (
        <div className="authority-section">
          <h4>Official Contact & Portals</h4>
          <div className="contact-links-grid">
            {authority.official_website && (
              <div className="contact-item">
                <span className="contact-label">Official Website:</span>
                <a
                  href={authority.official_website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="official-link"
                >
                  {authority.official_website} ↗
                </a>
              </div>
            )}

            {authority.complaint_url && (
              <div className="contact-item">
                <span className="contact-label">Filing Portal:</span>
                <a
                  href={authority.complaint_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="official-link complaint-link"
                >
                  {authority.complaint_url} ↗
                </a>
              </div>
            )}

            {authority.official_phone && (
              <div className="contact-item">
                <span className="contact-label">Official Phone:</span>
                <span className="contact-val">{authority.official_phone}</span>
              </div>
            )}

            {authority.official_email && (
              <div className="contact-item">
                <span className="contact-label">Official Email:</span>
                <a href={`mailto:${authority.official_email}`} className="official-link">
                  {authority.official_email}
                </a>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="card-footer-meta">
        <div className="verification-badge verified">
          ✓ {authority.verification_status || "VERIFIED"}
        </div>
        {authority.source_authority && (
          <span className="source-authority-text">
            Source: {authority.source_authority}
          </span>
        )}
        {authority.source_url && (
          <a
            href={authority.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="source-verify-link"
          >
            Verify source ↗
          </a>
        )}
      </div>
    </div>
  );
}
