import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// 数据源 API
export const dataSourceApi = {
  list: () => api.get('/datasources'),
  create: (data: any) => api.post('/datasources', data),
  update: (id: number, data: any) => api.put(`/datasources/${id}`, data),
  delete: (id: number) => api.delete(`/datasources/${id}`),
  test: (id: number) => api.post(`/datasources/${id}/test`),
}

// 字段映射 API
export const fieldMappingApi = {
  list: (sourceId?: number) => api.get('/fieldmappings', { params: { source_id: sourceId } }),
  create: (data: any) => api.post('/fieldmappings', data),
  update: (id: number, data: any) => api.put(`/fieldmappings/${id}`, data),
  delete: (id: number) => api.delete(`/fieldmappings/${id}`),
}

// 匹配规则 API
export const matchRuleApi = {
  list: (sourceId?: number) => api.get('/matchrules', { params: { source_id: sourceId } }),
  create: (data: any) => api.post('/matchrules', data),
  update: (id: number, data: any) => api.put(`/matchrules/${id}`, data),
  delete: (id: number) => api.delete(`/matchrules/${id}`),
}

// 同步任务 API
export const syncTaskApi = {
  list: () => api.get('/synctasks'),
  create: (data: any) => api.post('/synctasks', data),
  execute: (id: number) => api.post(`/synctasks/${id}/execute`),
}

// 同步记录 API
export const syncRecordApi = {
  list: (taskId?: number) => api.get('/syncrecords', { params: { task_id: taskId } }),
}

// 审核记录 API
export const auditRecordApi = {
  list: (status?: number) => api.get('/auditrecords', { params: { status } }),
  audit: (id: number, data: any) => api.post(`/auditrecords/${id}/audit`, data),
}

// 变更日志 API
export const changeLogApi = {
  list: (params?: any) => api.get('/changelogs', { params }),
}

export default api
