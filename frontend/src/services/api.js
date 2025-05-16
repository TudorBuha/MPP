const API_URL = 'http://localhost:8000/api';
const WS_URL = 'ws://localhost:8000/ws';

// Helper function to get headers with auth token
const getAuthHeaders = (contentType = false) => {
    const headers = {};
    const token = localStorage.getItem('token');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    if (contentType) {
        headers['Content-Type'] = 'application/json';
    }
    return headers;
};

class OfflineStore {
    constructor() {
        this.pendingOperations = [];
        this.loadPendingOperations();
    }

    loadPendingOperations() {
        const stored = localStorage.getItem('pendingOperations');
        this.pendingOperations = stored ? JSON.parse(stored) : [];
    }

    savePendingOperations() {
        localStorage.setItem('pendingOperations', JSON.stringify(this.pendingOperations));
    }

    addOperation(operation) {
        this.pendingOperations.push(operation);
        this.savePendingOperations();
    }

    async syncWithServer() {
        const operations = [...this.pendingOperations];
        this.pendingOperations = [];
        this.savePendingOperations();

        for (const operation of operations) {
            try {
                await this.executeOperation(operation);
            } catch (error) {
                console.error('Failed to sync operation:', error);
                this.addOperation(operation);
            }
        }
    }

    async executeOperation(operation) {
        switch (operation.type) {
            case 'create':
                await api.createContact(operation.data);
                break;
            case 'update':
                await api.updateContact(operation.data.id, operation.data);
                break;
            case 'delete':
                await api.deleteContact(operation.data.id);
                break;
            case 'transaction':
                await api.addTransaction(
                    operation.data.id,
                    operation.data.amount,
                    operation.data.note
                );
                break;
        }
    }
}

class WebSocketManager {
    constructor() {
        this.ws = null;
        this.listeners = [];
        this.connect();
    }

    connect() {
        this.ws = new WebSocket(WS_URL);
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.listeners.forEach(listener => listener(data));
        };

        this.ws.onclose = () => {
            setTimeout(() => this.connect(), 1000);
        };
    }

    addListener(callback) {
        this.listeners.push(callback);
        return () => {
            this.listeners = this.listeners.filter(l => l !== callback);
        };
    }

    send(data) {
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }
}

export const offlineStore = new OfflineStore();
export const wsManager = new WebSocketManager();

export const api = {
    // Get all contacts with optional search and sort parameters
    async getContacts(search = '', sort = '', page = 1, limit = 20) {
        try {
            const params = new URLSearchParams();
            if (search) params.append('search', search);
            if (sort) params.append('sort', sort);
            params.append('page', page);
            params.append('limit', limit);
            
            const response = await fetch(`${API_URL}/contacts?${params}`, {
                headers: getAuthHeaders()
            });
            if (!response.ok) throw new Error('Failed to fetch contacts');
            return response.json();
        } catch (error) {
            console.error('Network error:', error);
            // Return cached contacts if available
            const cached = localStorage.getItem('cachedContacts');
            return cached ? JSON.parse(cached) : [];
        }
    },

    // Get a single contact by ID
    async getContact(id) {
        const response = await fetch(`${API_URL}/contacts/${id}`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Failed to fetch contact');
        return response.json();
    },

    // Create a new contact
    async createContact(contact) {
        try {
            const response = await fetch(`${API_URL}/contacts`, {
                method: 'POST',
                headers: getAuthHeaders(true),
                body: JSON.stringify(contact),
            });
            if (!response.ok) throw new Error('Failed to create contact');
            const result = await response.json();
            wsManager.send({ type: 'new_contact', data: result });
            return result;
        } catch (error) {
            console.error('Network error:', error);
            offlineStore.addOperation({ type: 'create', data: contact });
            throw error;
        }
    },

    // Update an existing contact
    async updateContact(id, contact) {
        try {
            const response = await fetch(`${API_URL}/contacts/${id}`, {
                method: 'PUT',
                headers: getAuthHeaders(true),
                body: JSON.stringify(contact),
            });
            if (!response.ok) throw new Error('Failed to update contact');
            const result = await response.json();
            wsManager.send({ type: 'update_contact', data: result });
            return result;
        } catch (error) {
            console.error('Network error:', error);
            offlineStore.addOperation({ type: 'update', data: { id, ...contact } });
            throw error;
        }
    },

    // Delete a contact
    async deleteContact(id) {
        try {
            const response = await fetch(`${API_URL}/contacts/${id}`, {
                method: 'DELETE',
                headers: getAuthHeaders()
            });
            if (!response.ok) throw new Error('Failed to delete contact');
            const result = await response.json();
            wsManager.send({ type: 'delete_contact', data: { id } });
            return result;
        } catch (error) {
            console.error('Network error:', error);
            offlineStore.addOperation({ type: 'delete', data: { id } });
            throw error;
        }
    },

    // Add a transaction to a contact
    async addTransaction(id, amount, note = 'Transfer') {
        try {
            const params = new URLSearchParams();
            params.append('amount', amount);
            params.append('note', note);
            
            const response = await fetch(`${API_URL}/contacts/${id}/transaction?${params}`, {
                method: 'POST',
                headers: getAuthHeaders()
            });
            if (!response.ok) throw new Error('Failed to add transaction');
            const result = await response.json();
            wsManager.send({ type: 'new_transaction', data: { id, amount, note } });
            return result;
        } catch (error) {
            console.error('Network error:', error);
            offlineStore.addOperation({ type: 'transaction', data: { id, amount, note } });
            throw error;
        }
    },

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_URL}/upload`, {
                method: 'POST',
                body: formData,
            });
            if (!response.ok) throw new Error('Failed to upload file');
            return response.json();
        } catch (error) {
            console.error('Failed to upload file:', error);
            throw error;
        }
    },

    // Export contacts to CSV
    async exportContacts() {
        try {
            // Use window.open to trigger the download
            window.open(`${API_URL}/export-contacts`, '_blank');
            return true;
        } catch (error) {
            console.error('Failed to export contacts:', error);
            throw error;
        }
    },
    
    // Import contacts from CSV
    async importContacts(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_URL}/import-contacts`, {
                method: 'POST',
                body: formData,
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to import contacts');
            }
            return response.json();
        } catch (error) {
            console.error('Failed to import contacts:', error);
            throw error;
        }
    },
    
    // Download sample CSV template
    downloadSampleCSV() {
        // Create sample CSV content
        const headers = "name,phone,email,notes,tag,last_transaction\n";
        const row1 = "John Doe,0712345678,john@example.com,New client,Client,0\n";
        const row2 = "Jane Smith,0723456789,jane@example.com,Business partner,Partner,100\n";
        const csvContent = headers + row1 + row2;
        
        // Create a Blob with the CSV content
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        
        // Create a link to download the file
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'contacts_template.csv');
        document.body.appendChild(link);
        
        // Trigger the download
        link.click();
        
        // Clean up
        setTimeout(() => {
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }, 100);
        
        return true;
    },

    async getMonitoredUsers(token) {
        const response = await fetch('http://localhost:8000/api/admin/monitored-users', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error('Failed to fetch monitored users');
        return await response.json();
    }
}; 