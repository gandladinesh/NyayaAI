import { useState } from "react";
import "./App.css";
import LocationSelector from "./components/LocationSelector";
import AuthorityCard from "./components/AuthorityCard";
import LegalEvidenceCard from "./components/LegalEvidenceCard";
import ActionPlan from "./components/ActionPlan";
import CitationActions from "./components/CitationActions";
import { API_BASE_URL, API_ENDPOINTS } from "./config";

const SAMPLE_QUESTIONS = [
  { label: "Right to Life (Art. 21)", query: "What is the right to life under Article 21?" },
  { label: "Equality Before Law (Art. 14)", query: "What does equality before the law mean under Article 14?" },
  { label: "Freedom of Speech (Art. 19)", query: "What are the six freedoms guaranteed under Article 19?" },
  { label: "Filing an FIR (BNSS s. 173)", query: "What are the rules for First Information Report under Bharatiya Nagarik Suraksha Sanhita?" },
  { label: "Theft Offence (BNS s. 303)", query: "What is the legal definition and punishment for theft under BNS?" },
  { label: "Electronic Evidence (BSA s. 65)", query: "What are the requirements for admissibility of electronic records as evidence under BSA?" },
];

const PROBLEM_CATEGORIES = [
  {
    id: "consumer_dispute",
    title: "Consumer Dispute",
    desc: "Defective products, deficient services, overcharging, unfair practices",
    icon: "🛒",
  },
  {
    id: "real_estate",
    title: "Real Estate & Housing",
    desc: "Delayed possession, builder default, structural defects, RERA violations",
    icon: "🏢",
  },
  {
    id: "legal_aid",
    title: "Free Legal Aid",
    desc: "Legal representation for eligible citizens, Lok Adalat resolution, DLSA",
    icon: "⚖️",
  },
  {
    id: "human_rights",
    title: "Human Rights Violation",
    desc: "Custodial excesses, police misconduct, human rights complaints to SHRC/NHRC",
    icon: "🛡️",
  },
];

