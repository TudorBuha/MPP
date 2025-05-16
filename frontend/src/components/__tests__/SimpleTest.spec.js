import { describe, it, expect } from 'jest'

 // Mock filteredContacts functionality to test
function filterContacts(contacts, query) {
    return contacts.filter(contact => 
      contact.name.toLowerCase().includes(query.toLowerCase())
    );
  }
  
  // Mock data that mimics our app's contacts
  const mockContacts = [
    { id: 1, name: "Tudor Buha", phone: "0774660245" },
    { id: 2, name: "Chis Denis", phone: "0755395167" },
    { id: 3, name: "Vlad Cenuse", phone: "0736061333" }
  ];
  
  describe('Contact filtering', () => {
    it('correctly filters contacts by name', () => {
      const result = filterContacts(mockContacts, 'Tudor');
      expect(result).toHaveLength(1);
      expect(result[0].name).toBe('Tudor Buha');
    });
  
    it('returns all contacts when query is empty', () => {
      const result = filterContacts(mockContacts, '');
      expect(result).toHaveLength(3);
    });
  
    it('returns no contacts when no match is found', () => {
      const result = filterContacts(mockContacts, 'xyz');
      expect(result).toHaveLength(0);
    });
  });