<template>
  <div id="app">
    <nav v-if="isLoggedIn">
      <router-link to="/">Home</router-link> |
      <router-link v-if="isAdmin" to="/admin">Admin Dashboard</router-link>
      <button class="logout-btn" @click="logout">Logout</button>
    </nav>
    <router-view/>
  </div>
</template>

<script>
export default {
  name: "App",
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem('token');
    },
    isAdmin() {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      return user.role === 'admin';
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      this.$router.push('/login');
    }
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
  margin: 0 10px;
}

nav a.router-link-exact-active {
  color: #42b983;
}

.logout-btn {
  margin-left: 10px;
  padding: 6px 16px;
  background: #e74c3c;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}
.logout-btn:hover {
  background: #c0392b;
}
</style>
