<template>
  <div>
    <div class="page-header">
      <h2>匹配规则配置</h2>
      <a-space>
        <a-select
          v-model:value="selectedSourceId"
          placeholder="选择数据源"
          style="width: 200px"
          @change="fetchRules"
        >
          <a-select-option v-for="ds in dataSources" :key="ds.id" :value="ds.id">
            {{ ds.source_name }}
          </a-select-option>
        </a-select>
        <a-button type="primary" @click="showModal()" :disabled="!selectedSourceId">
          <template #icon><PlusOutlined /></template>
          新增规则
        </a-button>
      </a-space>
    </div>

    <a-alert
      v-if="!selectedSourceId"
      message="请先选择数据源"
      description="选择数据源后可配置该数据源的匹配规则"
      type="info"
      show-icon
      style="margin-bottom: 16px"
    />

    <a-table
      v-if="selectedSourceId"
      :dataSource="rules"
      :columns="columns"
      :loading="loading"
      rowKey="id"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'match_conditions'">
          <a-tag v-for="(cond, idx) in record.match_conditions" :key="idx" style="margin: 2px">
            {{ cond.source_field }} {{ cond.operator }} {{ cond.target_field }}
            <span v-if="idx < record.match_conditions.length - 1">({{ cond.logic }})</span>
          </a-tag>
        </template>
        <template v-if="column.key === 'status'">
          <a-tag :color="record.status === 1 ? 'green' : 'red'">
            {{ record.status === 1 ? '启用' : '停用' }}
          </a-tag>
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button type="link" size="small" @click="toggleStatus(record)">
              {{ record.status === 1 ? '禁用' : '启用' }}
            </a-button>
            <a-button type="link" size="small" @click="showModal(record)">编辑</a-button>
            <a-popconfirm title="确定删除?" @confirm="deleteRule(record.id)">
              <a-button type="link" size="small" danger>删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <a-modal
      v-model:open="visible"
      :title="editingId ? '编辑匹配规则' : '新增匹配规则'"
      @ok="handleSubmit"
      width="650px"
    >
      <a-form :model="form" :label-col="{ span: 4 }" :wrapper-col="{ span: 18 }">
        <a-form-item label="规则名称" required>
          <a-input v-model:value="form.rule_name" placeholder="请输入规则名称" />
        </a-form-item>

        <a-form-item label="匹配条件" required>
          <div class="condition-list">
            <div v-for="(cond, idx) in form.match_conditions" :key="idx" class="condition-item">
              <a-row :gutter="8" align="middle">
                <a-col :span="7">
                  <a-select v-model:value="cond.source_field" placeholder="一级字段" size="small">
                    <a-select-option v-for="f in sourceFields" :key="f" :value="f">{{ f }}</a-select-option>
                  </a-select>
                </a-col>
                <a-col :span="4">
                  <a-select v-model:value="cond.operator" size="small">
                    <a-select-option value="eq">等于</a-select-option>
                    <a-select-option value="ne">不等于</a-select-option>
                    <a-select-option value="like">包含</a-select-option>
                  </a-select>
                </a-col>
                <a-col :span="7">
                  <a-select v-model:value="cond.target_field" placeholder="三级字段" size="small">
                    <a-select-option v-for="f in targetFields" :key="f" :value="f">{{ f }}</a-select-option>
                  </a-select>
                </a-col>
                <a-col :span="4">
                  <a-select v-model:value="cond.logic" size="small">
                    <a-select-option value="AND">AND</a-select-option>
                    <a-select-option value="OR">OR</a-select-option>
                  </a-select>
                </a-col>
                <a-col :span="2">
                  <a-button type="text" danger size="small" @click="removeCondition(idx)">
                    <DeleteOutlined />
                  </a-button>
                </a-col>
              </a-row>
            </div>
            <a-button type="dashed" block @click="addCondition">
              <PlusOutlined /> 添加条件
            </a-button>
          </div>
        </a-form-item>

        <a-form-item label="优先级">
          <a-input-number v-model:value="form.priority" :min="1" :max="100" />
          <span class="hint">数字越小优先级越高</span>
        </a-form-item>

        <a-form-item label="状态">
          <a-switch v-model:checked="form.statusBool" checked-children="启用" un-checked-children="停用" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { matchRuleApi, dataSourceApi, fieldMappingApi } from '@/api'

