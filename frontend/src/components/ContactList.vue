<template>
  <div class="app-wrapper">
    <!-- Network Status Indicator -->
    <div class="network-status" :class="{ 'offline': !isOnline }">
      {{ isOnline ? 'Online' : 'Offline - Changes will sync when connection is restored' }}
    </div>
    
    <div class="contacts-container">
    <!-- Add this new header section back -->
    <div class="app-header">
      <h1>UBBank Contacts</h1>
      <div class="header-underline"></div>
    </div>
      
    <!-- Charts Section -->
    <ContactCharts :contacts="contacts" />
      
      <!-- Search Bar -->
    <div class="search-bar-container">
      <div class="search-bar">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Search contacts..." 
          class="search-input"
        />
      </div>
      <button @click="toggleSort" class="sort-btn">
        {{ isSortedAZ ? '🔄 Z-A' : '🔄 A-Z' }}
      </button>
    </div>

    <!-- Search Results -->
    <div v-if="searchQuery && noteMatchingContacts.length > 0" class="search-results">
      <h4>Contacts with matching notes:</h4>
      <div class="matching-contacts">
        <div v-for="contact in noteMatchingContacts" :key="contact.id" class="matching-contact">
          <span class="contact-name">{{ contact.name }}</span>
          <span class="contact-note">📝 {{ contact.notes }}</span>
        </div>
      </div>
    </div>
  
    <!-- Action Buttons Container -->
    <div class="action-buttons">
      <!-- Add Contact Button -->
      <button @click="showAddContactModal" class="add-contact-btn">
        ➕ Add New Contact
      </button>
      
      <!-- Export Contacts Button -->
      <button @click="exportContacts" class="export-contacts-btn">
        📥 Export Contacts
      </button>

      <!-- Import Contacts Button -->
      <button @click="showImportModal" class="import-contacts-btn">
        📤 Import Contacts
      </button>
      </div>
  
      <!-- Contacts List -->
      <div class="contacts-list">
      <div v-for="contact in displayedContacts" :key="contact.id" class="contact-card">
        <div class="contact-info">
          <div class="contact-header">
            <template v-if="editingId !== contact.id">
              <h3>{{ contact.name }}</h3>
              <span class="tag">{{ contact.tag }}</span>
            </template>
            <template v-else>
              <input 
                v-model="editingContact.name" 
                type="text" 
                class="edit-input" 
                placeholder="Name"
              />
            </template>
        </div>
          <div class="contact-details">
            <template v-if="editingId !== contact.id">
              <p>📞 {{ contact.phone }}</p>
              <p>✉️ {{ contact.email }}</p>
              <p class="notes">📝 {{ contact.notes || 'No notes' }}</p>
            </template>
            <template v-else>
              <input 
                v-model="editingContact.phone" 
                type="text" 
                class="edit-input" 
                placeholder="Phone"
              />
              <input 
                v-model="editingContact.email" 
                type="email" 
                class="edit-input" 
                placeholder="Email"
              />
              <input 
                v-model="editingContact.notes" 
                type="text" 
                class="edit-input" 
                placeholder="Notes"
              />
            </template>
      </div>
          <div class="banking-actions" :class="{
            'positive-transaction': contact.lastTransaction > 0,
            'negative-transaction': contact.lastTransaction < 0,
            'no-transaction': contact.lastTransaction === 0
          }">
            <div class="balance-info">
              <span class="balance-label">Last Transaction:</span>
              <span class="balance-amount" :class="{ 'sent': contact.lastTransaction < 0, 'received': contact.lastTransaction > 0 }">
                {{ formatCurrency(contact.lastTransaction) }}
              </span>
    </div>
            <button class="send-money-btn" @click="showTransferModal(contact)">
              💸 Send Money
            </button>
          </div>
        </div>
        <div class="contact-actions">
          <template v-if="editingId !== contact.id">
            <button class="edit-btn" @click="startEditing(contact)">
              ✏️ Edit
            </button>
            <button class="delete-btn" @click="deleteContact(contact.id)">
              🗑️ Delete
            </button>
          </template>
          <template v-else>
            <button class="save-btn" @click="updateContact(contact.id)">
              💾 Save
            </button>
            <button class="cancel-btn" @click="cancelEditing">
              ❌ Cancel
            </button>
          </template>
        </div>
      </div>
    </div>

    <!-- Loading More Indicator -->
    <div v-if="isLoadingMore" class="loading-more">
      Loading more contacts...
    </div>

    <!-- Transfer Modal -->
    <div v-if="showingTransferFor" class="transfer-modal">
      <div class="modal-content">
        <h3>Send Money to {{ showingTransferFor.name }}</h3>
        <div class="transfer-form">
          <div class="amount-input">
            <span class="currency">$</span>
            <input 
              type="number" 
              v-model="transferAmount" 
              placeholder="Amount"
              min="0.01"
              step="0.01"
            />
          </div>
          <input 
            type="text" 
            v-model="transferNote" 
            placeholder="Add a note (optional)"
          />
          <div class="transfer-actions">
            <button class="confirm-btn" @click="sendMoney">
              Confirm Transfer
            </button>
            <button class="cancel-btn" @click="cancelTransfer">
              Cancel
            </button>
          </div>
        </div>
        </div>
      </div>
    </div>

    <!-- Add Contact Modal -->
    <div v-if="showingAddContact" class="add-contact-modal">
      <div class="add-contact-content">
        <div class="add-contact-header">
          Add New Contact
        </div>
        <form @submit.prevent="addContact" class="add-contact-form">
          <input 
            v-model="newContact.name" 
            type="text" 
            placeholder="Name" 
            required 
          />
          <input 
            v-model="newContact.phone" 
            type="text" 
            placeholder="Phone Number" 
            required 
          />
          <input 
            v-model="newContact.email" 
            type="email" 
            placeholder="Email" 
            required 
          />
          <input 
            v-model="newContact.notes" 
            type="text" 
            placeholder="Notes"
          />
          <div class="add-contact-actions">
            <button type="submit" class="confirm-btn">
              Add Contact
            </button>
            <button type="button" class="cancel-btn" @click="cancelAddContact">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Import Contacts Modal -->
    <div v-if="showingImport" class="import-modal">
      <div class="import-content">
        <div class="import-header">
          Import Contacts from CSV
        </div>
        <div class="import-body">
          <p class="import-instructions">
            Upload a CSV file with the following columns: <br>
            <code>name, phone, email, notes, tag, last_transaction</code> (only name, phone, and email are required)
          </p>
          <div class="file-select">
            <label class="file-select-label">
              <span v-if="!selectedFile">Select CSV File</span>
              <span v-else>{{ selectedFile.name }}</span>
              <input 
                type="file" 
                @change="handleFileSelect" 
                accept=".csv"
                style="display: none;"
              />
            </label>
          </div>
          <div class="sample-download">
            <a href="#" @click.prevent="downloadSampleCSV">Download Sample CSV Template</a>
          </div>
          <div class="import-actions">
            <button 
              class="import-btn" 
              @click="importContacts" 
              :disabled="!selectedFile"
            >
              Import Contacts
            </button>
            <button class="cancel-btn" @click="cancelImport">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add this in the template section, right after the search bar -->
    <div v-if="isLoading" class="loading-message">
      Loading contacts...
    </div>
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    <div v-if="!isLoading && !error && contacts.length === 0" class="no-contacts-message">
      No contacts found. Add your first contact!
      </div>
    </div>
  </template>
  
  <script>
