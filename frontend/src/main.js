import { createApp } from 'vue'
import { createPinia } from 'pinia'

import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'

import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from '@/router'

import '@/assets/styles/global.scss'

import { setupErrorReporting } from '@/utils/errorReporter'

const app = createApp(App)

// 注册 Pinia 状态管理
app.use(createPinia())

// 注册 Vue Router 路由
app.use(router)

// 注册 Element Plus
app.use(ElementPlus, {
  locale: zhCn,
})

// 全局注册 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 注册前端错误监控
setupErrorReporting(app)

app.mount('#app')
