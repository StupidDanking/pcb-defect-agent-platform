/**
 * 前端全局错误监控与上报
 *
 * 职责：
 * - 捕获 JavaScript 运行时错误
 * - 捕获未处理的 Promise 异常
 * - 捕获 Vue 组件渲染错误
 * - 捕获资源加载错误
 * - 当前阶段先输出到控制台 + 保存到 localStorage
 *
 * Day4 先不上报后端，后续可以接入 /api/errors/report。
 */

import { ElMessage } from 'element-plus'

const REPORT_TO_BACKEND = false
const REPORT_API = '/api/errors/report'
const STORAGE_KEY = 'frontend_error_logs'
const MAX_ERROR_COUNT = 20

/**
 * 安全序列化错误对象
 */
function serializeError(error) {
  if (!error) {
    return {
      message: 'Unknown error',
      stack: '',
      name: 'Error',
    }
  }

  if (typeof error === 'string') {
    return {
      message: error,
      stack: '',
      name: 'Error',
    }
  }

  return {
    message: error.message || String(error),
    stack: error.stack || '',
    name: error.name || 'Error',
  }
}

/**
 * 保存错误到 localStorage
 */
function saveErrorToLocal(errorInfo) {
  try {
    const oldLogs = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
    oldLogs.unshift(errorInfo)

    const newLogs = oldLogs.slice(0, MAX_ERROR_COUNT)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newLogs))
  } catch (e) {
    console.warn('保存前端错误日志失败:', e)
  }
}

/**
 * 上报到后端。
 *
 * 当前 REPORT_TO_BACKEND=false，所以默认不会发送请求。
 * 后续如果后端实现 /api/errors/report，可以改成 true。
 */
function sendErrorToBackend(errorInfo) {
  if (!REPORT_TO_BACKEND) {
    return
  }

  try {
    fetch(REPORT_API, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(errorInfo),
    }).catch((e) => {
      console.warn('错误上报请求失败:', e)
    })
  } catch (e) {
    console.warn('错误上报异常:', e)
  }
}

/**
 * 统一错误上报入口
 */
export function reportError(type, error, extra = {}) {
  const serialized = serializeError(error)

  const errorInfo = {
    type,
    message: serialized.message,
    name: serialized.name,
    stack: serialized.stack,
    url: window.location.href,
    userAgent: navigator.userAgent,
    timestamp: new Date().toISOString(),
    extra,
  }

  console.group('[Frontend Error]')
  console.error(errorInfo)
  console.groupEnd()

  saveErrorToLocal(errorInfo)
  sendErrorToBackend(errorInfo)

  return errorInfo
}

/**
 * 获取本地前端错误日志
 */
export function getLocalErrorLogs() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  } catch {
    return []
  }
}

/**
 * 清空本地前端错误日志
 */
export function clearLocalErrorLogs() {
  localStorage.removeItem(STORAGE_KEY)
}

/**
 * 安装全局错误监控
 */
export function setupErrorReporting(app) {
  // 1. 捕获 JavaScript 运行时错误
  window.onerror = function (message, source, lineno, colno, error) {
    reportError('javascript_runtime_error', error || message, {
      source,
      lineno,
      colno,
    })

    return false
  }

  // 2. 捕获未处理的 Promise 异常
  window.onunhandledrejection = function (event) {
    reportError('unhandled_promise_rejection', event.reason, {
      promise: String(event.promise),
    })
  }

  // 3. 捕获资源加载错误，例如图片、脚本、样式加载失败
  window.addEventListener(
    'error',
    function (event) {
      const target = event.target

      if (
        target &&
        target !== window &&
        ['IMG', 'SCRIPT', 'LINK'].includes(target.tagName)
      ) {
        reportError('resource_load_error', `资源加载失败: ${target.tagName}`, {
          tagName: target.tagName,
          src: target.src || target.href || '',
        })
      }
    },
    true,
  )

  // 4. 捕获 Vue 组件错误
  app.config.errorHandler = function (error, instance, info) {
    reportError('vue_component_error', error, {
      component: instance?.type?.name || 'AnonymousComponent',
      info,
    })

    if (import.meta.env.DEV) {
      ElMessage.error('前端组件发生错误，请查看控制台')
    }
  }

  console.info('[ErrorReporter] 前端错误监控已启用')
}
