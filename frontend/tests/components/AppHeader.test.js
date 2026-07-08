import { describe, it, expect } from 'vitest'

describe('AppHeader 组件', () => {
  it('组件文件应该可以被导入', async () => {
    const module = await import('@/components/layout/AppHeader.vue')

    expect(module.default).toBeDefined()
  })
})