const loading = ref(false)
const visible = ref(false)
const editingId = ref<number | null>(null)
const selectedSourceId = ref<number | null>(null)
const dataSources = ref<any[]>([])
const rules = ref<any[]>([])
const sourceFields = ref<string[]>(['org_code', 'org_name', 'parent_code', 'org_type'])
const targetFields = ref<string[]>(['org_code', 'org_name', 'parent_id', 'org_type_id'])

const columns = [
  { title: '规则名称', dataIndex: 'rule_name', key: 'rule_name', width: 150 },
  { title: '匹配条件', dataIndex: 'match_conditions', key: 'match_conditions' },
  { title: '优先级', dataIndex: 'priority', key: 'priority', width: 80 },
  { title: '版本', dataIndex: 'version', key: 'version', width: 60 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 80 },
  { title: '操作', key: 'action', width: 180 },
]

const form = reactive({
  rule_name: '',
  match_conditions: [] as any[],
  priority: 1,
  statusBool: true,
})

const fetchDataSources = async () => {
  try {
    const res = await dataSourceApi.list()
    dataSources.value = res.data
  } catch (error) {
    message.error('获取数据源列表失败')
  }
}

const fetchRules = async () => {
  if (!selectedSourceId.value) return
  loading.value = true
  try {
    const res = await matchRuleApi.list(selectedSourceId.value)
    rules.value = res.data
  } catch (error) {
    message.error('获取规则列表失败')
  } finally {
    loading.value = false
  }
}

const addCondition = () => {
  form.match_conditions.push({
    source_field: '',
    operator: 'eq',
    target_field: '',
    logic: 'AND',
  })
}

const removeCondition = (idx: number) => {
  form.match_conditions.splice(idx, 1)
}

const showModal = (record?: any) => {
  editingId.value = record?.id || null
  if (record) {
    Object.assign(form, {
      rule_name: record.rule_name,
      match_conditions: record.match_conditions.map((c: any) => ({ ...c })),
      priority: record.priority,
      statusBool: record.status === 1,
    })
  } else {
    Object.assign(form, {
      rule_name: '',
      match_conditions: [{ source_field: '', operator: 'eq', target_field: '', logic: 'AND' }],
      priority: 1,
      statusBool: true,
    })
  }
  visible.value = true
}

const handleSubmit = async () => {
  if (!form.rule_name || form.match_conditions.length === 0) {
    message.error('请填写完整信息')
    return
  }

  const data = {
    rule_name: form.rule_name,
    source_id: selectedSourceId.value,
    match_conditions: form.match_conditions,
    priority: form.priority,
    status: form.statusBool ? 1 : 0,
  }

  try {
    if (editingId.value) {
      await matchRuleApi.update(editingId.value, data)
      message.success('更新成功')
    } else {
      await matchRuleApi.create(data)
      message.success('创建成功')
    }
    visible.value = false
    fetchRules()
  } catch (error) {
    message.error('操作失败')
  }
}

const toggleStatus = async (record: any) => {
  try {
    await matchRuleApi.update(record.id, {
      ...record,
      status: record.status === 1 ? 0 : 1,
    })
    message.success('状态更新成功')
    fetchRules()
  } catch (error) {
    message.error('操作失败')
  }
}

const deleteRule = async (id: number) => {
  try {
    await matchRuleApi.delete(id)
    message.success('删除成功')
    fetchRules()
  } catch (error) {
    message.error('删除失败')
  }
}

onMounted(() => {
  fetchDataSources()
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
.condition-list {
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  padding: 12px;
}
.condition-item {
  margin-bottom: 8px;
}
.hint {
  margin-left: 8px;
  color: #999;
  font-size: 12px;
}
</style>
