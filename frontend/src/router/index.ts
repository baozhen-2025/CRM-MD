import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        redirect: '/datasource',
      },
      {
        path: 'datasource',
        name: 'DataSource',
        component: () => import('@/views/datasource/DataSource.vue'),
        meta: { title: '数据源管理', icon: 'DatabaseOutlined' },
      },
      {
        path: 'mapping',
        name: 'FieldMapping',
        component: () => import('@/views/mapping/FieldMapping.vue'),
        meta: { title: '字段映射配置', icon: 'SwapOutlined' },
      },
      {
        path: 'rule',
        name: 'MatchRule',
        component: () => import('@/views/rule/MatchRule.vue'),
        meta: { title: '匹配规则配置', icon: 'FilterOutlined' },
      },
      {
        path: 'sync',
        name: 'SyncTask',
        component: () => import('@/views/sync/SyncTask.vue'),
        meta: { title: '同步任务管理', icon: 'SyncOutlined' },
      },
      {
        path: 'audit',
        name: 'Audit',
        component: () => import('@/views/audit/Audit.vue'),
        meta: { title: '人工审核', icon: 'AuditOutlined' },
      },
      {
        path: 'log',
        name: 'ChangeLog',
        component: () => import('@/views/log/ChangeLog.vue'),
        meta: { title: '变更日志', icon: 'FileTextOutlined' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
