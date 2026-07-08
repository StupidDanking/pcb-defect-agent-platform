import { describe, it, expect } from 'vitest'
import request from '@/utils/request'

describe('Axios 请求封装', () => {
  it('应该正确创建 axios 实例', () => {
    expect(request).toBeDefined()
    expect(request.defaults).toBeDefined()
  })

  it('应该设置请求超时时间', () => {
    expect(request.defaults.timeout).toBe(30000)
  })
})