import backgroundImage from '../assets/background3.jpg'
import ContactCharts from './ContactCharts.vue'
import { api, offlineStore, wsManager } from '../services/api'

  export default {
  components: {
    ContactCharts
  },
    data() {
      return {
      backgroundImage,
        searchQuery: '',
      editingId: null,
      editingContact: { name: '', phone: '', email: '', notes: '' },
      newContact: { name: '', phone: '', email: '', notes: '' },
      showingTransferFor: null,
      transferAmount: '',
      transferNote: '',
      contacts: [],
      showingAddContact: false,
      isSortedAZ: false,
      currentPage: 1,
      itemsPerPage: 5,
      isLoading: false,
      isLoadingMore: false,
      error: null,
      page: 1,
      hasMore: true,
      isOnline: navigator.onLine,
      wsUnsubscribe: null,
      showingImport: false,
      selectedFile: null
      };
    },
    computed: {
      filteredContacts() {
      if (!this.contacts) return [];
      
      let contacts = this.contacts.filter(contact => 
          contact.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        contact.phone.includes(this.searchQuery) ||
        (contact.tag && contact.tag.toLowerCase().includes(this.searchQuery.toLowerCase()))
      );
      
      if (this.isSortedAZ) {
        contacts.sort((a, b) => a.name.localeCompare(b.name));
      } else {
        contacts.sort((a, b) => b.name.localeCompare(a.name));
      }
      
      return contacts;
    },
    paginatedContacts() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filteredContacts.slice(start, end);
    },
    totalPages() {
      return Math.ceil(this.filteredContacts.length / this.itemsPerPage);
    },
    transactionStats() {
      const transactions = this.contacts.map(c => c.lastTransaction);
      return {
        highest: Math.max(...transactions),
        lowest: Math.min(...transactions),
        average: transactions.reduce((a, b) => a + b, 0) / transactions.length
      };
    },
    displayedContacts() {
      return this.filteredContacts.slice(0, this.currentPage * this.itemsPerPage);
    },
    noteMatchingContacts() {
      if (!this.searchQuery) return [];
        return this.contacts.filter(contact => 
        contact.notes && contact.notes.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
      }
    },
    methods: {
    async loadContacts(loadMore = false) {
      if (loadMore) {
        if (!this.hasMore || this.isLoadingMore) return;
        this.isLoadingMore = true;
      } else {
        this.isLoading = true;
        this.currentPage = 1;
      }

      this.error = null;
      try {
        const sortParam = this.isSortedAZ ? 'name' : '-name';
        const response = await api.getContacts(this.searchQuery, sortParam, this.currentPage);
        
        if (loadMore) {
          // Append new contacts to existing ones
          this.contacts = [...this.contacts, ...response.items];
          this.currentPage++;
        } else {
          // Reset contacts for new search/sort
          this.contacts = response.items;
          this.currentPage = 1;
        }
        
        // Update pagination state
        this.hasMore = this.currentPage < response.pages;
        this.totalContacts = response.total;
      } catch (error) {
        console.error('Failed to load contacts:', error);
        this.error = 'Failed to load contacts. Please try again.';
      } finally {
        this.isLoading = false;
        this.isLoadingMore = false;
      }
    },

    handleScroll() {
      if (this.isLoadingMore || !this.hasMore) return;
      
      const scrollPosition = window.innerHeight + window.scrollY;
      const threshold = document.documentElement.scrollHeight - 1000; // Load more when 1000px from bottom
      
      if (scrollPosition >= threshold) {
        this.loadContacts(true);
      }
    },

    async handleFileUpload(event, contactId) {
      const file = event.target.files[0];
      if (!file) return;

      try {
        const result = await api.uploadFile(file);
        await this.updateContact(contactId, {
          video_url: result.path
        });
      } catch (error) {
        console.error('Failed to upload file:', error);
        alert('Failed to upload file. Please try again.');
      }
    },

    handleOnline() {
      this.isOnline = true;
      offlineStore.syncWithServer();
    },

    handleOffline() {
      this.isOnline = false;
    },

    async addContact() {
      if (!this.newContact.name || !this.newContact.phone || !this.newContact.email) {
        alert("Please fill out all required fields");
        return;
      }

      try {
        const newTag = this.generateTag(this.newContact.name, this.newContact.phone);
        const contactData = { ...this.newContact, tag: newTag };
        await api.createContact(contactData);
        this.newContact = { name: '', phone: '', email: '', notes: '' };
        this.showingAddContact = false;
        await this.loadContacts();
      } catch (error) {
        if (!this.isOnline) {
          alert('Changes will sync when online');
        } else {
          alert('Failed to add contact. Please try again.');
        }
      }
    },
    async updateContact(id) {
      if (!this.editingContact.name || !this.editingContact.phone || !this.editingContact.email) {
        alert("Please fill out all required fields");
        return;
      }

      try {
        const tag = this.generateTag(this.editingContact.name, this.editingContact.phone);
        const contactData = { ...this.editingContact, tag };
        await api.updateContact(id, contactData);
        await this.loadContacts();
        this.cancelEditing();
      } catch (error) {
        console.error('Failed to update contact:', error);
        alert('Failed to update contact. Please try again.');
      }
    },
    async deleteContact(id) {
      if (confirm('Are you sure you want to delete this contact?')) {
        try {
          await api.deleteContact(id);
          await this.loadContacts();
        } catch (error) {
          console.error('Failed to delete contact:', error);
          alert('Failed to delete contact. Please try again.');
        }
      }
    },
    async sendMoney() {
      if (!this.transferAmount || this.transferAmount <= 0) {
        alert('Please enter a valid amount');
        return;
      }

      try {
        await api.addTransaction(
          this.showingTransferFor.id,
          -parseFloat(this.transferAmount),
          this.transferNote || 'Transfer'
        );
        await this.loadContacts();
        this.cancelTransfer();
      } catch (error) {
        console.error('Failed to send money:', error);
        alert('Failed to send money. Please try again.');
      }
    },
    startEditing(contact) {
      this.editingId = contact.id;
      this.editingContact = { ...contact };
    },
    cancelEditing() {
      this.editingId = null;
      this.editingContact = { name: '', phone: '', email: '', notes: '' };
    },
      generateTag(name, phone) {
        if (!name || !phone) return '';
        const firstTwo = name.substring(0, 2);
        const lastTwoDigits = phone.slice(-2);
        const lastTwoName = name.slice(-2);
        return `${firstTwo}${lastTwoDigits}${lastTwoName}`;
      },
    formatCurrency(amount) {
      return amount > 0 
        ? `+$${Math.abs(amount).toFixed(2)}` 
        : `-$${Math.abs(amount).toFixed(2)}`;
    },
    showTransferModal(contact) {
      this.showingTransferFor = contact;
      this.transferAmount = '';
      this.transferNote = '';
    },
    cancelTransfer() {
      this.showingTransferFor = null;
      this.transferAmount = '';
      this.transferNote = '';
    },
    showAddContactModal() {
      this.showingAddContact = true;
    },
    cancelAddContact() {
      this.showingAddContact = false;
      this.newContact = { name: '', phone: '', email: '', notes: '' };
    },
    toggleSort() {
      this.isSortedAZ = !this.isSortedAZ;
      this.loadContacts();
    },
    async exportContacts() {
      try {
        await api.exportContacts();
      } catch (error) {
        console.error('Failed to export contacts:', error);
        alert('Failed to export contacts. Please try again.');
      }
    },
    showImportModal() {
      this.showingImport = true;
    },
    cancelImport() {
      this.showingImport = false;
      this.selectedFile = null;
    },
    async handleFileSelect(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedFile = file;
      }
    },
    async downloadSampleCSV() {
      try {
        await api.downloadSampleCSV();
      } catch (error) {
        console.error('Failed to download sample CSV:', error);
        alert('Failed to download sample CSV. Please try again.');
      }
    },
    async importContacts() {
      if (!this.selectedFile) {
        alert('Please select a file to import');
          return;
        }
        
      try {
        await api.importContacts(this.selectedFile);
        this.showingImport = false;
        this.selectedFile = null;
        await this.loadContacts();
      } catch (error) {
        console.error('Failed to import contacts:', error);
        alert('Failed to import contacts. Please try again.');
      }
    }
  },
  watch: {
    searchQuery() {
      this.loadContacts();
    }
  },
  async created() {
    await this.loadContacts();
    
    // Setup WebSocket listeners
    this.wsUnsubscribe = wsManager.addListener(data => {
      if (data.type === 'new_contact') {
        this.contacts.unshift(data.data);
      } else if (data.type === 'update_contact') {
        const index = this.contacts.findIndex(c => c.id === data.data.id);
        if (index !== -1) {
          this.contacts.splice(index, 1, data.data);
        }
      } else if (data.type === 'delete_contact') {
        this.contacts = this.contacts.filter(c => c.id !== data.data.id);
      }
    });

    // Setup online/offline handlers
    window.addEventListener('online', this.handleOnline);
    window.addEventListener('offline', this.handleOffline);
    // Add window scroll event listener
    window.addEventListener('scroll', this.handleScroll);
  },
  beforeUnmount() {
    if (this.wsUnsubscribe) {
      this.wsUnsubscribe();
    }
    window.removeEventListener('online', this.handleOnline);
    window.removeEventListener('offline', this.handleOffline);
    // Remove window scroll event listener
    window.removeEventListener('scroll', this.handleScroll);
    }
  };
  </script>

