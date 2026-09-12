"""
NyayaAI — Authority Routing Database Models (SQLModel / SQLite → PostgreSQL ready)

All contact information must come from verified official government sources.
Fields with unknown values must be NULL — never fabricated.
The source_url for each record must point to the page that proves the information.

SQLModel is used so the same models serve as both:
  - SQLAlchemy ORM models (for database operations)
  - Pydantic schemas (for API serialization)

To migrate to PostgreSQL: change DATABASE_URL in config and run alembic migrations.
The model definitions themselves require no changes.
"""

from datetime import date
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


# ── Enums ────────────────────────────────────────────────────────────────────

class AuthorityType(str, Enum):
    CENTRAL_GOVERNMENT = "central_government"
    STATE_GOVERNMENT   = "state_government"
    DISTRICT_AUTHORITY = "district_authority"
    POLICE             = "police"
    LOCAL_BODY         = "local_body"
    SPECIALIZED        = "specialized"   # SEBI, RERA, NHRC, consumer courts, etc.
    COURT_FORUM        = "court_forum"   # District Consumer Forum, Labour Court, etc.
    LEGAL_AID          = "legal_aid"     # NALSA, SLSA, DLSA
    OMBUDSMAN          = "ombudsman"     # Banking, Insurance Ombudsman
    TRIBUNAL           = "tribunal"      # NGT, SAT, CAT, ITAT, etc.


class AuthorityLevel(str, Enum):
    CENTRAL  = "central"
    STATE    = "state"
    DISTRICT = "district"
    LOCAL    = "local"
    SPECIAL  = "special"


class SourceTypeDB(str, Enum):
    """Source authority level for authority records."""
    OFFICIAL      = "official"      # Government website, official gazette
    COURT         = "court"         # eCourts, court portal
    SUPPLEMENTARY = "supplementary" # Third-party reference


class VerificationStatusDB(str, Enum):
    """Three-level verification status for authority records."""
    VERIFIED           = "verified"
    PARTIALLY_VERIFIED = "partially_verified"
    UNVERIFIED         = "unverified"


# ── State ────────────────────────────────────────────────────────────────────

class State(SQLModel, table=True):
    __tablename__ = "states"

    state_id: str = Field(primary_key=True)           # "TS", "AP", "MH", "DL"
    state_name: str = Field(index=True)               # "Telangana"
    state_code: str                                    # "TS"
    state_type: str = Field(default="state")           # "state" | "union_territory"
    capital: Optional[str] = None
    high_court: Optional[str] = None
    high_court_url: Optional[str] = None
    is_union_territory: bool = Field(default=False)
    status: str = Field(default="active")
    source_url: str                                    # Proves this record
    last_verified: date

    districts: List["District"] = Relationship(back_populates="state")
    authorities: List["Authority"] = Relationship(back_populates="state")


class StateRead(SQLModel):
    state_id: str
    state_name: str
    state_code: str
    state_type: str = "state"
    capital: Optional[str]
    high_court: Optional[str]
    high_court_url: Optional[str]
    is_union_territory: bool
    status: str = "active"


# ── District ─────────────────────────────────────────────────────────────────

class District(SQLModel, table=True):
    __tablename__ = "districts"

    district_id: str = Field(primary_key=True)        # "TS-HYD"
    state_id: str = Field(foreign_key="states.state_id", index=True)
    district_name: str = Field(index=True)             # "Hyderabad"
    district_code: Optional[str] = None
    headquarters: Optional[str] = None
    status: str = Field(default="active")
    source_url: str
    last_verified: date

    state: Optional[State] = Relationship(back_populates="districts")
    authorities: List["Authority"] = Relationship(back_populates="district")


class DistrictRead(SQLModel):
    district_id: str
    state_id: str
    district_name: str
    district_code: Optional[str]
    headquarters: Optional[str]
    status: str = "active"


# ── Authority ─────────────────────────────────────────────────────────────────

class Authority(SQLModel, table=True):
    __tablename__ = "authorities"

    authority_id: str = Field(primary_key=True)        # "TS-CDRF-HYD"
    authority_name: str = Field(index=True)
    authority_type: AuthorityType
    authority_level: AuthorityLevel

    # Scope: NULL = all-India central authority
    state_id: Optional[str] = Field(default=None, foreign_key="states.state_id", index=True)
    district_id: Optional[str] = Field(default=None, foreign_key="districts.district_id", index=True)

    jurisdiction_desc: Optional[str] = None           # Plain-language jurisdiction description

    # Contact — NULL if not publicly known from official sources.
    # NEVER fabricate phone numbers, email, or addresses.
    official_address: Optional[str] = None
    official_website: Optional[str] = None
    official_email: Optional[str] = None              # NULL if not publicly available
    official_phone: Optional[str] = None              # NULL if not publicly available
    complaint_url: Optional[str] = None               # Direct complaint filing URL if available

    # Source metadata — mandatory
    source_url: str                                    # The page proving this record's details
    source_type: SourceTypeDB
    source_authority: str                              # "Government of Telangana" etc.
    verification_status: VerificationStatusDB = Field(default=VerificationStatusDB.UNVERIFIED)
    last_verified: date

    is_active: bool = Field(default=True)

    state: Optional[State] = Relationship(back_populates="authorities")
    district: Optional[District] = Relationship(back_populates="authorities")
    jurisdictions: List["AuthorityJurisdiction"] = Relationship(back_populates="authority")
    complaint_procedures: List["ComplaintProcedure"] = Relationship(back_populates="authority")


