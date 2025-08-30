import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import HelloWorld from '../src/components/HelloWorld.vue'

describe('HelloWorld', () => {
  it('renders proper greeting', () => {
    const wrapper = mount(HelloWorld, {
      props: {
        msg: 'Hello Vitest'
      }
    })
    
    expect(wrapper.text()).toContain('Hello Vitest')
  })

  it('increments count on button click', async () => {
    const wrapper = mount(HelloWorld)
    
    expect(wrapper.find('button').text()).toBe('Count: 0')
    
    await wrapper.find('button').trigger('click')
    
    expect(wrapper.find('button').text()).toBe('Count: 1')
  })
})