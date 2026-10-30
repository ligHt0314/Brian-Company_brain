"""Meeting and handover contracts; business records live in FalkorDB."""

from datetime import date
from typing import Literal
from pydantic import Field, model_validator
from app.domain.models import Strict


class DecisionDraft(Strict):
    text: str = Field(min_length=1, max_length=1500)
    quote: str = Field(min_length=1, max_length=2500)


class ActionDraft(DecisionDraft):
    owner_id: str | None = None
    due_date: date | None = None


class Recap(Strict):
    summary: str = Field(min_length=1, max_length=6000)
    decisions: list[DecisionDraft] = Field(default_factory=list, max_length=30)
    actions: list[ActionDraft] = Field(default_factory=list, max_length=40)
    knowledge_source_ids: list[str] = Field(default_factory=list, max_length=12)


class MeetingCreate(Strict):
    title: str = Field(min_length=3, max_length=200)
    kind: Literal["meeting", "handover"] = "meeting"
    agenda: str = Field(default="", max_length=12000)
    notes: str = Field(default="", max_length=50000)
    scheduled_at: str
    participant_ids: list[str] = Field(min_length=1, max_length=40)
    absent_ids: list[str] = Field(default_factory=list, max_length=40)
    project_id: str
    acl_groups: list[Literal["engineering", "leadership", "all_employees"]] = Field(
        min_length=1, max_length=3
    )
    previous_meeting_id: str | None = None
    carry_action_ids: list[str] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def validate_time(self):
        from datetime import datetime

        parsed = datetime.fromisoformat(self.scheduled_at.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("Meeting time must include a time zone")
        self.title = self.title.strip()
        if len(self.title) < 3:
            raise ValueError("Provide a meaningful session title")
        if len(set(self.participant_ids)) != len(self.participant_ids):
            raise ValueError("Do not repeat participants")
        if not set(self.absent_ids) <= set(self.participant_ids):
            raise ValueError("Absent people must be invited participants")
        return self


class MeetingPatch(Strict):
    expected_version: int = Field(ge=1)
    status: Literal["planned", "in_progress", "completed", "archived"]


class RecapConfirm(Strict):
    expected_version: int = Field(ge=1)
    draft_id: str | None = None
    recap: Recap


class ActionCreate(ActionDraft):
    expected_version: int = Field(ge=1)


class ActionPatch(Strict):
    expected_version: int = Field(ge=1)
    owner_id: str | None = None
    due_date: date | None = None
    status: Literal["open", "in_progress", "blocked", "done", "cancelled"] | None = None
    outcome: str | None = Field(default=None, max_length=4000)


class BriefRequest(Strict):
    recipient_id: str


class BriefBlock(Strict):
    text: str = Field(min_length=1, max_length=3000)
    reference_ids: list[str] = Field(min_length=1, max_length=20)


class BriefOutput(Strict):
    blocks: list[BriefBlock] = Field(min_length=1, max_length=12)


class Event(Strict):
    at: str
    actor: str
    event: str
    detail: str


class KnowledgeLink(Strict):
    source_id: str
    title: str
    evidence_id: str | None = None
    quote: str


class Action(Strict):
    id: str
    title: str
    owner_id: str | None
    due_date: str | None
    status: Literal["open", "in_progress", "blocked", "done", "cancelled"]
    outcome: str
    version: int
    origin_meeting_id: str
    meeting_ids: list[str]
    quote: str
    created_at: str
    updated_at: str
    history: list[Event]
    acl_groups: list[str]


class Meeting(Strict):
    id: str
    title: str
    kind: Literal["meeting", "handover"]
    agenda: str
    notes: str
    scheduled_at: str
    participant_ids: list[str]
    absent_ids: list[str]
    project_id: str
    acl_groups: list[str]
    previous_meeting_id: str | None
    action_ids: list[str]
    status: Literal["planned", "in_progress", "completed", "archived"]
    summary: str
    decisions: list[DecisionDraft]
    knowledge_links: list[KnowledgeLink]
    version: int
    created_at: str
    updated_at: str
    history: list[Event]
    recap_confirmed: bool = False


class MeetingDetail(Strict):
    meeting: Meeting
    actions: list[Action]


class RecapDraft(Strict):
    id: str
    meeting_id: str
    expected_version: int
    recap: Recap
    mode: Literal["live_model"] = "live_model"


class Brief(Strict):
    meeting_id: str
    recipient_id: str
    mode: Literal["live_model", "manual_context"]
    warning: str | None = None
    blocks: list[BriefBlock]
    references: dict[str, str]
    changes: list[Event]


class MeetingNotes(Strict):
    expected_version: int = Field(ge=1)
    notes: str = Field(min_length=1, max_length=50000)
    agenda: str | None = Field(default=None, max_length=12000)
