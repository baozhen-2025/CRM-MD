<template>
  <div>
    <div class="page-header">
      <h2>数据源管理</h2>
      <a-button type="primary" @click="showModal()">
        <template #icon><PlusOutlined /></template>
        新增数据源
      </a-button>
    </div>

    <a-table :dataSource="dataSources" :columns="columns" :loading="loading" rowKey="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'sync_direction'">
          <a-tag :color="record.sync_direction === 'download' ? 'blue' : 'green'">
            {{ record.sync_direction === 'download' ? '下发同步' : '上报同步' }}
          </a-tag>
        </template>
        <template v-if="column.key === 'status'">
          <a-tag :color="record.status === 1 ? 'green' : 'red'">
            {{ record.status === 1 ? '启用' : '停用' }}
          </a-tag>
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button type="link" size="small" @click="testConnection(record)">测试连接</a-button>
            <a-button type="link" size="small" @click="showModal(record)">编辑</a-button>
            <a-popconfirm title="确定删除?" @confirm="deleteSource(record.id)">
              <a-button type="link" size="small" danger>删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <a-modal
      v-model:open="visible"
      :title="editingId ? '编辑数据源' : '新增数据源'"
      @ok="handleSubmit"
      width="650px"
    >
      <a-form :model="form" :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }">
        <a-form-item label="数据源名称" required>
          <a-input v-model:value="form.source_name" placeholder="请输入数据源名称" />
        </a-form-item>
        <a-form-item label="同步方向" required>
          <a-select v-model:value="form.sync_direction" placeholder="请选择同步方向">
            <a-select-option value="download">下发同步（一级公司 → 三级公司）</a-select-option>
            <a-select-option value="upload">上报同步（三级公司 → 一级公司）</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="数据维度" required>
          <a-select v-model:value="form.source_type" placeholder="请选择数据维度" @change="handleSourceTypeChange">
            <a-select-option value="组织架构">组织架构</a-select-option>
            <a-select-option value="客商">客商</a-select-option>
            <a-select-option value="人员">人员</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="目标主数据表" required>
          <a-select v-model:value="form.target_table" placeholder="请选择目标主数据表">
            <a-select-option v-for="table in targetTableOptions" :key="table.value" :value="table.value">
              {{ table.label }}
            </a-select-option>
          </a-select>
          <div class="field-hint">数据将同步到此主数据表</div>
        </a-form-item>
        <a-form-item label="接口地址" required>
          <a-input v-model:value="form.api_url" placeholder="请输入API接口地址" />
        </a-form-item>
        <a-form-item label="请求方式">
          <a-select v-model:value="form.request_method">
            <a-select-option value="GET">GET</a-select-option>
            <a-select-option value="POST">POST</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="认证方式">
          <a-select v-model:value="form.auth_type">
            <a-select-option value="none">无认证</a-select-option>
            <a-select-option value="token">Token认证</a-select-option>
            <a-select-option value="basic">Basic认证</a-select-option>
            <a-select-option value="oauth2">OAuth2</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="Token值" v-if="form.auth_type === 'token'">
          <a-input-password v-model:value="form.auth_config.token" placeholder="请输入Token" />
        </a-form-item>
        <a-form-item label="增量标识字段">
          <a-input v-model:value="form.increment_field" placeholder="如：update_time" />
        </a-form-item>
        <a-form-item label="状态">
          <a-switch v-model:checked="form.statusBool" checked-children="启用" un-checked-children="停用" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { dataSourceApi } from '@/api'

const loading = ref(false)
const visible = ref(false)
const editingId = ref<number | null>(null)
const dataSources = ref<any[]>([])

const columns = [
  { title: '序号', dataIndex: 'id', key: 'id', width: 60 },
  { title: '数据源名称', dataIndex: 'source_name', key: 'source_name', width: 150 },
  { title: '同步方向', dataIndex: 'sync_direction', key: 'sync_direction', width: 120 },
  { title: '数据维度', dataIndex: 'source_type', key: 'source_type', width: 100 },
  { title: '目标主数据表', dataIndex: 'target_table', key: 'target_table', width: 180 },
  { title: '接口地址', dataIndex: 'api_url', key: 'api_url', ellipsis: true },
  { title: '状态', dataIndex: 'status', key: 'status', width: 80 },
  { title: '操作', key: 'action', width: 180 },
]

// 目标表选项（根据数据维度筛选）
const allTargetTables = [
  { value: 'md_master_organization', label: '组织架构主数据表 (md_master_organization)', type: '组织架构' },
  { value: 'md_master_customer', label: '客商主数据表 (md_master_customer)', type: '客商' },
  { value: 'md_master_employee', label: '人员主数据表 (md_master_employee)', type: '人员' },
]

const targetTableOptions = computed(() => {
  if (!form.source_type) return allTargetTables
  return allTargetTables.filter(t => t.type === form.source_type)
})

const form = reactive({
  source_name: '',
  source_type: '',
  api_url: '',
  request_method: 'POST',
  auth_type: 'none',
  auth_config: {} as any,
  increment_field: '',
  target_table: '',
  sync_direction: 'download',
  statusBool: true,
})

const handleSourceTypeChange = () => {
  // 切换数据维度时，自动匹配目标表
  const matched = allTargetTables.find(t => t.type === form.source_type)
  if (matched) {
    form.target_table = matched.value
  } else {
    form.target_table = ''
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await dataSourceApi.list()
    dataSources.value = res.data
  } catch (error) {
    message.error('获取数据源列表失败')
  } finally {
    loading.value = false
  }
}

const showModal = (record?: any) => {
  editingId.value = record?.id || null
  if (record) {
    Object.assign(form, {
      ...record,
      auth_config: record.auth_config || {},
      statusBool: record.status === 1,
    })
  } else {
    Object.assign(form, {
      source_name: '',
      source_type: '',
      api_url: '',
      request_method: 'POST',
      auth_type: 'none',
      auth_config: {},
      increment_field: '',
      target_table: '',
      sync_direction: 'download',
      statusBool: true,
    })
  }
  visible.value = true
}

const handleSubmit = async () => {
  if (!form.source_name || !form.source_type || !form.api_url || !form.target_table) {
    message.error('请填写必填项')
    return
  }

  const data = {
    ...form,
    status: form.statusBool ? 1 : 0,
  }
  try {
    if (editingId.value) {
      await dataSourceApi.update(editingId.value, data)
      message.success('更新成功')
    } else {
      await dataSourceApi.create(data)
      message.success('创建成功')
    }
    visible.value = false
    fetchData()
  } catch (error) {
    message.error('操作失败')
  }
}

const testConnection = async (record: any) => {
  try {
    const res = await dataSourceApi.test(record.id)
    if (res.data.success) {
      message.success(`连接成功，延迟: ${res.data.latency}ms`)
    }
  } catch (error) {
    message.error('连接失败')
  }
}

const deleteSource = async (id: number) => {
  try {
    await dataSourceApi.delete(id)
    message.success('删除成功')
    fetchData()
  } catch (error) {
    message.error('删除失败')
  }
}

onMounted(() => {
  fetchData()
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
.field-hint {
  color: #999;
  font-size: 12px;
  margin-top: 4px;
}
</style>
