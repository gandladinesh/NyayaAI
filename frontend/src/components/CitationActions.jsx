import { useState } from "react";
import { downloadCitationFile, copyCitationText } from "../utils/citationFormatter";

export default function CitationActions({ answer }) {
  const [copied, setCopied] = useState(false);
  const [downloading, setDownloading] = useState(false);

  if (!answer || !answer.primary_result) {
    return null;
  }

  const handleCopy = async () => {
    try {
      await copyCitationText(answer);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch (err) {
      console.error("Failed to copy citation:", err);
    }
  };

  const handleDownload = () => {
    try {
      setDownloading(true);
      downloadCitationFile(answer);
      setTimeout(() => setDownloading(false), 1000);
    } catch (err) {
      console.error("Failed to download citation:", err);
      setDownloading(false);
    }
  };

  return (
    <div className="citation-export-bar">
      <div className="citation-export-info">
        <span className="citation-export-label">⚖️ LEGAL EVIDENCE EXPORT</span>
        <span className="citation-export-subtext">
          Download or copy verified statutory text, citations, and Supreme Court authorities.
        </span>
      </div>

      <div className="citation-button-group">
        <button
          type="button"
          className={`citation-action-btn copy-btn ${copied ? "copied" : ""}`}
          onClick={handleCopy}
          title="Copy formatted citation and legal text to clipboard"
        >
          {copied ? (
            <>
              <span className="btn-icon">✓</span> Copied to Clipboard!
            </>
          ) : (
            <>
              <span className="btn-icon">📋</span> Copy Citation
            </>
          )}
        </button>

        <button
          type="button"
          className="citation-action-btn download-btn"
          onClick={handleDownload}
          disabled={downloading}
          title="Download full legal citation document as a .txt file"
        >
          <span className="btn-icon">📥</span> Download Citation (.txt)
        </button>
      </div>
    </div>
  );
}
