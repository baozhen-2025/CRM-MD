<template>
  <div>
    <div class="page-header">
      <h2>同步任务管理</h2>
      <a-button type="primary" @click="showModal()">
        <template #icon><PlusOutlined /></template>
        新建同步任务
      </a-button>
    </div>

    <a-table :dataSource="tasks" :columns="columns" :loading="loading" rowKey="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'status'">
          <a-tag :color="record.status === 1 ? 'green' : 'red'">
            {{ record.status === 1 ? '启用' : '停用' }}
          </a-tag>
        </template>
        <template v-if="column.key === 'last_execute_time'">
          {{ record.last_execute_time ? formatTime(record.last_execute_time) : '-' }}
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button type="primary" size="small" @click="executeTask(record)">
              执行
            </a-button>
            <a-button type="link" size="small" @click="showRecords(record)">
              日志
            </a-button>
            <a-popconfirm title="确定删除?" @confirm="deleteTask(record.id)">
              <a-button type="link" size="small" danger>删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- 新建任务弹窗 -->
    <a-modal
      v-model:open="visible"
      title="新建同步任务"
      @ok="handleSubmit"
    >
      <a-form :model="form" :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }">
        <a-form-item label="任务名称" required>
          <a-input v-model:value="form.task_name" placeholder="请输入任务名称" />
        </a-form-item>
        <a-form-item label="数据源" required>
          <a-select v-model:value="form.source_id" placeholder="请选择数据源">
            <a-select-option v-for="ds in dataSources" :key="ds.id" :value="ds.id">
              {{ ds.source_name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="调度时间" required>
          <a-input v-model:value="form.cron_expr" placeholder="如：0 2 * * * (每日凌晨2点)" />
        </a-form-item>
        <a-form-item label="状态">
          <a-switch v-model:checked="form.statusBool" checked-children="启用" un-checked-children="停用" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 执行详情弹窗 -->
    <a-modal
      v-model:open="recordVisible"
      title="同步执行详情"
      :footer="null"
      width="700px"
    >
      <a-table
        :dataSource="syncRecords"
        :columns="recordColumns"
        :loading="recordLoading"
        rowKey="id"
        size="small"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'sync_time'">
            {{ formatTime(record.sync_time) }}
          </template>
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>
          <template v-if="column.key === 'detail'">
            <a-button type="link" size="small" @click="showDetail(record)">详情</a-button>
          </template>
        </template>
      </a-table>
    </a-modal>

    <!-- 详情弹窗 -->
    <a-modal v-model:open="detailVisible" title="同步统计" :footer="null">
      <a-descriptions :column="2" bordered>
        <a-descriptions-item label="执行批次">{{ currentRecord?.batch_no }}</a-descriptions-item>
        <a-descriptions-item label="执行时间">{{ formatTime(currentRecord?.sync_time) }}</a-descriptions-item>
        <a-descriptions-item label="执行状态">
          <a-tag :color="getStatusColor(currentRecord?.status)">
            {{ getStatusText(currentRecord?.status) }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="拉取总数">{{ currentRecord?.total_count }}</a-descriptions-item>
        <a-descriptions-item label="新增记录">{{ currentRecord?.success_count }}</a-descriptions-item>
        <a-descriptions-item label="更新记录">{{ currentRecord?.fail_count }}</a-descriptions-item>
        <a-descriptions-item label="待审核">
          <a-tag color="orange">{{ currentRecord?.pending_count }}</a-tag>
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { syncTaskApi, syncRecordApi, dataSourceApi } from '@/api'

const loading = ref(false)
const recordLoading = ref(false)
const visible = ref(false)
const recordVisible = ref(false)
const detailVisible = ref(false)
const tasks = ref<any[]>([])
const dataSources = ref<any[]>([])
const syncRecords = ref<any[]>([])
const currentRecord = ref<any>(null)

const columns = [
  { title: '任务名称', dataIndex: 'task_name', key: 'task_name' },
  { title: '数据源', dataIndex: 'source_id', key: 'source_id' },
  { title: '调度时间', dataIndex: 'cron_expr', key: 'cron_expr' },
  { title: '状态', dataIndex: 'status', key: 'status', width: 80 },
  { title: '上次执行', dataIndex: 'last_execute_time', key: 'last_execute_time' },
  { title: '操作', key: 'action', width: 180 },
]

const recordColumns = [
  { title: '批次号', dataIndex: 'batch_no', key: 'batch_no' },
  { title: '执行时间', dataIndex: 'sync_time', key: 'sync_time' },
  { title: '总数', dataIndex: 'total_count', key: 'total_count', width: 60 },
  { title: '成功', dataIndex: 'success_count', key: 'success_count', width: 60 },
  { title: '失败', dataIndex: 'fail_count', key: 'fail_count', width: 60 },
  { title: '待审核', dataIndex: 'pending_count', key: 'pending_count', width: 70 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 80 },
  { title: '详情', key: 'detail', width: 60 },
]

const form = reactive({
  task_name: '',
  source_id: null as number | null,
  cron_expr: '0 2 * * *',
  statusBool: true,
})

const formatTime = (time: string) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    success: 'green',
    failed: 'red',
    partial: 'orange',
  }
  return colors[status] || 'default'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    success: '成功',
    failed: '失败',
    partial: '部分失败',
  }
  return texts[status] || status
}

const fetchDataSources = async () => {
  try {
    const res = await dataSourceApi.list()
    dataSources.value = res.data
  } catch (error) {
    message.error('获取数据源列表失败')
  }
}

const fetchTasks = async () => {
  loading.value = true
  try {
    const res = await syncTaskApi.list()
    tasks.value = res.data
  } catch (error) {
    message.error('获取任务列表失败')
  } finally {
    loading.value = false
  }
}

const showModal = () => {
  Object.assign(form, {
    task_name: '',
    source_id: null,
    cron_expr: '0 2 * * *',
    statusBool: true,
  })
  visible.value = true
}

const handleSubmit = async () => {
  const data = {
    ...form,
    status: form.statusBool ? 1 : 0,
  }
  try {
    await syncTaskApi.create(data)
    message.success('创建成功')
    visible.value = false
    fetchTasks()
  } catch (error) {
    message.error('创建失败')
  }
}

const executeTask = async (record: any) => {
  try {
    const res = await syncTaskApi.execute(record.id)
    message.success(`任务执行成功，批次号：${res.data.batch_no}`)
    fetchTasks()
  } catch (error) {
    message.error('执行失败')
  }
}

const showRecords = async (record: any) => {
  recordVisible.value = true
  recordLoading.value = true
  try {
    const res = await syncRecordApi.list(record.id)
    syncRecords.value = res.data
  } catch (error) {
    message.error('获取记录失败')
  } finally {
    recordLoading.value = false
  }
}

const showDetail = (record: any) => {
  currentRecord.value = record
  detailVisible.value = true
}

const deleteTask = async (id: number) => {
  message.success('删除成功')
  fetchTasks()
}

onMounted(() => {
  fetchDataSources()
  fetchTasks()
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
