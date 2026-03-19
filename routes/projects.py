from fastapi import HTTPException, Depends, APIRouter, Path, Query
from sqlalchemy.orm import Session
from db.db import get_db
from lib.auth import get_current_user
from models.plan import Projects, Plans, Tasks
from models.organization import Organization, OrganizationMember
from schema.project import ProjectResponse, CreateProject, PatchProject, ProjectCreateResponse
from pydantic import UUID4
from lib.subscription import require_active_subscription
from typing import List, Optional
from sqlalchemy import func
from schema.task import TaskStatusEnum


router = APIRouter()


def ensure_org_owner_or_admin(db: Session, organization: Organization, user_id: UUID4):
    if organization.owner_id == user_id:
        return

    membership = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.organization_id == organization.organization_id,
            OrganizationMember.user_id == user_id,
        )
        .first()
    )

    if not membership or membership.role.lower() != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only organization owner or admin can perform this action",
        )


@router.post("/", response_model=ProjectCreateResponse)
def create_project(
    payload: CreateProject,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    subscription=Depends(require_active_subscription),
):

    # Check active subscription
    user_plan = db.query(Plans).filter(Plans.plan_id == subscription.plan_id).first()

    if not user_plan:
        raise HTTPException(
            status_code=404, detail="no plan exist for this subscription"
        )

    total_projects = (
        db.query(Projects).filter(
            Projects.owner_user_id == current_user.user_id,
            Projects.organization_id.is_(None),
            Projects.isDelete == False
        ).count()
    )

    # check total projects < max project allowed in plan
    if total_projects >= user_plan.max_projects:
        raise HTTPException(
            status_code=403, detail="Project limit reached for your current plan"
        )

    new_project = Projects(
        owner_user_id=current_user.user_id,
        organization_id=None,
        name=payload.name,
        description=payload.description,
    )
    db.add(new_project)

    db.commit()
    db.refresh(new_project)

    return new_project


@router.post("/organization", response_model=ProjectCreateResponse)
def create_project_organization(
    payload: CreateProject,
    organization_id: UUID4 = Query(..., description="Organization ID to create project for"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    subscription=Depends(require_active_subscription),
):
    # Fetch organization and verify current user is the owner
    organization = db.query(Organization).filter(
        Organization.organization_id == organization_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=404, detail="Organization not found"
        )

    ensure_org_owner_or_admin(db, organization, current_user.user_id)

    # Check active subscription
    user_plan = db.query(Plans).filter(Plans.plan_id == subscription.plan_id).first()

    if not user_plan:
        raise HTTPException(
            status_code=404, detail="no plan exist for this subscription"
        )

    total_projects = (
        db.query(Projects).filter(
            Projects.organization_id == organization_id
        ).count()
    )

    # check total projects < max project allowed in plan
    if total_projects >= user_plan.max_projects:
        raise HTTPException(
            status_code=403, detail="Project limit reached for your current plan"
        )

    new_project = Projects(
        owner_user_id=organization.owner_id,
        organization_id=organization_id,
        name=payload.name,
        description=payload.description,
    )
    db.add(new_project)

    db.commit()
    db.refresh(new_project)

    return new_project


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project_details(
    payload: PatchProject,
    project_id: UUID4 = Path(..., description="project_id of the project"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_project = db.query(Projects).filter(Projects.project_id == project_id).first()

    if not user_project:
        raise HTTPException(status_code=404, detail="Project not found")

    if user_project.organization_id:
        organization = db.query(Organization).filter(
            Organization.organization_id == user_project.organization_id
        ).first()

        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")

        ensure_org_owner_or_admin(db, organization, current_user.user_id)
    else:
        if user_project.owner_user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this project")

    if payload.name is not None:
        user_project.name = payload.name
    if payload.description is not None:
        user_project.description = payload.description

    db.commit()
    db.refresh(user_project)
    return user_project


@router.get("/", response_model=List[ProjectResponse])
def get_project(
    project_id: Optional[UUID4] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = (
        db.query(
            Projects,
            func.count(Tasks.task_id).label("total_tasks"),
            func.count(Tasks.task_id)
                .filter(Tasks.status == TaskStatusEnum.DONE.value)
                .label("completed_tasks")
        )
        .outerjoin(
            Tasks,
            (Tasks.project_id == Projects.project_id) &
            (Tasks.isDelete == False)
        )
        .filter(
            Projects.owner_user_id == current_user.user_id,
            Projects.organization_id == None,
            Projects.isDelete == False
        )
        .group_by(Projects.project_id)
    )

    if project_id is not None:
        query = query.filter(Projects.project_id == project_id)

    results = query.all()

    if not results:
        raise HTTPException(status_code=404, detail="No projects found for the user")

    # 🔥 Map response properly
    response = []
    for project, total_tasks, completed_tasks in results:
        response.append(
            ProjectResponse(
                project_id=project.project_id,
                owner_user_id=project.owner_user_id,
                organization_id=project.organization_id,
                name=project.name,
                description=project.description,
                created_at=project.created_at,
                updated_at=project.updated_at,
                total_tasks=total_tasks,
                completed_tasks=completed_tasks
            )
        )

    return response



@router.get("/organization", response_model=List[ProjectResponse])
def get_project_organization(
    organization_id: UUID4 = Query(..., description="Organization ID to fetch projects for"),
    project_id: Optional[UUID4] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    from models.organization import Organization

    organization = db.query(Organization).filter(
        Organization.organization_id == organization_id
    ).first()

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    organization_member = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == organization_id,
        OrganizationMember.user_id == current_user.user_id
    ).first()
    if current_user.user_id != organization.owner_user_id and not organization_member:
        raise HTTPException(status_code=403, detail="Not a member of this organization")

    query = (
        db.query(
            Projects,
            func.count(Tasks.task_id).label("total_tasks"),
            func.count(Tasks.task_id)
                .filter(Tasks.status == TaskStatusEnum.DONE.value)
                .label("completed_tasks")
        )
        .outerjoin(
            Tasks,
            (Tasks.project_id == Projects.project_id) &
            (Tasks.isDelete == False)
        )
        .filter(
            Projects.organization_id == organization_id,
            Projects.isDelete == False
        )
        .group_by(Projects.project_id)
    )

    if project_id is not None:
        query = query.filter(Projects.project_id == project_id)

    results = query.all()

    if not results:
        raise HTTPException(status_code=404, detail="No projects found for the organization")

    response = []
    for project, total_tasks, completed_tasks in results:
        response.append(
            ProjectResponse(
                project_id=project.project_id,
                owner_user_id=project.owner_user_id,
                organization_id=project.organization_id,
                name=project.name,
                description=project.description,
                created_at=project.created_at,
                updated_at=project.updated_at,
                total_tasks=total_tasks,
                completed_tasks=completed_tasks
            )
        )

    return response



@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: UUID4 = Path(..., description="project_id of the project"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_project = db.query(Projects).filter(
        Projects.project_id == project_id,
        Projects.isDelete == False
    ).first()

    if not user_project:
        raise HTTPException(status_code=404, detail="Project not found")

    if user_project.organization_id:
        organization = db.query(Organization).filter(
            Organization.organization_id == user_project.organization_id
        ).first()

        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")

        ensure_org_owner_or_admin(db, organization, current_user.user_id)
    else:
        if user_project.owner_user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this project")

    user_project.isDelete = True
    db.commit()
    return
