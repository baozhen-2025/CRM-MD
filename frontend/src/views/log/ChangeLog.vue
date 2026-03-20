<template>
  <div>
    <div class="page-header">
      <h2>变更日志</h2>
    </div>

    <a-card size="small" style="margin-bottom: 16px">
      <a-form layout="inline">
        <a-form-item label="数据维度">
          <a-select v-model:value="filters.data_type" placeholder="全部" style="width: 120px" allowClear>
            <a-select-option value="组织架构">组织架构</a-select-option>
            <a-select-option value="客商">客商</a-select-option>
            <a-select-option value="人员">人员</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="操作类型">
          <a-select v-model:value="filters.action" placeholder="全部" style="width: 100px" allowClear>
            <a-select-option value="新增">新增</a-select-option>
            <a-select-option value="修改">修改</a-select-option>
            <a-select-option value="删除">删除</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="fetchLogs">查询</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-table :dataSource="logs" :columns="columns" :loading="loading" rowKey="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'action'">
          <a-tag :color="getActionColor(record.action)">
            {{ record.action }}
          </a-tag>
        </template>
        <template v-if="column.key === 'change_time'">
          {{ formatTime(record.change_time) }}
        </template>
        <template v-if="column.key === 'detail'">
          <a-button type="link" size="small" @click="showDetail(record)">查看</a-button>
        </template>
      </template>
    </a-table>

    <!-- 变更详情弹窗 -->
    <a-modal v-model:open="detailVisible" title="变更详情" :footer="null" width="700px">
      <div v-if="currentLog">
        <a-descriptions :column="2" bordered size="small" style="margin-bottom: 16px">
          <a-descriptions-item label="变更时间">{{ formatTime(currentLog.change_time) }}</a-descriptions-item>
          <a-descriptions-item label="操作类型">
            <a-tag :color="getActionColor(currentLog.action)">{{ currentLog.action }}</a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="数据维度">{{ currentLog.data_type }}</a-descriptions-item>
          <a-descriptions-item label="数据标识">{{ currentLog.data_name }}</a-descriptions-item>
          <a-descriptions-item label="变更来源" :span="2">{{ currentLog.change_source }}</a-descriptions-item>
        </a-descriptions>

        <a-card title="变更对比" size="small">
          <a-table
            :dataSource="changeData"
            :columns="changeColumns"
            :pagination="false"
            size="small"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'old_value'">
                <span :class="{ 'value-deleted': record.changed }">{{ record.old_value || '-' }}</span>
              </template>
              <template v-if="column.key === 'new_value'">
                <span :class="{ 'value-added': record.changed }">{{ record.new_value || '-' }}</span>
              </template>
            </template>
          </a-table>
        </a-card>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { changeLogApi } from '@/api'

const loading = ref(false)
const detailVisible = ref(false)
const logs = ref<any[]>([])
const currentLog = ref<any>(null)

const filters = reactive({
  data_type: undefined as string | undefined,
  action: undefined as string | undefined,
})

const columns = [
  { title: '变更时间', dataIndex: 'change_time', key: 'change_time', width: 180 },
  { title: '数据维度', dataIndex: 'data_type', key: 'data_type', width: 100 },
  { title: '操作类型', dataIndex: 'action', key: 'action', width: 80 },
  { title: '数据标识', dataIndex: 'data_name', key: 'data_name' },
  { title: '变更来源', dataIndex: 'change_source', key: 'change_source', width: 120 },
  { title: '详情', key: 'detail', width: 80 },
]

const changeColumns = [
  { title: '字段', dataIndex: 'field', key: 'field', width: 150 },
  { title: '变更前', dataIndex: 'old_value', key: 'old_value' },
  { title: '变更后', dataIndex: 'new_value', key: 'new_value' },
]

const changeData = computed(() => {
  if (!currentLog.value) return []
  const oldVal = currentLog.value.old_value || {}
  const newVal = currentLog.value.new_value || {}
  const allKeys = new Set([...Object.keys(oldVal), ...Object.keys(newVal)])
  return Array.from(allKeys).map(key => ({
    field: key,
    old_value: oldVal[key],
    new_value: newVal[key],
    changed: oldVal[key] !== newVal[key],
  }))
})

const getActionColor = (action: string) => {
  const colors: Record<string, string> = {
    '新增': 'green',
    '修改': 'blue',
    '删除': 'red',
  }
  return colors[action] || 'default'
}

const formatTime = (time: string) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const fetchLogs = async () => {
  loading.value = true
  try {
    const res = await changeLogApi.list({
      data_type: filters.data_type,
      action: filters.action,
    })
    logs.value = res.data
  } catch (error) {
    message.error('获取日志列表失败')
  } finally {
    loading.value = false
  }
}

const showDetail = (record: any) => {
  currentLog.value = record
  detailVisible.value = true
}

onMounted(() => {
  fetchLogs()
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
.value-deleted {
  background-color: #fff1f0;
  text-decoration: line-through;
  color: #ff4d4f;
}
.value-added {
  background-color: #f6ffed;
  color: #52c41a;
}
</style>
