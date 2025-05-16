const { test, expect } = require('@jest/globals');

// Simple filtering function that mimics our Vue component's filtering
function filterContacts(contacts, query) {
  if (!query) return contacts;
  return contacts.filter(contact => 
    contact.name.toLowerCase().includes(query.toLowerCase()) || 
    contact.phone.includes(query) ||
    (contact.tag && contact.tag.toLowerCase().includes(query.toLowerCase()))
  );
}

// Mock data
const mockContacts = [
  { id: 1, name: "Tudor Buha", phone: "0774660245", tag: "Tu45ha" },
  { id: 2, name: "Chis Denis", phone: "0755395167", tag: "Ch67is" },
  { id: 3, name: "Vlad Cenuse", phone: "0736061333", tag: "Vl33se" }
];

// Tests
test('should filter contacts by name', () => {
  const result = filterContacts(mockContacts, 'Tudor');
  expect(result.length).toBe(1);
  expect(result[0].name).toBe('Tudor Buha');
});

test('should filter contacts by phone number', () => {
  const result = filterContacts(mockContacts, '0755');
  expect(result.length).toBe(1);
  expect(result[0].name).toBe('Chis Denis');
});

test('should filter contacts by tag', () => {
  const result = filterContacts(mockContacts, 'Vl33');
  expect(result.length).toBe(1);
  expect(result[0].name).toBe('Vlad Cenuse');
});

test('should return all contacts when query is empty', () => {
  const result = filterContacts(mockContacts, '');
  expect(result.length).toBe(3);
});

test('should return no contacts when no match is found', () => {
  const result = filterContacts(mockContacts, 'xyz');
  expect(result.length).toBe(0);
});

// New test for case-insensitive search
test('should perform case-insensitive search', () => {
  const lowerResult = filterContacts(mockContacts, 'tudor');
  const upperResult = filterContacts(mockContacts, 'TUDOR');
  const mixedResult = filterContacts(mockContacts, 'TuDoR');
  
  expect(lowerResult.length).toBe(1);
  expect(upperResult.length).toBe(1);
  expect(mixedResult.length).toBe(1);
  expect(lowerResult[0].name).toBe('Tudor Buha');
  expect(upperResult[0].name).toBe('Tudor Buha');
  expect(mixedResult[0].name).toBe('Tudor Buha');
});

// New test for partial name matches
test('should find contacts with partial name matches', () => {
  const result = filterContacts(mockContacts, 'is');
  expect(result.length).toBe(1);
  expect(result[0].name).toBe('Chis Denis');
});

// New test for multiple matches
test('should return multiple contacts when query matches multiple records', () => {
  // Add a new contact with similar name pattern
  const extendedContacts = [
    ...mockContacts,
    { id: 4, name: "Denis Smith", phone: "0755123456", tag: "De56th" }
  ];
  
  const result = filterContacts(extendedContacts, 'Denis');
  expect(result.length).toBe(2);
  expect(result.map(c => c.name)).toContain('Chis Denis');
  expect(result.map(c => c.name)).toContain('Denis Smith');
}); 