<style>
/* Add this new style block WITHOUT scoped for global styles */
body {
  margin: 0;
  padding: 0;
  min-height: 100vh;
  background: url('../assets/background3.jpg') no-repeat center center fixed;
  background-size: cover;
}
</style>
  
  <style scoped>
/* Make containers even more glassy and modern */
  .contacts-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.03); /* More transparent */
  min-height: 100vh;
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(12px); /* Increased blur */
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 10px !important;
  overflow-x: hidden; /* Prevent horizontal scrolling */
}

.search-bar-container {
  display: flex;
  gap: 50px;
  margin-top: 20px;
  margin-bottom: 25px;
  align-items: center;
  width: 100%;
  justify-content: center;
}

.search-bar {
  flex: 1;
  min-width: 0;
  max-width: 800px;
}

.search-input {
  width: 100%;
  padding: 12px 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
  background-color: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(12px);
  color: #000;
  font-weight: 600;
  box-shadow: 
    inset 0 2px 10px rgba(0, 0, 0, 0.05),
    0 2px 10px rgba(0, 0, 0, 0.05);
}

.search-input:focus {
  border-color: #6dd5ed;
  outline: none;
  box-shadow: 
    0 0 15px rgba(109, 213, 237, 0.2),
    inset 0 2px 10px rgba(0, 0, 0, 0.05);
}

