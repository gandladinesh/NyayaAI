/**
 * NyayaAI — Legal Citation Formatter & Exporter
 *
 * Formats verified legal evidence, exact statutory text, AI explanations,
 * and Supreme Court case authorities into a clean, professional,
 * unadulterated citation document for citizens.
 */

/**
 * Safely derives a clean filename from the provision reference number.
 * e.g., "Article 21" -> "NyayaAI_Article_21_Citation.txt"
 */
export function getCitationFilename(answer) {
  const ref = answer?.primary_result?.reference_number || "Legal_Provision";
  const safeRef = ref.replace(/[^a-zA-Z0-9_-]/g, "_").replace(/_+/g, "_");
  return `NyayaAI_${safeRef}_Citation.txt`;
}

/**
 * Formats complete legal evidence into an authoritative, unedited citation document.
 * Never modifies or hallucinates legal text or citations.
 */
export function formatCitationText(answer) {
  if (!answer || !answer.primary_result) return "";

  const p = answer.primary_result;
  const question = answer.question || "N/A";
  const timestamp = new Date().toLocaleString("en-IN", {
    timeZone: "Asia/Kolkata",
    dateStyle: "full",
    timeStyle: "medium",
  });

  const divider = "=".repeat(80);
  const subDivider = "-".repeat(80);

  let doc = "";
  doc += `${divider}\n`;
  doc += `                       NYAYA AI — CITIZEN LEGAL CITATION\n`;
  doc += `              Verified Legal Evidence & Judicial Authorities Record\n`;
  doc += `${divider}\n\n`;

  doc += `Generated On        : ${timestamp} IST\n`;
  doc += `Platform            : NyayaAI (Indian Legal & Human Rights Assistant)\n`;
  doc += `Citizen Question    : "${question}"\n\n`;

  doc += `${divider}\n`;
  doc += `I. PRIMARY LEGAL PROVISION (VERIFIED STATUTE)\n`;
  doc += `${divider}\n`;
  doc += `Provision Reference : ${p.reference_number || "N/A"}\n`;
  doc += `Enactment / Act     : ${p.act || "N/A"}\n`;
  doc += `Official Citation   : ${p.official_citation || "N/A"}\n`;
  doc += `Verification Status : ${(p.verification_status || "VERIFIED").toUpperCase()}\n\n`;

  doc += `--- [EXACT LEGAL TEXT] ---\n`;
  doc += `(Exact, unedited statutory wording from official government records)\n\n`;
  doc += `${p.exact_text || "N/A"}\n\n`;

  doc += `--- [OFFICIAL SOURCE METADATA] ---\n`;
  doc += `Source Authority    : ${p.source_name || "N/A"}\n`;
  doc += `Source Type         : ${p.source_type || "official"}\n`;
  doc += `Source URL          : ${p.source_url || "N/A"}\n\n`;

  doc += `${divider}\n`;
  doc += `II. AI-GENERATED EXPLANATION (PLAIN LANGUAGE)\n`;
  doc += `${divider}\n`;
  doc += `NOTICE: The following explanation is AI-generated for public awareness\n`;
  doc += `and citizen understanding. It is NOT statutory text and does not constitute\n`;
  doc += `formal legal advice.\n\n`;
  doc += `${p.ai_explanation || "N/A"}\n\n`;

  doc += `${divider}\n`;
  doc += `III. RELEVANT SUPREME COURT CASE AUTHORITIES\n`;
  doc += `${divider}\n`;

  if (p.case_authorities && p.case_authorities.length > 0) {
    p.case_authorities.forEach((auth, idx) => {
      doc += `\n[Case Authority #${idx + 1}]\n`;
      doc += `Case Name           : ${auth.case_name || "N/A"}\n`;
      doc += `Citation (SCC/AIR)  : ${auth.citation || "N/A"}\n`;
      doc += `Court               : ${auth.court || "Supreme Court of India"}\n`;
      if (auth.judgment_date) {
        doc += `Judgment Date       : ${auth.judgment_date}\n`;
      }
      doc += `Legal Principle     : ${auth.legal_principle || "N/A"}\n`;
      doc += `Verification Status : ${(auth.verification_status || "VERIFIED").toUpperCase()}\n`;
      if (auth.source_name) {
        doc += `Official Source     : ${auth.source_name}\n`;
      }
      if (auth.source_url) {
        doc += `Source URL          : ${auth.source_url}\n`;
      }
      doc += `${subDivider}\n`;
    });
  } else {
    doc += `No specific case authorities indexed for this provision in Phase 1.\n\n`;
  }

  if (answer.related_results && answer.related_results.length > 0) {
    doc += `\n${divider}\n`;
    doc += `IV. RELATED LEGAL PROVISIONS\n`;
    doc += `${divider}\n`;
    answer.related_results.forEach((rel, idx) => {
      doc += `\n[Related Provision #${idx + 1}]\n`;
      doc += `Reference Number    : ${rel.reference_number || "N/A"}\n`;
      doc += `Act                 : ${rel.act || "N/A"}\n`;
      doc += `Official Citation   : ${rel.official_citation || "N/A"}\n`;
      doc += `Source URL          : ${rel.source_url || "N/A"}\n`;
      if (rel.ai_explanation) {
        doc += `Plain Summary       : ${rel.ai_explanation}\n`;
      }
      doc += `${subDivider}\n`;
    });
  }

  doc += `\n${divider}\n`;
  doc += `IMPORTANT LEGAL NOTICE & DISCLAIMER\n`;
  doc += `${divider}\n`;
  doc += `NyayaAI provides legal information and citizen assistance. The statutory text\n`;
  doc += `and judicial principles contained herein are obtained from verified official\n`;
  doc += `government sources. This record does not constitute legal representation,\n`;
  doc += `formal legal counsel, or substitute for consultation with an advocate.\n`;
  doc += `${divider}\n`;

  return doc;
}

/**
 * Triggers a client-side download of the citation text document.
 */
export function downloadCitationFile(answer) {
  const content = formatCitationText(answer);
  const filename = getCitationFilename(answer);
  const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Copies the citation text to clipboard with fallback for non-secure contexts.
 */
export async function copyCitationText(answer) {
  const content = formatCitationText(answer);
  if (navigator?.clipboard && window.isSecureContext) {
    await navigator.clipboard.writeText(content);
    return true;
  } else {
    const textArea = document.createElement("textarea");
    textArea.value = content;
    textArea.style.position = "fixed";
    textArea.style.left = "-999999px";
    textArea.style.top = "-999999px";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    const success = document.execCommand("copy");
    textArea.remove();
    return success;
  }
}
