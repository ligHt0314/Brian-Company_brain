from typing import Annotated
from fastapi import APIRouter, Depends
from app.auth.policy import current_user, require
from app.domain.models import Me
from app.work.models import (
    MeetingCreate,
    MeetingNotes,
    MeetingPatch,
    RecapConfirm,
    ActionCreate,
    ActionPatch,
    BriefRequest,
    Meeting,
    MeetingDetail,
    Action,
    RecapDraft,
    Brief,
)
from app.work.service import Work

router = APIRouter(prefix="/api/v1", tags=["Meetings and actions"])
User = Annotated[Me, Depends(current_user)]


def work():
    from app import main

    return Work(main.repo, main.store)


@router.get("/meetings", response_model=list[Meeting])
def meetings(user: User):
    service = work()
    # Linked knowledge revocation makes saved recaps unavailable until access is restored.
    with service.repo.lock:
        results = []
        from fastapi import HTTPException

        for m in service.list("meeting", user):
            try:
                results.append(service.visible_meeting(m["id"], user))
            except HTTPException as exc:
                if exc.status_code not in {404, 409}:
                    raise
        return results


@router.post("/meetings", response_model=Meeting)
def create_meeting(body: MeetingCreate, user: User):
    require(user, "review")
    return work().create(body, user)


@router.get("/meetings/{id}", response_model=MeetingDetail)
def meeting_detail(id: str, user: User):
    return work().detail(id, user)


@router.patch("/meetings/{id}", response_model=Meeting)
def update_meeting(id: str, body: MeetingPatch, user: User):
    require(user, "review")
    return work().patch_meeting(id, body, user)


@router.post("/meetings/{id}/recap", response_model=RecapDraft)
def recap(id: str, user: User):
    require(user, "review")
    return work().draft(id, user)


@router.post("/meetings/{id}/confirm-recap", response_model=MeetingDetail)
def confirm_recap(id: str, body: RecapConfirm, user: User):
    require(user, "review")
    return work().confirm(id, body, user)


@router.post("/meetings/{id}/actions", response_model=Action)
def create_action(id: str, body: ActionCreate, user: User):
    require(user, "review")
    return work().add_action(id, body, user)


@router.get("/actions", response_model=list[Action])
def actions(user: User):
    service = work()
    with service.repo.lock:
        permitted = {m["id"] for m in meetings(user)}
        return [a for a in service.list("action", user) if a["origin_meeting_id"] in permitted]


@router.patch("/actions/{id}", response_model=Action)
def update_action(id: str, body: ActionPatch, user: User):
    require(user, "review")
    return work().patch_action(id, body, user)


@router.post("/meetings/{id}/brief", response_model=Brief)
def catchup(id: str, body: BriefRequest, user: User):
    return work().brief(id, body, user)


@router.patch("/meetings/{id}/notes", response_model=Meeting)
def meeting_notes(id: str, body: MeetingNotes, user: User):
    require(user, "review")
    return work().notes(id, body, user)