.sort-btn {
  padding: 12px 20px;
  background: linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 5px;
  white-space: nowrap;
  box-shadow: 0 4px 15px rgba(33, 147, 176, 0.2);
  flex-shrink: 0;
  height: 48px;
}

.sort-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(33, 147, 176, 0.3);
}

.add-contact-btn {
  width: 100%;
  padding: 15px;
  margin: 20px 0;
  background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.2em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 4px 15px rgba(44, 62, 80, 0.2);
}

.add-contact-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(44, 62, 80, 0.3);
}

.add-contact-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.add-contact-content {
  background: rgba(255, 255, 255, 0.95);
  padding: 30px;
  border-radius: 16px;
    width: 90%;
  max-width: 400px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.add-contact-header {
    text-align: center;
  margin-bottom: 25px;
  font-size: 1.5em;
  font-weight: 700;
  color: #2c3e50;
}

.add-contact-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.add-contact-form input {
  padding: 12px 15px;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 1.1em;
  transition: all 0.3s ease;
}

.add-contact-form input:focus {
  border-color: #3498db;
  outline: none;
  box-shadow: 0 0 15px rgba(52, 152, 219, 0.2);
}

.add-contact-actions {
  display: flex;
  gap: 15px;
  margin-top: 20px;
}

.submit-btn {
  background-image: linear-gradient(to right, #42b983 0%, #3aa876 100%);
  color: white;
  padding: 12px;
  border: none;
  border-radius: 6px;
    cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  }
  
  .contacts-list {
    display: flex;
    flex-direction: column;
  gap: 20px;
  overflow-y: auto;
  padding: 10px;
  margin-bottom: 20px;
  overflow-x: hidden; /* Prevent horizontal scrolling */
  width: 100%;
  }
  
  .contact-card {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 20px 30px;
  box-shadow: 
    0 4px 20px rgba(0, 0, 0, 0.05),
    inset 0 0 20px rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.4s ease;
  width: 100%;
  box-sizing: border-box;
  transform-origin: center;
  max-width: 100%;
  margin: 0 auto;
}

.contact-card:hover {
  background-color: rgba(255, 255, 255, 0.08);
  transform: translateY(-5px) scale(1.02);
  box-shadow: 
    0 8px 30px rgba(0, 0, 0, 0.1),
    inset 0 0 30px rgba(255, 255, 255, 0.1);
}

.contact-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}

.contact-header h3 {
  margin: 0;
  color: #000000;
  font-size: 1.3em;
  font-weight: 800;
  text-shadow: none;
  background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.contact-details {
  margin-bottom: 15px;
}

.contact-details p {
  margin: 8px 0;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.1em;
  font-weight: 600;
  text-shadow: 0 1px 1px rgba(255, 255, 255, 0.3);
}

.phone-icon, .email-icon {
  font-style: normal;
  font-size: 1.2em;
  filter: drop-shadow(0 2px 3px rgba(0, 0, 0, 0.2));
}

.tag {
  background: linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.85em;
  font-weight: 600;
  box-shadow: 
    0 2px 10px rgba(33, 147, 176, 0.2),
    inset 0 1px 1px rgba(255, 255, 255, 0.2);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  border: none;
  letter-spacing: 0.5px;
}

.contact-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.3);
}

