import axios from 'axios'
import { ElMessage } from 'element-plus'
import { reportError } from '@/utils/errorReporter'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    reportError('axios_request_error', error)
    return Promise.reject(error)
  },
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const status = error.response?.status
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      '请求失败'

    reportError('axios_response_error', error, {
      status,
      url: error.config?.url,
      method: error.config?.method,
      response: error.response?.data,
    })

    if (status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('username')
      ElMessage.error('登录已过期，请重新登录')

      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    } else if (status === 403) {
      ElMessage.error('没有权限访问该资源')
    } else if (status === 404) {
      ElMessage.error('请求的资源不存在')
    } else if (status >= 500) {
      ElMessage.error('服务器错误，请稍后再试')
    } else {
      ElMessage.error(message)
    }

    return Promise.reject(error)
  },
)

export default request
