<template>
  <div>
    <div class="page-header">
      <h2>人工审核</h2>
      <a-space>
        <a-select v-model:value="filterStatus" placeholder="审核状态" style="width: 120px" @change="fetchRecords">
          <a-select-option :value="0">待审核</a-select-option>
          <a-select-option :value="1">已通过</a-select-option>
          <a-select-option :value="2">已拒绝</a-select-option>
          <a-select-option :value="undefined">全部</a-select-option>
        </a-select>
      </a-space>
    </div>

    <a-table :dataSource="records" :columns="columns" :loading="loading" rowKey="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'source_data'">
          <a-tag>{{ record.source_data?.name || record.source_data?.org_name || '-' }}</a-tag>
        </template>
        <template v-if="column.key === 'match_status'">
          <a-tag :color="record.match_status === '未匹配' ? 'orange' : 'blue'">
            {{ record.match_status }}
          </a-tag>
        </template>
        <template v-if="column.key === 'audit_status'">
          <a-tag :color="getAuditStatusColor(record.audit_status)">
            {{ getAuditStatusText(record.audit_status) }}
          </a-tag>
        </template>
        <template v-if="column.key === 'action'">
          <a-button
            type="primary"
            size="small"
            @click="showAudit(record)"
            :disabled="record.audit_status !== 0"
          >
            审核
          </a-button>
        </template>
      </template>
    </a-table>

    <!-- 审核弹窗 -->
    <a-modal
      v-model:open="auditVisible"
      title="人工审核"
      @ok="handleAudit"
      width="600px"
    >
      <div v-if="currentRecord">
        <a-alert
          :type="currentRecord.match_status === '未匹配' ? 'warning' : 'info'"
          :message="'问题类型：' + currentRecord.match_status"
          style="margin-bottom: 16px"
        />

        <a-card title="一级公司数据（源数据）" size="small" style="margin-bottom: 16px">
          <a-descriptions :column="1" size="small">
            <a-descriptions-item
              v-for="(value, key) in currentRecord.source_data"
              :key="key"
              :label="key"
            >
              {{ value }}
            </a-descriptions-item>
          </a-descriptions>
        </a-card>

        <a-card title="处理方式" size="small">
          <a-radio-group v-model:value="auditForm.action">
            <a-radio value="new">新增为新记录</a-radio>
            <a-radio value="bind">绑定到已有记录</a-radio>
            <a-radio value="skip">跳过</a-radio>
            <a-radio value="reject">拒绝</a-radio>
          </a-radio-group>

          <div v-if="auditForm.action === 'bind'" style="margin-top: 16px">
            <a-select
              v-model:value="auditForm.bind_target_id"
              placeholder="选择要绑定的记录"
              style="width: 100%"
            >
              <a-select-option
                v-for="item in currentRecord.match_candidates || []"
                :key="item.id"
                :value="item.id"
              >
                {{ item.name }} (相似度: {{ item.similarity }}%)
              </a-select-option>
            </a-select>
          </div>

          <a-textarea
            v-model:value="auditForm.remark"
            placeholder="审核意见（可选）"
            :rows="2"
            style="margin-top: 16px"
          />
        </a-card>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { auditRecordApi } from '@/api'

const loading = ref(false)
const auditVisible = ref(false)
const filterStatus = ref(0)
const records = ref<any[]>([])
const currentRecord = ref<any>(null)

const columns = [
  { title: '批次号', dataIndex: 'sync_record_id', key: 'sync_record_id', width: 120 },
  { title: '数据维度', dataIndex: 'data_type', key: 'data_type', width: 100 },
  { title: '源数据', dataIndex: 'source_data', key: 'source_data' },
  { title: '问题类型', dataIndex: 'match_status', key: 'match_status', width: 100 },
  { title: '审核状态', dataIndex: 'audit_status', key: 'audit_status', width: 100 },
  { title: '审核人', dataIndex: 'auditor', key: 'auditor', width: 80 },
  { title: '操作', key: 'action', width: 80 },
]

const auditForm = reactive({
  action: 'new',
  bind_target_id: null as number | null,
  remark: '',
})

const getAuditStatusColor = (status: number) => {
  const colors = ['orange', 'green', 'red']
  return colors[status] || 'default'
}

const getAuditStatusText = (status: number) => {
  const texts = ['待审核', '已通过', '已拒绝']
  return texts[status] || '未知'
}

const fetchRecords = async () => {
  loading.value = true
  try {
    const res = await auditRecordApi.list(filterStatus.value)
    records.value = res.data
  } catch (error) {
    message.error('获取审核列表失败')
  } finally {
    loading.value = false
  }
}

const showAudit = (record: any) => {
  currentRecord.value = record
  Object.assign(auditForm, {
    action: 'new',
    bind_target_id: null,
    remark: '',
  })
  auditVisible.value = true
}

const handleAudit = async () => {
  if (!currentRecord.value) return

  try {
    await auditRecordApi.audit(currentRecord.value.id, {
      action: auditForm.action,
      bind_target_id: auditForm.bind_target_id,
      remark: auditForm.remark,
    })
    message.success('审核成功')
    auditVisible.value = false
    fetchRecords()
  } catch (error) {
    message.error('审核失败')
  }
}

onMounted(() => {
  fetchRecords()
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.page-header h2 {
  margin: 0;
}
</style>