.edit-btn, .delete-btn {
  background-image: linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%);
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  box-shadow: 0 4px 15px rgba(33, 147, 176, 0.2);
}

.edit-btn:hover, .delete-btn:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.edit-input {
  width: 100%;
  padding: 8px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  font-size: 14px;
  margin: 4px 0;
  transition: all 0.3s ease;
  background-color: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(8px);
  color: #000;
  font-weight: 600;
}

.edit-input:focus {
  border-color: #42b983;
  outline: none;
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 0 15px rgba(66, 185, 131, 0.2);
  transform: translateY(-1px);
}

.save-btn {
  background-image: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  box-shadow: 0 4px 15px rgba(17, 153, 142, 0.2);
}

.cancel-btn {
  background-image: linear-gradient(to right, #95a5a6 0%, #7f8c8d 100%);
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  flex: 1;
  display: flex;
    align-items: center;
  justify-content: center;
  gap: 5px;
}

.save-btn:hover, .cancel-btn:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

@media (max-width: 600px) {
  .contacts-container {
    padding: 10px;
  }
  
  .contact-card {
    padding: 15px;
  }
  
  .contact-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .tag {
    align-self: flex-start;
  }
}

.app-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 25px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 
    0 4px 30px rgba(0, 0, 0, 0.1),
    inset 0 0 40px rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}

