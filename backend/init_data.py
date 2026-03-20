"""
初始化示例数据脚本
运行方式: python init_data.py
"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal, engine, Base
from app.models.models import (
    DataSource, FieldMapping, MatchRule, SyncTask,
    SyncRecord, AuditRecord, ChangeLog
)
from datetime import datetime, timedelta
import random

# 创建表
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # 检查是否已有数据
    if db.query(DataSource).count() > 0:
        print("数据已存在，跳过初始化")
    else:
        # 1. 创建数据源
        data_sources = [
            DataSource(
                source_name="一级公司-组织架构",
                source_type="组织架构",
                api_url="http://level1.company.com/api/organizations",
                request_method="POST",
                auth_type="token",
                auth_config={"token": "xxx"},
                increment_field="update_time",
                target_table="md_master_organization",
                sync_direction="download",
                status=1
            ),
            DataSource(
                source_name="一级公司-客商",
                source_type="客商",
                api_url="http://level1.company.com/api/customers",
                request_method="POST",
                auth_type="token",
                auth_config={"token": "xxx"},
                increment_field="update_time",
                target_table="md_master_customer",
                sync_direction="download",
                status=1
            ),
            DataSource(
                source_name="一级公司-人员",
                source_type="人员",
                api_url="http://level1.company.com/api/employees",
                request_method="POST",
                auth_type="token",
                auth_config={"token": "xxx"},
                increment_field="update_time",
                target_table="md_master_employee",
                sync_direction="download",
                status=1
            ),
        ]
        db.add_all(data_sources)
        db.commit()

        # 2. 创建字段映射
        field_mappings = [
            # 组织架构映射
            FieldMapping(source_id=1, source_field="org_code", target_field="org_code", field_type="string", is_match_key=True),
            FieldMapping(source_id=1, source_field="org_name", target_field="org_name", field_type="string", is_match_key=False),
            FieldMapping(source_id=1, source_field="parent_code", target_field="parent_id", field_type="string", is_match_key=False),
            FieldMapping(source_id=1, source_field="org_type", target_field="org_type_id", field_type="string", is_match_key=False, value_mapping={"总部": "1", "分公司": "2", "部门": "3"}),
            # 客商映射
            FieldMapping(source_id=2, source_field="customer_code", target_field="customer_code", field_type="string", is_match_key=True),
            FieldMapping(source_id=2, source_field="customer_name", target_field="customer_name", field_type="string", is_match_key=False),
            FieldMapping(source_id=2, source_field="credit_code", target_field="credit_code", field_type="string", is_match_key=False),
        ]
        db.add_all(field_mappings)
        db.commit()

        # 3. 创建匹配规则
        match_rules = [
            MatchRule(
                rule_name="组织编码精确匹配",
                source_id=1,
                match_conditions=[
                    {"source_field": "org_code", "operator": "eq", "target_field": "org_code", "logic": "AND"}
                ],
                priority=1,
                status=1
            ),
            MatchRule(
                rule_name="组织名称+上级匹配",
                source_id=1,
                match_conditions=[
                    {"source_field": "org_name", "operator": "eq", "target_field": "org_name", "logic": "AND"},
                    {"source_field": "parent_code", "operator": "eq", "target_field": "parent_id", "logic": "AND"}
                ],
                priority=2,
                status=1
            ),
            MatchRule(
                rule_name="客商编码匹配",
                source_id=2,
                match_conditions=[
                    {"source_field": "customer_code", "operator": "eq", "target_field": "customer_code", "logic": "AND"}
                ],
                priority=1,
                status=1
            ),
        ]
        db.add_all(match_rules)
        db.commit()

        # 4. 创建同步任务
        sync_tasks = [
            SyncTask(task_name="组织数据同步", source_id=1, cron_expr="0 2 * * *", status=1, last_execute_time=datetime.now() - timedelta(hours=5)),
            SyncTask(task_name="客商数据同步", source_id=2, cron_expr="0 3 * * *", status=1, last_execute_time=datetime.now() - timedelta(hours=4)),
            SyncTask(task_name="人员数据同步", source_id=3, cron_expr="0 4 * * *", status=1, last_execute_time=datetime.now() - timedelta(hours=3)),
        ]
        db.add_all(sync_tasks)
        db.commit()

        # 5. 创建同步记录
        sync_records = [
            SyncRecord(task_id=1, batch_no="SYNC-2024031802001", total_count=234, success_count=230, fail_count=0, pending_count=4, status="success"),
            SyncRecord(task_id=2, batch_no="SYNC-2024031803001", total_count=156, success_count=155, fail_count=1, pending_count=0, status="success"),
            SyncRecord(task_id=3, batch_no="SYNC-2024031804001", total_count=892, success_count=890, fail_count=2, pending_count=0, status="success"),
        ]
        db.add_all(sync_records)
        db.commit()

        # 6. 创建审核记录
        audit_records = [
            AuditRecord(
                sync_record_id=1,
                data_type="组织架构",
                source_data={"org_code": "ORG-NEW001", "org_name": "深圳分公司", "parent_code": "ORG-000"},
                match_status="未匹配",
                match_candidates=[{"id": 1001, "name": "深圳分公司", "similarity": 95}],
                audit_status=0
            ),
            AuditRecord(
                sync_record_id=2,
                data_type="客商",
                source_data={"customer_code": "CUS-001", "customer_name": "华为技术有限公司", "credit_code": "91440300xxx"},
                match_status="多匹配(2条)",
                match_candidates=[
                    {"id": 2001, "name": "华为技术有限公司", "similarity": 100},
                    {"id": 2002, "name": "华为技术服务有限公司", "similarity": 85}
                ],
                audit_status=0
            ),
            AuditRecord(
                sync_record_id=1,
                data_type="组织架构",
                source_data={"org_code": "ORG-NEW002", "org_name": "成都办事处", "parent_code": "ORG-001"},
                match_status="未匹配",
                match_candidates=[],
                audit_status=1,
                audit_action="new",
                auditor="admin",
                audit_time=datetime.now() - timedelta(hours=2)
            ),
        ]
        db.add_all(audit_records)
        db.commit()

        # 7. 创建变更日志
        change_logs = [
            ChangeLog(
                data_type="组织架构",
                data_id=1001,
                data_name="深圳分公司",
                action="新增",
                old_value=None,
                new_value={"org_code": "ORG-1001", "org_name": "深圳分公司", "parent_id": "ORG-000"},
                change_source="一级公司同步",
                change_time=datetime.now() - timedelta(hours=5)
            ),
            ChangeLog(
                data_type="组织架构",
                data_id=1002,
                data_name="北京分公司",
                action="修改",
                old_value={"org_name": "北京分司"},
                new_value={"org_name": "北京分公司"},
                change_source="一级公司同步",
                change_time=datetime.now() - timedelta(hours=5)
            ),
            ChangeLog(
                data_type="客商",
                data_id=2001,
                data_name="华为技术有限公司",
                action="新增",
                old_value=None,
                new_value={"customer_code": "CUS-2001", "customer_name": "华为技术有限公司"},
                change_source="一级公司同步",
                change_time=datetime.now() - timedelta(hours=4)
            ),
            ChangeLog(
                data_type="人员",
                data_id=3001,
                data_name="张三",
                action="修改",
                old_value={"department": "技术部"},
                new_value={"department": "研发部"},
                change_source="一级公司同步",
                change_time=datetime.now() - timedelta(hours=3)
            ),
        ]
        db.add_all(change_logs)
        db.commit()

        print("✅ 示例数据初始化完成！")
        print(f"  - 数据源: {len(data_sources)} 条")
        print(f"  - 字段映射: {len(field_mappings)} 条")
        print(f"  - 匹配规则: {len(match_rules)} 条")
        print(f"  - 同步任务: {len(sync_tasks)} 条")
        print(f"  - 同步记录: {len(sync_records)} 条")
        print(f"  - 审核记录: {len(audit_records)} 条")
        print(f"  - 变更日志: {len(change_logs)} 条")

finally:
    db.close()
