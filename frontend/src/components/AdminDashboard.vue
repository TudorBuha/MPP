<template>
  <div class="admin-dashboard">
    <h2>Monitored Users</h2>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="loading">Loading...</div>
    <table v-if="!loading && monitoredUsers.length">
      <thead>
        <tr>
          <th>User ID</th>
          <th>Detected At</th>
          <th>Reason</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in monitoredUsers" :key="user.user_id">
          <td>{{ user.user_id }}</td>
          <td>{{ user.detected_at }}</td>
          <td>{{ user.reason }}</td>
        </tr>
      </tbody>
    </table>
    <div v-if="!loading && !monitoredUsers.length">No monitored users.</div>
  </div>
</template>

<script>
import { api } from '../services/api'

export default {
  name: 'AdminDashboard',
  data() {
    return {
      monitoredUsers: [],
      loading: false,
      error: null
    }
  },
  async created() {
    this.loading = true;
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        this.error = 'Not authenticated.';
        this.loading = false;
        return;
      }
      this.monitoredUsers = (await api.getMonitoredUsers(token)).monitored_users;
    } catch (e) {
      this.error = e.message;
    } finally {
      this.loading = false;
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  max-width: 700px;
  margin: 40px auto;
  background: rgba(255,255,255,0.9);
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
}
h2 {
  text-align: center;
  margin-bottom: 24px;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 16px;
}
th, td {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}
th {
  background: #2193b0;
  color: #fff;
}
.error {
  color: #e74c3c;
  margin-bottom: 16px;
  text-align: center;
}
</style> 