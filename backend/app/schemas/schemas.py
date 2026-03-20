from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

# ============ DataSource Schemas ============
class DataSourceBase(BaseModel):
    source_name: str
    source_type: str
    api_url: str
    request_method: str = "POST"
    auth_type: str
    auth_config: Optional[dict] = None
    increment_field: Optional[str] = None
    target_table: Optional[str] = None
    sync_direction: str = "download"
    status: int = 1

class DataSourceCreate(DataSourceBase):
    pass

class DataSourceUpdate(BaseModel):
    source_name: Optional[str] = None
    source_type: Optional[str] = None
    api_url: Optional[str] = None
    request_method: Optional[str] = None
    auth_type: Optional[str] = None
    auth_config: Optional[dict] = None
    increment_field: Optional[str] = None
    target_table: Optional[str] = None
    sync_direction: Optional[str] = None
    status: Optional[int] = None

class DataSourceResponse(DataSourceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ============ FieldMapping Schemas ============
class FieldMappingBase(BaseModel):
    source_id: int
    source_field: str
    target_field: str
    field_type: Optional[str] = None
    is_match_key: bool = False
    value_mapping: Optional[dict] = None

class FieldMappingCreate(FieldMappingBase):
    pass

class FieldMappingResponse(FieldMappingBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ============ MatchRule Schemas ============
class MatchCondition(BaseModel):
    source_field: str
    operator: str = "eq"
    target_field: str
    logic: str = "AND"

class MatchRuleBase(BaseModel):
    rule_name: str
    source_id: int
    match_conditions: List[MatchCondition]
    priority: int = 1
    status: int = 1

class MatchRuleCreate(MatchRuleBase):
    pass

class MatchRuleResponse(MatchRuleBase):
    id: int
    version: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ============ SyncTask Schemas ============
class SyncTaskBase(BaseModel):
    task_name: str
    source_id: int
    cron_expr: str
    status: int = 1

class SyncTaskCreate(SyncTaskBase):
    pass

class SyncTaskResponse(SyncTaskBase):
    id: int
    last_execute_time: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ============ SyncRecord Schemas ============
class SyncRecordResponse(BaseModel):
    id: int
    task_id: int
    batch_no: str
    sync_time: datetime
    total_count: int
    success_count: int
    fail_count: int
    pending_count: int
    status: str

    class Config:
        from_attributes = True

# ============ AuditRecord Schemas ============
class AuditRecordResponse(BaseModel):
    id: int
    sync_record_id: int
    data_type: str
    source_data: dict
    match_status: str
    match_candidates: Optional[List[dict]] = None
    audit_status: int
    audit_action: Optional[str] = None
    bind_target_id: Optional[int] = None
    auditor: Optional[str] = None
    audit_time: Optional[datetime] = None
    audit_remark: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AuditAction(BaseModel):
    action: str  # new / bind / skip / reject
    bind_target_id: Optional[int] = None
    remark: Optional[str] = None

# ============ ChangeLog Schemas ============
class ChangeLogResponse(BaseModel):
    id: int
    data_type: str
    data_id: int
    data_name: str
    action: str
    old_value: Optional[dict] = None
    new_value: Optional[dict] = None
    change_time: datetime
    change_source: str

    class Config:
        from_attributes = True
