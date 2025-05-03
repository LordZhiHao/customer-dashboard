<!-- App.vue -->
<template>
  <div id="app">
    <header class="app-header">
      <h1>Customer Dashboard</h1>
      <nav class="main-nav">
        <router-link to="/" class="nav-link">Dashboard</router-link>
        <router-link to="/analytics" class="nav-link">Analytics</router-link>
      </nav>
    </header>

    <main class="app-content">
      <router-view
        :newMember="latestMember"
        :newVisit="latestVisit"
        @member-added="onMemberAdded"
        @visit-added="onVisitAdded" />
    </main>

    <footer class="app-footer">
      <p>&copy; {{ new Date().getFullYear() }} Customer Management System</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: "App",
  data() {
    return {
      latestMember: null,
      latestVisit: null,
    };
  },
  methods: {
    onMemberAdded(member) {
      this.latestMember = member;
    },
    onVisitAdded(visit) {
      this.latestVisit = visit;
    },
  },
};
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f5f5f5;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  background-color: #4caf50;
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.main-nav {
  display: flex;
  gap: 20px;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-weight: 500;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-link:hover,
.router-link-active {
  background-color: rgba(255, 255, 255, 0.2);
}

.app-content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.app-footer {
  background-color: #f0f0f0;
  text-align: center;
  padding: 1rem;
  margin-top: 2rem;
  color: #666;
}

h1,
h2,
h3,
h4 {
  margin-bottom: 1rem;
  color: #333;
}

.btn {
  display: inline-block;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  text-align: center;
  transition: background-color 0.3s;
}

.form-control {
  display: block;
  width: 100%;
  padding: 8px 12px;
  font-size: 14px;
  line-height: 1.5;
  color: #495057;
  background-color: #fff;
  border: 1px solid #ced4da;
  border-radius: 4px;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-control:focus {
  border-color: #80bdff;
  outline: 0;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: inline-block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}
</style>
