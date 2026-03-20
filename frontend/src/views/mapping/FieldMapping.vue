<template>
  <div>
    <div class="page-header">
      <h2>字段映射配置</h2>
      <a-space>
        <a-select
          v-model:value="selectedSourceId"
          placeholder="选择数据源"
          style="width: 200px"
          @change="fetchMappings"
        >
          <a-select-option v-for="ds in dataSources" :key="ds.id" :value="ds.id">
            {{ ds.source_name }}
          </a-select-option>
        </a-select>
        <a-button type="primary" @click="showModal()" :disabled="!selectedSourceId">
          <template #icon><PlusOutlined /></template>
          添加字段映射
        </a-button>
      </a-space>
    </div>

    <a-alert
      v-if="!selectedSourceId"
      message="请先选择数据源"
      description="选择数据源后可配置该数据源的字段映射关系"
      type="info"
      show-icon
      style="margin-bottom: 16px"
    />

    <a-table
      v-if="selectedSourceId"
      :dataSource="mappings"
      :columns="columns"
      :loading="loading"
      rowKey="id"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'is_match_key'">
          <a-tag :color="record.is_match_key ? 'blue' : 'default'">
            {{ record.is_match_key ? '是' : '否' }}
          </a-tag>
        </template>
        <template v-if="column.key === 'value_mapping'">
          <a-button
            v-if="record.value_mapping"
            type="link"
            size="small"
            @click="showValueMapping(record)"
          >
            查看映射 ({{ Object.keys(record.value_mapping).length }})
          </a-button>
          <span v-else>-</span>
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button type="link" size="small" @click="showModal(record)">编辑</a-button>
            <a-popconfirm title="确定删除?" @confirm="deleteMapping(record.id)">
              <a-button type="link" size="small" danger>删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <a-modal
      v-model:open="visible"
      :title="editingId ? '编辑字段映射' : '添加字段映射'"
      @ok="handleSubmit"
    >
      <a-form :model="form" :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }">
        <a-form-item label="一级公司字段" required>
          <a-input v-model:value="form.source_field" placeholder="如：org_code" />
        </a-form-item>
        <a-form-item label="三级公司字段" required>
          <a-input v-model:value="form.target_field" placeholder="如：org_code" />
        </a-form-item>
        <a-form-item label="字段类型">
          <a-select v-model:value="form.field_type">
            <a-select-option value="string">字符串</a-select-option>
            <a-select-option value="number">数字</a-select-option>
            <a-select-option value="date">日期</a-select-option>
            <a-select-option value="boolean">布尔</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="作为匹配主键">
          <a-switch v-model:checked="form.is_match_key" />
        </a-form-item>
        <a-form-item label="值映射配置">
          <a-textarea
            v-model:value="valueMappingStr"
            placeholder="JSON格式，如：{'总部':'1','分公司':'2'}"
            :rows="3"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <a-modal v-model:open="valueMappingVisible" title="值映射详情" :footer="null">
      <a-descriptions :column="1" bordered size="small">
        <a-descriptions-item
          v-for="(value, key) in currentValueMapping"
          :key="key"
          :label="key"
        >
          {{ value }}
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { fieldMappingApi, dataSourceApi } from '@/api'

const loading = ref(false)
const visible = ref(false)
const valueMappingVisible = ref(false)
const editingId = ref<number | null>(null)
const selectedSourceId = ref<number | null>(null)
const dataSources = ref<any[]>([])
const mappings = ref<any[]>([])
const currentValueMapping = ref<any>({})

const columns = [
  { title: '一级公司字段', dataIndex: 'source_field', key: 'source_field' },
  { title: '三级公司字段', dataIndex: 'target_field', key: 'target_field' },
  { title: '字段类型', dataIndex: 'field_type', key: 'field_type', width: 100 },
  { title: '匹配主键', dataIndex: 'is_match_key', key: 'is_match_key', width: 100 },
  { title: '值映射', dataIndex: 'value_mapping', key: 'value_mapping', width: 120 },
  { title: '操作', key: 'action', width: 120 },
]

const form = reactive({
  source_field: '',
  target_field: '',
  field_type: 'string',
  is_match_key: false,
})

const valueMappingStr = ref('')

const fetchDataSources = async () => {
  try {
    const res = await dataSourceApi.list()
    dataSources.value = res.data
  } catch (error) {
    message.error('获取数据源列表失败')
  }
}

const fetchMappings = async () => {
  if (!selectedSourceId.value) return
  loading.value = true
  try {
    const res = await fieldMappingApi.list(selectedSourceId.value)
    mappings.value = res.data
  } catch (error) {
    message.error('获取映射列表失败')
  } finally {
    loading.value = false
  }
}

const showModal = (record?: any) => {
  editingId.value = record?.id || null
  if (record) {
    Object.assign(form, {
      source_field: record.source_field,
      target_field: record.target_field,
      field_type: record.field_type || 'string',
      is_match_key: record.is_match_key,
    })
    valueMappingStr.value = record.value_mapping ? JSON.stringify(record.value_mapping, null, 2) : ''
  } else {
    Object.assign(form, {
      source_field: '',
      target_field: '',
      field_type: 'string',
      is_match_key: false,
    })
    valueMappingStr.value = ''
  }
  visible.value = true
}

const handleSubmit = async () => {
  let valueMapping = null
  if (valueMappingStr.value) {
    try {
      valueMapping = JSON.parse(valueMappingStr.value)
    } catch (e) {
      message.error('值映射JSON格式错误')
      return
    }
  }

  const data = {
    ...form,
    source_id: selectedSourceId.value,
    value_mapping: valueMapping,
  }

  try {
    if (editingId.value) {
      await fieldMappingApi.update(editingId.value, data)
      message.success('更新成功')
    } else {
      await fieldMappingApi.create(data)
      message.success('创建成功')
    }
    visible.value = false
    fetchMappings()
  } catch (error) {
    message.error('操作失败')
  }
}

const showValueMapping = (record: any) => {
  currentValueMapping.value = record.value_mapping
  valueMappingVisible.value = true
}

const deleteMapping = async (id: number) => {
  try {
    await fieldMappingApi.delete(id)
    message.success('删除成功')
    fetchMappings()
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
</style>