.app-header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(
    circle,
    rgba(255, 255, 255, 0.1) 0%,
    transparent 60%
  );
  animation: shimmer 10s infinite linear;
  pointer-events: none;
}

.app-header h1 {
  margin: 0;
  font-size: 3em;
  font-weight: 800;
  background: linear-gradient(135deg, #2193b0 0%, #6dd5ed 50%, #2193b0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 
    2px 2px 4px rgba(0, 0, 0, 0.2),
    0 0 20px rgba(33, 147, 176, 0.3);
  letter-spacing: 3px;
  transform: translateZ(0);
  transition: all 0.3s ease;
}

.app-header:hover h1 {
  transform: scale(1.02) translateZ(0);
  background: linear-gradient(135deg, #42b983 0%, #2980b9 50%, #1a5f7a 100%);
  -webkit-background-clip: text;
  letter-spacing: 3px;
}

.header-underline {
  height: 4px;
  width: 180px;
  margin: 15px auto 0;
  background: linear-gradient(to right, 
    #42b983, 
    #2980b9, 
    #1a5f7a,
    #2980b9, 
    #42b983
  );
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  animation: shimmerLine 3s infinite linear;
  background-size: 200% 100%;
}

@keyframes shimmer {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes shimmerLine {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: -100% 0;
  }
}

/* Add these new styles */
.banking-actions {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 15px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.positive-transaction {
  background: linear-gradient(135deg, rgba(46, 204, 113, 0.1) 0%, rgba(46, 204, 113, 0.2) 100%);
  border: 1px solid rgba(46, 204, 113, 0.3);
  box-shadow: 0 0 15px rgba(46, 204, 113, 0.1);
}

.negative-transaction {
  background: linear-gradient(135deg, rgba(231, 76, 60, 0.1) 0%, rgba(231, 76, 60, 0.2) 100%);
  border: 1px solid rgba(231, 76, 60, 0.3);
  box-shadow: 0 0 15px rgba(231, 76, 60, 0.1);
}

.no-transaction {
  background: linear-gradient(135deg, rgba(149, 165, 166, 0.1) 0%, rgba(149, 165, 166, 0.2) 100%);
  border: 1px solid rgba(149, 165, 166, 0.3);
  box-shadow: 0 0 15px rgba(149, 165, 166, 0.1);
}

.average-transaction {
  background: linear-gradient(135deg, rgba(241, 196, 15, 0.1) 0%, rgba(241, 196, 15, 0.2) 100%);
  border: 1px solid rgba(241, 196, 15, 0.3);
  box-shadow: 0 0 15px rgba(241, 196, 15, 0.1);
}

.balance-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 0.9em;
}

.balance-label {
  color: rgba(0, 0, 0, 0.7);
  font-weight: 600;
}

.balance-amount {
  font-weight: 700;
  font-size: 1.1em;
}

.balance-amount.sent {
  color: #e74c3c;
}

.balance-amount.received {
  color: #2ecc71;
}

.send-money-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.send-money-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(17, 153, 142, 0.3);
}

.transfer-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.modal-content {
  background: rgba(255, 255, 255, 0.95);
  padding: 30px;
  border-radius: 16px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  text-align: center;
  margin: auto;
}

.modal-content h3 {
  margin-bottom: 25px;
  color: #333;
  font-size: 1.5em;
}

.transfer-form {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.amount-input {
  position: relative;
  width: 80%;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  padding: 0;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.currency {
  position: static;
  font-size: 1.4em;
  font-weight: 600;
  color: #333;
  padding: 12px 15px;
  background: rgba(0, 0, 0, 0.02);
  border-right: 2px solid rgba(0, 0, 0, 0.1);
}

.amount-input input {
  width: 100%;
  padding: 12px 15px;
  font-size: 1.4em;
  border: none;
  background: transparent;
  outline: none;
  color: #333;
  font-weight: 500;
  text-align: center;
}

.amount-input:focus-within {
  border-color: #38ef7d;
  box-shadow: 0 0 20px rgba(56, 239, 125, 0.15);
}

.transfer-form input[type="text"] {
  width: 80%;
  padding: 12px 15px;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  font-size: 1.1em;
  background: rgba(255, 255, 255, 0.9);
  text-align: center;
}

.transfer-actions {
  display: flex;
  gap: 15px;
  width: 80%;
  margin-top: 10px;
}

.confirm-btn, .cancel-btn {
  flex: 1;
  padding: 12px 20px;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  font-size: 1.1em;
  transition: all 0.3s ease;
}

.confirm-btn {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    color: white;
}

.cancel-btn {
  background: linear-gradient(135deg, #e0e0e0 0%, #c0c0c0 100%);
  color: #333;
}

.confirm-btn:hover, .cancel-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  }

.loading-message, .error-message, .no-contacts-message {
  text-align: center;
  padding: 20px;
  margin: 20px 0;
  border-radius: 8px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.loading-message {
  color: #2193b0;
}

.error-message {
  color: #e74c3c;
  background: rgba(231, 76, 60, 0.1);
}

.no-contacts-message {
  color: #34495e;
}

.network-status {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  padding: 8px;
  text-align: center;
  background: #4CAF50;
  color: white;
  font-weight: bold;
  z-index: 1000;
  transition: background-color 0.3s;
}

.network-status.offline {
  background: #f44336;
}

.contacts-wrapper {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
  padding: 20px;
  margin-top: 20px;
}

.loading-more {
  text-align: center;
  padding: 20px;
  color: #2193b0;
  font-weight: 600;
}

.contact-video {
  width: 100%;
  max-width: 400px;
  margin: 10px 0;
  border-radius: 8px;
}

.upload-btn {
  background: linear-gradient(135deg, #6e8efb, #4a6cf7);
  color: white;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-block;
  margin-top: 10px;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(74, 108, 247, 0.2);
}

.upload-btn:hover {
  background: linear-gradient(135deg, #4a6cf7, #6e8efb);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(74, 108, 247, 0.3);
}

.file-upload-container {
  margin-top: 15px;
  display: flex;
  justify-content: center;
}

.contact-video {
  width: 100%;
  max-width: 400px;
  margin: 15px auto;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  display: block;
}

.search-results {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 15px;
  margin: 10px 0;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.search-results h4 {
  color: #ffffff;
  margin: 0 0 10px 0;
  font-weight: 500;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.matching-contacts {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.matching-contact {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.matching-contact:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateX(5px);
}

.contact-name {
  color: #ffffff;
  font-weight: 500;
}

.contact-note {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9em;
}

.export-contacts-btn {
  padding: 12px 25px;
  background: linear-gradient(135deg, #11998e, #38ef7d);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(17, 153, 142, 0.2);
  margin-top: 0;
  margin-left: 0;
}

.export-contacts-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(17, 153, 142, 0.3);
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin: 20px 0;
}

.add-contact-btn {
  padding: 12px 25px;
  background: linear-gradient(135deg, #4a6cf7, #6e8efb);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 0;
  box-shadow: 0 4px 15px rgba(74, 108, 247, 0.2);
}

.import-contacts-btn {
  padding: 12px 25px;
  background: linear-gradient(135deg, #9b59b6, #8e44ad);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 0;
  box-shadow: 0 4px 15px rgba(155, 89, 182, 0.2);
}

.import-contacts-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(155, 89, 182, 0.3);
}

.import-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.import-content {
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.import-header {
  padding: 20px;
  background: linear-gradient(135deg, #9b59b6, #8e44ad);
  color: white;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
}

.import-body {
  padding: 20px;
}

.import-instructions {
  margin-bottom: 20px;
  color: #333;
  text-align: center;
}

.import-instructions code {
  background-color: rgba(155, 89, 182, 0.1);
  padding: 2px 5px;
  border-radius: 4px;
  color: #8e44ad;
  font-family: monospace;
}

.file-select {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.file-select-label {
  background: linear-gradient(135deg, #9b59b6, #8e44ad);
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.file-select-label:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(155, 89, 182, 0.3);
}

.sample-download {
  text-align: center;
  margin-bottom: 20px;
}

.sample-download a {
  color: #8e44ad;
  text-decoration: none;
  transition: all 0.3s ease;
}

.sample-download a:hover {
  text-decoration: underline;
}

.import-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.import-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #9b59b6, #8e44ad);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.import-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(155, 89, 182, 0.3);
}

.import-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
  
<style scoped>
.app-wrapper {
  width: 100%;
  min-height: 100vh;
  position: relative;
  overflow-x: hidden; /* Prevent horizontal scrolling */
  }
  </style>
  