class AuthorityRead(SQLModel):
    authority_id: str
    authority_name: str
    authority_type: AuthorityType
    authority_level: AuthorityLevel
    state_id: Optional[str]
    district_id: Optional[str]
    jurisdiction_desc: Optional[str]
    official_address: Optional[str]
    official_website: Optional[str]
    official_email: Optional[str]
    official_phone: Optional[str]
    complaint_url: Optional[str]
    source_url: str
    source_type: SourceTypeDB
    source_authority: str
    verification_status: VerificationStatusDB
    last_verified: date
    is_active: bool


# ── Authority Jurisdiction ────────────────────────────────────────────────────

class AuthorityJurisdiction(SQLModel, table=True):
    __tablename__ = "authority_jurisdictions"

    id: Optional[int] = Field(default=None, primary_key=True)
    authority_id: str = Field(foreign_key="authorities.authority_id", index=True)
    legal_category: str = Field(index=True)           # "consumer_dispute", "police", "labour", etc.
    jurisdiction_notes: Optional[str] = None

    authority: Optional[Authority] = Relationship(back_populates="jurisdictions")


# ── Complaint Procedure ───────────────────────────────────────────────────────

class ComplaintProcedure(SQLModel, table=True):
    __tablename__ = "complaint_procedures"

    procedure_id: str = Field(primary_key=True)
    authority_id: str = Field(foreign_key="authorities.authority_id", index=True)
    legal_category: Optional[str] = Field(default=None, index=True)
    complaint_method: Optional[str] = Field(default=None, description="e.g. online_portal, written, e_daakhil")

    # Steps stored as JSON string (SQLite) — will be proper JSONB in PostgreSQL
    procedure_steps_json: Optional[str] = Field(
        default=None,
        description="JSON array of step objects: [{step: int, instruction: str, notes: str}]",
    )
    time_limit: Optional[str] = None                  # "30 days from incident"
    fee: Optional[str] = None                         # "No fee" or "₹100"
    format_required: Optional[str] = None             # "Online form" or "Written complaint"
    required_docs_json: Optional[str] = Field(
        default=None,
        description="JSON array of required documents",
    )
    escalation_authority_id: Optional[str] = Field(default=None, description="Direct escalation authority ID")

    source_url: str
    source_type: SourceTypeDB
    verification_status: VerificationStatusDB = Field(default=VerificationStatusDB.UNVERIFIED)
    last_verified: date

    authority: Optional[Authority] = Relationship(back_populates="complaint_procedures")


# ── Escalation Path ───────────────────────────────────────────────────────────

class EscalationPath(SQLModel, table=True):
    __tablename__ = "escalation_paths"

    id: Optional[int] = Field(default=None, primary_key=True)
    from_authority_id: str = Field(foreign_key="authorities.authority_id", index=True)
    to_authority_id: str = Field(foreign_key="authorities.authority_id", index=True)
    legal_category: Optional[str] = None
    escalation_trigger: Optional[str] = None          # "If no response within 30 days"
    time_limit: Optional[str] = None
    source_url: str
    last_verified: date


# ── Authority Routing Response ────────────────────────────────────────────────

class JurisdictionAnalysis(SQLModel):
    """Result of the jurisdiction analysis step in Action Mode."""
    is_determined: bool = Field(
        description="False if jurisdiction cannot be reliably determined — system must ask.",
    )
    jurisdiction_type: Optional[AuthorityLevel] = None
    reasoning: Optional[str] = None
    missing_information: Optional[str] = Field(
        None,
        description="What information is needed to determine jurisdiction, if undetermined",
    )


class AuthorityRoutingResult(SQLModel):
    """Complete routing result for Action Mode."""
    jurisdiction_analysis: JurisdictionAnalysis
    primary_authority: Optional[AuthorityRead] = None
    escalation_authority: Optional[AuthorityRead] = None
    complaint_procedure: Optional[ComplaintProcedure] = None
    applicable_central_laws: List[str] = Field(default_factory=list)
    applicable_state_laws: List[str] = Field(default_factory=list)
    action_plan_steps: List[str] = Field(default_factory=list)
    source_note: str = Field(
        default=(
            "Authority information sourced from official government records. "
            "Contact details are shown only where publicly available. "
            "Verify current contact details on the official website before visiting."
        )
    )
