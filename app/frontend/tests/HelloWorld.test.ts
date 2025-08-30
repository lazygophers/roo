import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import HelloWorld from '../src/components/HelloWorld.vue'

describe('HelloWorld', () => {
  it('renders proper message', () => {
    const wrapper = mount(HelloWorld)
    expect(wrapper.text()).toContain('Hello World!')
  })

  it('increments count when button is clicked', async () => {
    const wrapper = mount(HelloWorld)
    const button = wrapper.find('button')
    
    expect(button.text()).toBe('Count: 0')
    
    await button.trigger('click')
    
    expect(button.text()).toBe('Count: 1')
  })

  it('has correct CSS classes', () => {
    const wrapper = mount(HelloWorld)
    const div = wrapper.find('div.hello-world')
    expect(div.classes()).toContain('hello-world')
  })
})