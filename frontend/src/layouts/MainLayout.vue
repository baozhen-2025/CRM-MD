<template>
  <a-layout style="min-height: 100vh">
    <a-layout-sider v-model:collapsed="collapsed" collapsible>
      <div class="logo">
        <span v-if="!collapsed">主数据集成平台</span>
        <span v-else>MD</span>
      </div>
      <a-menu
        v-model:selectedKeys="selectedKeys"
        theme="dark"
        mode="inline"
        @click="handleMenuClick"
      >
        <a-menu-item key="datasource">
          <template #icon><DatabaseOutlined /></template>
          数据源管理
        </a-menu-item>
        <a-menu-item key="mapping">
          <template #icon><SwapOutlined /></template>
          字段映射配置
        </a-menu-item>
        <a-menu-item key="rule">
          <template #icon><FilterOutlined /></template>
          匹配规则配置
        </a-menu-item>
        <a-menu-item key="sync">
          <template #icon><SyncOutlined /></template>
          同步任务管理
        </a-menu-item>
        <a-menu-item key="audit">
          <template #icon><AuditOutlined /></template>
          人工审核
        </a-menu-item>
        <a-menu-item key="log">
          <template #icon><FileTextOutlined /></template>
          变更日志
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header class="header">
        <a-breadcrumb>
          <a-breadcrumb-item>首页</a-breadcrumb-item>
          <a-breadcrumb-item>{{ currentTitle }}</a-breadcrumb-item>
        </a-breadcrumb>
        <div class="user-info">
          <a-avatar style="background-color: #1890ff">A</a-avatar>
          <span style="margin-left: 8px">管理员</span>
        </div>
      </a-layout-header>
      <a-layout-content class="content">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  DatabaseOutlined,
  SwapOutlined,
  FilterOutlined,
  SyncOutlined,
  AuditOutlined,
  FileTextOutlined,
} from '@ant-design/icons-vue'

const router = useRouter()
const route = useRoute()
const collapsed = ref(false)

const selectedKeys = ref([route.path.split('/')[1] || 'datasource'])

const currentTitle = computed(() => {
  const titles: Record<string, string> = {
    datasource: '数据源管理',
    mapping: '字段映射配置',
    rule: '匹配规则配置',
    sync: '同步任务管理',
    audit: '人工审核',
    log: '变更日志',
  }
  return titles[selectedKeys.value[0]] || ''
})

const handleMenuClick = ({ key }: { key: string }) => {
  router.push(`/${key}`)
}
</script>

<style scoped>
.logo {
  height: 32px;
  margin: 16px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: bold;
}

.header {
  background: #fff;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
}

.content {
  margin: 16px;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  min-height: calc(100vh - 64px - 32px);
}
</style>
