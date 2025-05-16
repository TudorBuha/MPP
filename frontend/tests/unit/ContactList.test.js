/* eslint-env jest */
const { test, expect } = require('@jest/globals');

// Mock data
const mockContacts = [
  {
    id: 1,
    name: 'John Doe',
    phone: '0712345678',
    email: 'john@example.com',
    notes: 'Best friend from high school',
    tag: 'Jo78oe',
    lastTransaction: 100
  },
  {
    id: 2,
    name: 'Jane Smith',
    phone: '0723456789',
    email: 'jane@example.com',
    notes: 'Tennis partner',
    tag: 'Ja89th',
    lastTransaction: -50
  }
];

// Helper function to mimic component's filtering logic
function filterContacts(contacts, query) {
  if (!query) return contacts;
  query = query.toLowerCase();
  return contacts.filter(contact => 
    contact.name.toLowerCase().includes(query) || 
    contact.phone.includes(query) ||
    (contact.tag && contact.tag.toLowerCase().includes(query))
  );
}

test('filters contacts by name', () => {
  const result = filterContacts(mockContacts, 'John');
  expect(result.length).toBe(1);
  expect(result[0].name).toBe('John Doe');
});

test('filters contacts by phone number', () => {
  const result = filterContacts(mockContacts, '0712');
  expect(result.length).toBe(1);
  expect(result[0].phone).toBe('0712345678');
});

test('filters contacts by tag', () => {
  const result = filterContacts(mockContacts, 'Jo78');
  expect(result.length).toBe(1);
  expect(result[0].tag).toBe('Jo78oe');
});

test('returns all contacts when query is empty', () => {
  const result = filterContacts(mockContacts, '');
  expect(result.length).toBe(2);
});

test('returns no contacts when no match is found', () => {
  const result = filterContacts(mockContacts, 'xyz');
  expect(result.length).toBe(0);
}); 