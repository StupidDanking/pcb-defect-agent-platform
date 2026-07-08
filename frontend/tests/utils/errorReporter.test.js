import { describe, it, expect, beforeEach } from 'vitest'
import {
  reportError,
  getLocalErrorLogs,
  clearLocalErrorLogs,
} from '@/utils/errorReporter'

describe('错误上报模块', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('应该正确记录错误信息到 localStorage', () => {
    reportError('test_error', new Error('Day4 前端错误监控测试'), {
      source: 'vitest',
    })

    const logs = getLocalErrorLogs()

    expect(logs.length).toBe(1)
    expect(logs[0].type).toBe('test_error')
    expect(logs[0].message).toBe('Day4 前端错误监控测试')
    expect(logs[0].extra.source).toBe('vitest')
  })

  it('应该可以清空本地错误日志', () => {
    reportError('test_error', new Error('测试错误'))

    clearLocalErrorLogs()

    const logs = getLocalErrorLogs()
    expect(logs.length).toBe(0)
  })
})
