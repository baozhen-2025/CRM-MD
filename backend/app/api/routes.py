from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import random

from ..database import get_db
from ..models.models import (
    DataSource, FieldMapping, MatchRule, SyncTask,
    SyncRecord, AuditRecord, ChangeLog
)
from ..schemas.schemas import (
    DataSourceCreate, DataSourceUpdate, DataSourceResponse,
    FieldMappingCreate, FieldMappingResponse,
    MatchRuleCreate, MatchRuleResponse,
    SyncTaskCreate, SyncTaskResponse,
    SyncRecordResponse, AuditRecordResponse, AuditAction,
    ChangeLogResponse
)

router = APIRouter()

# ============ DataSource API ============
@router.get("/datasources", response_model=List[DataSourceResponse])
def get_datasources(db: Session = Depends(get_db)):
    return db.query(DataSource).all()

@router.post("/datasources", response_model=DataSourceResponse)
def create_datasource(data: DataSourceCreate, db: Session = Depends(get_db)):
    db_obj = DataSource(**data.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.put("/datasources/{id}", response_model=DataSourceResponse)
def update_datasource(id: int, data: DataSourceUpdate, db: Session = Depends(get_db)):
    db_obj = db.query(DataSource).filter(DataSource.id == id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="数据源不存在")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(db_obj, key, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.delete("/datasources/{id}")
def delete_datasource(id: int, db: Session = Depends(get_db)):
    db_obj = db.query(DataSource).filter(DataSource.id == id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="数据源不存在")
    db.delete(db_obj)
    db.commit()
    return {"success": True}

@router.post("/datasources/{id}/test")
def test_datasource(id: int, db: Session = Depends(get_db)):
    db_obj = db.query(DataSource).filter(DataSource.id == id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="数据源不存在")
    # 模拟连接测试
    return {"success": True, "message": "连接成功", "latency": random.randint(50, 200)}

# ============ FieldMapping API ============
@router.get("/fieldmappings", response_model=List[FieldMappingResponse])
def get_fieldmappings(source_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(FieldMapping)
    if source_id:
        query = query.filter(FieldMapping.source_id == source_id)
    return query.all()

@router.post("/fieldmappings", response_model=FieldMappingResponse)
def create_fieldmapping(data: FieldMappingCreate, db: Session = Depends(get_db)):
    db_obj = FieldMapping(**data.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.put("/fieldmappings/{id}", response_model=FieldMappingResponse)
def update_fieldmapping(id: int, data: FieldMappingCreate, db: Session = Depends(get_db)):
    db_obj = db.query(FieldMapping).filter(FieldMapping.id == id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="映射配置不存在")
    for key, value in data.dict().items():
        setattr(db_obj, key, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.delete("/fieldmappings/{id}")
def delete_fieldmapping(id: int, db: Session = Depends(get_db)):
    db_obj = db.query(FieldMapping).filter(FieldMapping.id == id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="映射配置不存在")
    db.delete(db_obj)
    db.commit()
    return {"success": True}

# ============ MatchRule API ============
@router.get("/matchrules", response_model=List[MatchRuleResponse])
def get_matchrules(source_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(MatchRule)
    if source_id:
        query = query.filter(MatchRule.source_id == source_id)
    return query.all()

@router.post("/matchrules", response_model=MatchRuleResponse)
def create_matchrule(data: MatchRuleCreate, db: Session = Depends(get_db)):
    db_obj = MatchRule(**data.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.put("/matchrules/{id}", response_model=MatchRuleResponse)
def update_matchrule(id: int, data: MatchRuleCreate, db: Session = Depends(get_db)):
    db_obj = db.query(MatchRule).filter(MatchRule.id == id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="规则不存在")
    for key, value in data.dict().items():
        setattr(db_obj, key, value)
    db_obj.version += 1
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.delete("/matchrules/{id}")
def delete_matchrule(id: int, db: Session = Depends(get_db)):
    db_obj = db.query(MatchRule).filter(MatchRule.id == id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="规则不存在")
    db.delete(db_obj)
    db.commit()
    return {"success": True}

# ============ SyncTask API ============
@router.get("/synctasks", response_model=List[SyncTaskResponse])
def get_synctasks(db: Session = Depends(get_db)):
    return db.query(SyncTask).all()

@router.post("/synctasks", response_model=SyncTaskResponse)
def create_synctask(data: SyncTaskCreate, db: Session = Depends(get_db)):
    db_obj = SyncTask(**data.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.post("/synctasks/{id}/execute")
def execute_synctask(id: int, db: Session = Depends(get_db)):
    task = db.query(SyncTask).filter(SyncTask.id == id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 模拟执行同步
    batch_no = f"SYNC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    record = SyncRecord(
        task_id=id,
        batch_no=batch_no,
        total_count=random.randint(100, 500),
        success_count=random.randint(80, 450),
        fail_count=random.randint(0, 5),
        pending_count=random.randint(0, 10),
        status="success"
    )
    task.last_execute_time = datetime.now()
    db.add(record)
    db.commit()

    return {
        "success": True,
        "batch_no": batch_no,
        "record_id": record.id
    }

# ============ SyncRecord API ============
@router.get("/syncrecords", response_model=List[SyncRecordResponse])
def get_syncrecords(task_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(SyncRecord).order_by(SyncRecord.sync_time.desc())
    if task_id:
        query = query.filter(SyncRecord.task_id == task_id)
    return query.limit(50).all()

# ============ AuditRecord API ============
@router.get("/auditrecords", response_model=List[AuditRecordResponse])
def get_auditrecords(status: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(AuditRecord).order_by(AuditRecord.created_at.desc())
    if status is not None:
        query = query.filter(AuditRecord.audit_status == status)
    return query.limit(100).all()

@router.post("/auditrecords/{id}/audit")
def audit_record(id: int, data: AuditAction, db: Session = Depends(get_db)):
    record = db.query(AuditRecord).filter(AuditRecord.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="审核记录不存在")

    record.audit_status = 1 if data.action in ["new", "bind"] else 2
    record.audit_action = data.action
    record.bind_target_id = data.bind_target_id
    record.audit_remark = data.remark
    record.auditor = "admin"
    record.audit_time = datetime.now()
    db.commit()

    return {"success": True}

# ============ ChangeLog API ============
@router.get("/changelogs", response_model=List[ChangeLogResponse])
def get_changelogs(
    data_type: Optional[str] = None,
    action: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ChangeLog).order_by(ChangeLog.change_time.desc())
    if data_type:
        query = query.filter(ChangeLog.data_type == data_type)
    if action:
        query = query.filter(ChangeLog.action == action)
    return query.limit(100).all()
