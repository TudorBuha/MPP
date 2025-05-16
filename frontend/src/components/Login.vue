<template>
  <div class="login-container">
    <div class="login-box">
      <h2 v-if="!showRegister">UBBank Login</h2>
      <h2 v-else>Register</h2>
      <form v-if="!showRegister" @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">Username</label>
          <input
            type="text"
            id="username"
            v-model="username"
            required
            placeholder="Enter your username"
          />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input
            type="password"
            id="password"
            v-model="password"
            required
            placeholder="Enter your password"
          />
        </div>
        <button type="submit" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
        <p v-if="error" class="error">{{ error }}</p>
        <p class="toggle-link">
          Don't have an account?
          <a href="#" @click.prevent="showRegister = true">Register</a>
        </p>
      </form>
      <form v-else @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="reg-username">Username</label>
          <input
            type="text"
            id="reg-username"
            v-model="regUsername"
            required
            placeholder="Choose a username"
          />
        </div>
        <div class="form-group">
          <label for="reg-password">Password</label>
          <input
            type="password"
            id="reg-password"
            v-model="regPassword"
            required
            placeholder="Choose a password"
          />
        </div>
        <button type="submit" :disabled="loading">
          {{ loading ? 'Registering...' : 'Register' }}
        </button>
        <p v-if="regError" class="error">{{ regError }}</p>
        <p class="toggle-link">
          Already have an account?
          <a href="#" @click.prevent="showRegister = false">Login</a>
        </p>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'LoginPage',
  data() {
    return {
      username: '',
      password: '',
      loading: false,
      error: null,
      showRegister: false,
      regUsername: '',
      regPassword: '',
      regError: null
    };
  },
  methods: {
    async handleLogin() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.post('http://localhost:8000/api/auth/login', {
          username: this.username,
          password: this.password
        });
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        if (response.data.user.role === 'admin') {
          this.$router.push('/admin');
        } else {
          this.$router.push('/');
        }
      } catch (err) {
        this.error = err.response?.data?.detail || 'Login failed. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    async handleRegister() {
      this.loading = true;
      this.regError = null;
      try {
        await axios.post('http://localhost:8000/api/auth/register', {
          username: this.regUsername,
          password: this.regPassword
        });
        // Registration successful, switch to login
        this.showRegister = false;
        this.username = this.regUsername;
        this.password = this.regPassword;
        this.regUsername = '';
        this.regPassword = '';
        this.regError = null;
      } catch (err) {
        this.regError = err.response?.data?.detail || 'Registration failed. Please try again.';
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.login-box {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

button {
  width: 100%;
  padding: 0.75rem;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

button:hover {
  background-color: #3aa876;
}

button:disabled {
  background-color: #a8d5c2;
  cursor: not-allowed;
}

.error {
  color: #dc3545;
  text-align: center;
  margin-top: 1rem;
}

.toggle-link {
  text-align: center;
  margin-top: 1rem;
}

.toggle-link a {
  color: #42b983;
  cursor: pointer;
  text-decoration: underline;
}
</style> 