function App() {
  const [question, setQuestion] = useState("");
  const [mode, setMode] = useState("information");
  const [language, setLanguage] = useState("en");
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [errorType, setErrorType] = useState(""); // "network" | "api" | "no_result"
  const [unresolvedData, setUnresolvedData] = useState(null); // stores { status, message, suggestions, next_steps }

  // Action Mode state
  const [selectedState, setSelectedState] = useState("");
  const [selectedStateObj, setSelectedStateObj] = useState(null);
  const [selectedDistrict, setSelectedDistrict] = useState("");
  const [selectedDistrictObj, setSelectedDistrictObj] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [actionResult, setActionResult] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [actionError, setActionError] = useState("");
  const [actionErrorType, setActionErrorType] = useState("");

  // Helper function to get user-friendly error message
  const getErrorMessage = (errorType) => {
    switch (errorType) {
      case "network":
        return {
          title: "Unable to Connect",
          message:
            `The legal information service is not responding. Please check that the backend server is running and accessible at ${API_BASE_URL}.`,
        };
      case "api":
        return {
          title: "Service Error",
          message:
            "The service encountered an error processing your request. Please try again.",
        };
      case "no_result":
        return {
          title: "No Relevant Information Found",
          message:
            "The service couldn't find legal provisions matching your question. Try rephrasing your question or explore the suggestions below.",
        };
      default:
        return {
          title: "Error",
          message: "An unexpected error occurred. Please try again.",
        };
    }
  };

  // Helper to map confidence level to citizen-friendly label and styling
  const getConfidenceInfo = (level, score) => {
    switch (level) {
      case "high":
        return {
          label: "High confidence",
          className: "confidence-high",
          scoreText: score !== undefined ? `${score}% match` : "",
        };
      case "medium":
        return {
          label: "Moderate confidence",
          className: "confidence-medium",
          scoreText: score !== undefined ? `${score}% match` : "",
        };
      case "low":
        return {
          label: "Low confidence",
          className: "confidence-low",
          scoreText: score !== undefined ? `${score}% match` : "",
        };
      default:
        return {
          label: score !== undefined ? `${score}% relevance` : "Relevance score",
          className: "confidence-default",
          scoreText: score !== undefined ? `${score}%` : "",
        };
    }
  };

  const askNyayaAI = async () => {
    if (!question.trim()) {
      return;
    }

    setLoading(true);
    setError("");
    setErrorType("");
    setAnswer(null);
    setUnresolvedData(null);

    try {
      const response = await fetch(API_ENDPOINTS.query, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question.trim(),
          top_k: 3,
          language: language,
        }),
      });

      if (!response.ok) {
        setErrorType("api");
        setError(getErrorMessage("api").message);
        return;
      }

      const data = await response.json();

      if (data.status !== "success") {
        setErrorType("no_result");
        setError(data.message || getErrorMessage("no_result").message);
        setUnresolvedData({
          status: data.status,
          message: data.message,
          suggestions: data.suggestions || [],
          next_steps: data.next_steps || [],
        });
        return;
      }

      setAnswer(data);
    } catch (err) {
      console.error(err);
      setErrorType("network");
      setError(getErrorMessage("network").message);
    } finally {
      setLoading(false);
    }
  };


  // Action Mode authority routing handler
  const handleActionSubmit = async (e) => {
    if (e) e.preventDefault();

    if (!selectedState || !selectedDistrict || !selectedCategory) {
      setActionError("Please select a State, District, and Legal Problem Category.");
      setActionErrorType("");
      return;
    }

    setActionLoading(true);
    setActionError("");
    setActionErrorType("");
    setActionResult(null);

    try {
      const queryParams = new URLSearchParams({
        state_id: selectedState,
        district_id: selectedDistrict,
        legal_category: selectedCategory,
      });

      const response = await fetch(`${API_ENDPOINTS.route}?${queryParams.toString()}`);
      if (!response.ok) {
        setActionErrorType("api");
        setActionError(
          "The service encountered an error routing your request. Please try again."
        );
        return;
      }

      const data = await response.json();
      setActionResult(data);
    } catch (err) {
      console.error("Action Mode error:", err);
      setActionErrorType("network");
      setActionError(
        `Unable to connect to the routing service. Please check that the backend server is running and accessible at ${API_BASE_URL}.`
      );
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <div className="logo">⚖</div>
          <div>
            <h1>NyayaAI</h1>
            <p>Indian Legal & Human Rights Assistant</p>
          </div>
        </div>
      </header>

      <main className="main">
        <section className="hero">
          <div className="badge">🇮🇳 Citizen Legal Assistance</div>
          <div className="mode-selector">
  <button
    type="button"
    className={mode === "information" ? "mode-button active" : "mode-button"}
    onClick={() => setMode("information")}
  >
    Information Mode
  </button>

  <button
    type="button"
    className={mode === "action" ? "mode-button active" : "mode-button"}
    onClick={() => setMode("action")}
  >
    Action Mode
  </button>
</div>

          <h2>
            {mode === "information" ? (
  <>
    Understand your <span>legal rights</span>
  </>
) : (
  <>
    Take action on your <span>legal problem</span>
  </>
)}
          </h2>

          <p className="hero-text">
            {mode === "information"
              ? "Ask about Indian laws, constitutional rights, legal provisions, and important legal concepts."
              : "Tell us your jurisdiction and issue. NyayaAI identifies the official responsible authority, statutory procedures, and your 4-step action plan."}
          </p>

          {/* Mode 1: Information Mode Query Box */}
          {mode === "information" && (
            <div className="query-section">
              <div className="query-box">
                <textarea
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  onKeyDown={(e) => {
                    if ((e.ctrlKey || e.metaKey) && e.key === "Enter" && question.trim() && !loading) {
                      e.preventDefault();
                      askNyayaAI();
                    }
                  }}
                  placeholder="Ask a legal question (e.g., What is the right to life guaranteed under Article 21?)..."
                  rows="4"
                />

                <div className="query-footer">
                  <div className="query-footer-left">
                    <span className="query-hint">Press <kbd>Ctrl</kbd> + <kbd>Enter</kbd> to search</span>
                    <div className="language-selector-inline">
                      <label htmlFor="lang-select" className="lang-label">Language:</label>
                      <select
                        id="lang-select"
                        value={language}
                        onChange={(e) => setLanguage(e.target.value)}
                        className="lang-select"
                        disabled={loading}
                        title="Select explanation language (Statutory text remains in authoritative English)"
                      >
                        <option value="en">English</option>
                        <option value="hi">हिंदी (Hindi)</option>
                        <option value="te">తెలుగు (Telugu)</option>
                        <option value="mr">मराठी (Marathi)</option>
                      </select>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={askNyayaAI}
                    disabled={!question.trim() || loading}
                  >
                    {loading ? "Searching Verified Corpus..." : "Ask NyayaAI →"}
                  </button>
                </div>

              </div>

              <div className="sample-queries-container">
                <span className="sample-queries-label">Explore Key Constitutional Rights:</span>
                <div className="sample-chips">
                  {SAMPLE_QUESTIONS.map((item, idx) => (
                    <button
                      key={idx}
                      type="button"
                      className="sample-chip"
                      onClick={() => {
                        setQuestion(item.query);
                        setError("");
                        setErrorType("");
                      }}
                      disabled={loading}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Mode 2: Action Mode Form */}
          {mode === "action" && (
            <div className="action-form-box">
              <p className="action-form-intro">
                Select your State, District, and legal grievance category to route directly to the designated official authority and procedural filing roadmap.
              </p>

              <form onSubmit={handleActionSubmit}>
                <LocationSelector
                  selectedState={selectedState}
                  selectedDistrict={selectedDistrict}
                  onStateChange={(stateId, stateObj) => {
                    setSelectedState(stateId);
                    setSelectedStateObj(stateObj);
                    setActionResult(null);
                  }}
                  onDistrictChange={(distId, distObj) => {
                    setSelectedDistrict(distId);
                    setSelectedDistrictObj(distObj);
                    setActionResult(null);
                  }}
                  disabled={actionLoading}
                />

                <div className="input-field" style={{ marginTop: "14px" }}>
                  <label className="input-label">
                    Legal Problem Category <span className="required-star">*</span>
                  </label>
                  <div className="category-pill-grid">
                    {PROBLEM_CATEGORIES.map((cat) => {
                      const isSelected = selectedCategory === cat.id;
                      return (
                        <button
                          type="button"
                          key={cat.id}
                          className={`category-pill ${isSelected ? "selected" : ""}`}
                          onClick={() => {
                            setSelectedCategory(cat.id);
                            setActionResult(null);
                          }}
                          disabled={actionLoading}
                        >
                          <span className="category-icon">{cat.icon}</span>
                          <div className="category-info">
                            <div className="category-title">{cat.title}</div>
                            <div className="category-desc">{cat.desc}</div>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div className="action-form-footer">
                  <button
                    type="submit"
                    className="action-submit-btn"
                    disabled={
                      !selectedState ||
                      !selectedDistrict ||
                      !selectedCategory ||
                      actionLoading
                    }
                  >
                    {actionLoading
                      ? "Determining Jurisdiction & Routing..."
                      : "Find Responsible Authority & Action Plan →"}
                  </button>
                </div>
              </form>
            </div>
          )}
        </section>

        {/* ── Information Mode Results ───────────────────────────────────── */}
        {mode === "information" && (
          <>
            {error && (
              <section className="result-card error-card">
                <div className="error-content">
                  <div className="error-icon">⚠️</div>
                  <div className="error-text">
                    <h3>{getErrorMessage(errorType).title}</h3>
                    <p>{error}</p>
                  </div>
                </div>

                {/* Suggestions for rephrasing or searching */}
                {unresolvedData?.suggestions?.length > 0 && (
                  <div className="unresolved-guidance-box">
                    <div className="guidance-heading">
                      <span className="guidance-icon">💡</span>
                      <h4>Search Suggestions</h4>
                    </div>
                    <ul className="guidance-list">
                      {unresolvedData.suggestions.map((suggestion, idx) => (
                        <li key={idx}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Official redressal pathways */}
                {unresolvedData?.next_steps?.length > 0 && (
                  <div className="unresolved-redressal-box">
                    <div className="guidance-heading">
                      <span className="guidance-icon">🏛️</span>
                      <h4>Official Citizen Redressal Pathways</h4>
                    </div>
                    <ul className="redressal-list">
                      {unresolvedData.next_steps.map((step, idx) => (
                        <li key={idx}>{step}</li>
                      ))}
                    </ul>
                    <p className="redressal-disclaimer">
                      Note: These are official redressal channels and guidance pathways, not a formal legal opinion.
                    </p>
                  </div>
                )}

                <div className="error-actions">
                  <button
                    type="button"
                    className="retry-button"
                    onClick={askNyayaAI}
                    disabled={loading}
                  >
                    {loading ? "Retrying..." : "↻ Retry"}
                  </button>
                </div>
              </section>
            )}

            {answer && answer.primary_result && (
              <section className="results">
                <div className="question-heading">
                  <span>Your question</span>
                  <h2>{answer.question}</h2>
                </div>

                <CitationActions answer={answer} />

                {/* Confidence & Relevance Banner */}
                {answer.primary_result.confidence_level && (
                  <div className="confidence-banner">
                    <div className="confidence-main">
                      <span className={`confidence-pill ${getConfidenceInfo(answer.primary_result.confidence_level).className}`}>
                        {getConfidenceInfo(answer.primary_result.confidence_level).label}
                      </span>
                      {answer.primary_result.relevance_score !== undefined && (
                        <span className="relevance-score-tag">
                          {answer.primary_result.relevance_score}% Relevance Score
                        </span>
                      )}
                    </div>
                    <p className="confidence-note">
                      Confidence reflects how closely the verified provision matches your question; it is not a legal opinion.
                    </p>
                  </div>
                )}

                <div className="result-card">
                  <div className="result-label">VERIFIED LEGAL PROVISION</div>

                  <h2>{answer.primary_result.reference_number}</h2>

                  <p className="act-name">{answer.primary_result.act}</p>

                  <div className="verification">
                    ✓ {answer.primary_result.verification_status}
                  </div>

                  <div className="legal-text">
                    <h3>Exact Legal Text</h3>
                    <p>{answer.primary_result.exact_text}</p>
                  </div>
                </div>

                <div className="result-card">
                  <div className="result-label">AI EXPLANATION</div>

                  <h3>In simple language</h3>

                  <p className="explanation">
                    {answer.primary_result.ai_explanation}
                  </p>

                  <p className="ai-note">
                    This is an AI-generated explanation and is not the legal text.
                  </p>
                </div>

                {answer.primary_result.case_authorities?.length > 0 && (
                  <div className="result-card">
                    <div className="result-label">LEGAL AUTHORITIES</div>

                    <h3>Relevant Supreme Court cases</h3>

                    {answer.primary_result.case_authorities.map((authority) => (
                      <div className="case-authority" key={authority.case_id}>
                        <h4>{authority.case_name}</h4>

                        <p className="case-citation">{authority.citation}</p>

                        <p>{authority.legal_principle}</p>

                        <span>
                          {authority.court} • {authority.verification_status}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                <div className="result-card source-card">
                  <div className="result-label">SOURCE</div>

                  <h3>{answer.primary_result.source_name}</h3>

                  <p>Citation: {answer.primary_result.official_citation}</p>

                  <a
                    href={answer.primary_result.source_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    View source →
                  </a>
                </div>

                {/* Related Provisions */}
                {answer.related_results?.length > 0 && (
                  <div className="result-card related-results-card">
                    <div className="result-label">RELATED VERIFIED PROVISIONS</div>
                    <p className="related-intro">Other provisions identified from the verified corpus that may be relevant:</p>
                    <div className="related-items-list">
                      {answer.related_results.map((rel, idx) => (
                        <div key={rel.provision_id || idx} className="related-item">
                          <div className="related-item-header">
                            <span className="related-ref">{rel.reference_number}</span>
                            <span className="related-act">{rel.act}</span>
                            {rel.confidence_level && (
                              <span className={`related-confidence-badge ${getConfidenceInfo(rel.confidence_level).className}`}>
                                {getConfidenceInfo(rel.confidence_level).label}
                                {rel.relevance_score !== undefined && ` (${rel.relevance_score}%)`}
                              </span>
                            )}
                          </div>
                          {rel.ai_explanation && (
                            <p className="related-explanation">{rel.ai_explanation}</p>
                          )}
                          <div className="related-meta">
                            <span>✓ {rel.verification_status}</span>
                            {rel.official_citation && <span>• {rel.official_citation}</span>}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </section>
            )}

            {!answer && !loading && !error && (
              <section className="info-grid">
                <div className="info-card">
                  <div className="card-icon">📜</div>
                  <h3>Verified Legal Text</h3>
                  <p>
                    Exact legal provisions are kept separate from AI-generated
                    explanations.
                  </p>
                </div>

                <div className="info-card">
                  <div className="card-icon">🤖</div>
                  <h3>Simple Explanation</h3>
                  <p>
                    Complex legal concepts are explained in language that is easier
                    for citizens to understand.
                  </p>
                </div>

                <div className="info-card">
                  <div className="card-icon">⚖️</div>
                  <h3>Legal Authorities</h3>
                  <p>
                    Relevant judicial authorities can be shown alongside the legal
                    information.
                  </p>
                </div>
              </section>
            )}
          </>
        )}

        {/* ── Action Mode Results ─────────────────────────────────────────── */}
        {mode === "action" && (
          <>
            {actionError && (
              <section className="result-card error-card">
                <div className="error-content">
                  <div className="error-icon">⚠️</div>
                  <div className="error-text">
                    <h3>
                      {actionErrorType === "network"
                        ? "Unable to Connect"
                        : "Routing Error"}
                    </h3>
                    <p>{actionError}</p>
                  </div>
                </div>
                <div className="error-actions">
                  <button
                    type="button"
                    className="retry-button"
                    onClick={handleActionSubmit}
                    disabled={actionLoading}
                  >
                    {actionLoading ? "Retrying..." : "↻ Retry"}
                  </button>
                </div>
              </section>
            )}

            {actionResult && (
              <section className="results">
                <div className="question-heading">
                  <span>Jurisdiction & Authority Routing</span>
                  <h2>
                    {PROBLEM_CATEGORIES.find((c) => c.id === selectedCategory)?.title || selectedCategory}
                    {" • "}
                    {selectedDistrictObj?.district_name || selectedDistrict},{" "}
                    {selectedStateObj?.state_name || selectedState}
                  </h2>
                </div>

                {/* Case 1: Jurisdiction Undetermined */}
                {actionResult.jurisdiction_analysis &&
                !actionResult.jurisdiction_analysis.is_determined ? (
                  <div className="result-card undetermined-card">
                    <div className="card-top-meta">
                      <div className="result-label">JURISDICTION ADVISORY</div>
                      <span className="authority-level-badge">FURTHER DETAILS REQUIRED</span>
                    </div>
                    <h3 className="undetermined-title">Jurisdiction Could Not Be Fully Determined</h3>
                    <p className="undetermined-reasoning">
                      {actionResult.jurisdiction_analysis.reasoning}
                    </p>
                    {actionResult.jurisdiction_analysis.missing_information && (
                      <div className="undetermined-missing-info">
                        <strong>Missing details:</strong>{" "}
                        {actionResult.jurisdiction_analysis.missing_information}
                      </div>
                    )}
                  </div>
                ) : (
                  /* Case 2: Jurisdiction Determined */
                  <>
                    {actionResult.primary_authority && (
                      <AuthorityCard authority={actionResult.primary_authority} />
                    )}

                    {actionResult.escalation_authority &&
                      actionResult.escalation_authority.authority_id !==
                        actionResult.primary_authority?.authority_id && (
                        <AuthorityCard
                          authority={actionResult.escalation_authority}
                          isEscalation={true}
                        />
                      )}

                    {(actionResult.applicable_central_laws?.length > 0 ||
                      actionResult.applicable_state_laws?.length > 0) && (
                      <LegalEvidenceCard
                        applicableCentralLaws={actionResult.applicable_central_laws}
                        applicableStateLaws={actionResult.applicable_state_laws}
                      />
                    )}

                    {(actionResult.action_plan_steps?.length > 0 ||
                      actionResult.complaint_procedure) && (
                      <ActionPlan
                        actionPlanSteps={actionResult.action_plan_steps}
                        complaintProcedure={actionResult.complaint_procedure}
                        escalationAuthority={actionResult.escalation_authority}
                        sourceNote={actionResult.source_note}
                      />
                    )}
                  </>
                )}
              </section>
            )}

            {!actionResult && !actionLoading && !actionError && (
              <section className="info-grid">
                <div className="info-card">
                  <div className="card-icon">🏛️</div>
                  <h3>Statutory Jurisdiction</h3>
                  <p>
                    Direct routing from State and District to the designated official forum.
                  </p>
                </div>

                <div className="info-card">
                  <div className="card-icon">📋</div>
                  <h3>Official Filing Procedure</h3>
                  <p>
                    Statutory fees, formats, required evidence, and document checklists.
                  </p>
                </div>

                <div className="info-card">
                  <div className="card-icon">⚡</div>
                  <h3>Escalation Pathway</h3>
                  <p>
                    Statutory appellate authorities if the primary body fails to respond in time.
                  </p>
                </div>
              </section>
            )}
          </>
        )}

        <section className="notice">
          <strong>Important:</strong> NyayaAI provides legal information and
          citizen assistance. It is not a substitute for advice from a
          qualified legal professional.
        </section>
      </main>

      <footer>
        <p>NyayaAI • Indian Legal & Human Rights Assistant</p>
      </footer>
    </div>
  );
}

export default App;