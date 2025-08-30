import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import HelloWorld from '../src/components/HelloWorld.vue'

describe('HelloWorld', () => {
  it('renders proper greeting when name is provided', () => {
    const name = 'Vitest'
    const wrapper = mount(HelloWorld, {
      props: { name }
    })
    
    expect(wrapper.text()).toContain(`${name}!`)
    expect(wrapper.find('h1').text()).toBe(`${name}!`)
  })

  it('renders default greeting when no name is provided', () => {
    const wrapper = mount(HelloWorld)
    
    expect(wrapper.text()).toContain('Hello World!')
    expect(wrapper.find('h1').text()).toBe('Hello World!')
  })

  it('increments count when button is clicked', async () => {
    const wrapper = mount(HelloWorld)
    const button = wrapper.find('button')
    
    expect(wrapper.vm.count).toBe(0)
    
    await button.trigger('click')
    
    expect(wrapper.vm.count).toBe(1)
    expect(wrapper.text()).toContain('Count: 1')
  })
})