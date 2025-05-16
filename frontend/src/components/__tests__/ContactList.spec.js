import { shallowMount } from '@vue/test-utils'
import ContactList from '../ContactList.vue'
import { describe, it, expect, beforeEach } from 'jest'

describe('ContactList.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = shallowMount(ContactList)
  })

  it('filters contacts correctly', () => {
    wrapper.vm.searchQuery = 'Tudor'
    expect(wrapper.vm.filteredContacts).toHaveLength(1)
    expect(wrapper.vm.filteredContacts[0].name).toBe('Tudor Buha')
  })
}) 