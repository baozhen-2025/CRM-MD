from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, SmallInteger
from sqlalchemy.sql import func
from ..database import Base

class DataSource(Base):
    """数据源配置表"""
    __tablename__ = "md_data_source"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(100), nullable=False, comment="数据源名称")
    source_type = Column(String(50), comment="数据维度：组织架构/客商/人员")
    api_url = Column(String(500), comment="接口地址")
    request_method = Column(String(10), default="POST")
    auth_type = Column(String(50), comment="认证方式")
    auth_config = Column(JSON, comment="认证配置")
    increment_field = Column(String(50), comment="增量标识字段")
    target_table = Column(String(100), comment="目标主数据表名")
    sync_direction = Column(String(20), default="download", comment="同步方向：download下发/upload上报")
    status = Column(SmallInteger, default=1, comment="状态:1启用,0停用")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class FieldMapping(Base):
    """字段映射配置表"""
    __tablename__ = "md_field_mapping"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, comment="数据源ID")
    source_field = Column(String(100), comment="一级公司字段名")
    target_field = Column(String(100), comment="三级公司字段名")
    field_type = Column(String(50), comment="字段类型")
    is_match_key = Column(Boolean, default=False, comment="是否匹配主键")
    value_mapping = Column(JSON, comment="值映射配置")
    created_at = Column(DateTime, server_default=func.now())


class MatchRule(Base):
    """匹配规则配置表"""
    __tablename__ = "md_match_rule"

    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(100), nullable=False, comment="规则名称")
    source_id = Column(Integer, comment="数据源ID")
    match_conditions = Column(JSON, comment="匹配条件列表")
    priority = Column(Integer, default=1, comment="优先级")
    status = Column(SmallInteger, default=1, comment="状态")
    version = Column(Integer, default=1, comment="版本号")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class SyncTask(Base):
    """同步任务表"""
    __tablename__ = "md_sync_task"

    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String(100), nullable=False, comment="任务名称")
    source_id = Column(Integer, comment="数据源ID")
    cron_expr = Column(String(50), comment="调度表达式")
    status = Column(SmallInteger, default=1, comment="状态")
    last_execute_time = Column(DateTime, comment="上次执行时间")
    created_at = Column(DateTime, server_default=func.now())


class SyncRecord(Base):
    """同步记录表"""
    __tablename__ = "md_sync_record"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, comment="任务ID")
    batch_no = Column(String(50), comment="批次号")
    sync_time = Column(DateTime, server_default=func.now())
    total_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    fail_count = Column(Integer, default=0)
    pending_count = Column(Integer, default=0)
    status = Column(String(20), default="success")


class AuditRecord(Base):
    """人工审核表"""
    __tablename__ = "md_audit_record"

    id = Column(Integer, primary_key=True, index=True)
    sync_record_id = Column(Integer, comment="同步记录ID")
    data_type = Column(String(50), comment="数据维度")
    source_data = Column(JSON, comment="源数据")
    match_status = Column(String(50), comment="匹配状态")
    match_candidates = Column(JSON, comment="候选匹配数据")
    audit_status = Column(SmallInteger, default=0, comment="审核状态:0待审,1通过,2拒绝")
    audit_action = Column(String(50), comment="审核操作:new/bind/skip")
    bind_target_id = Column(Integer, comment="绑定目标ID")
    auditor = Column(String(50), comment="审核人")
    audit_time = Column(DateTime)
    audit_remark = Column(Text, comment="审核意见")
    created_at = Column(DateTime, server_default=func.now())


class ChangeLog(Base):
    """变更日志表"""
    __tablename__ = "md_change_log"

    id = Column(Integer, primary_key=True, index=True)
    data_type = Column(String(50), comment="数据维度")
    data_id = Column(Integer, comment="数据ID")
    data_name = Column(String(200), comment="数据标识")
    action = Column(String(20), comment="操作类型")
    old_value = Column(JSON, comment="旧值")
    new_value = Column(JSON, comment="新值")
    change_time = Column(DateTime, server_default=func.now())
    change_source = Column(String(50), comment="变更来源")
