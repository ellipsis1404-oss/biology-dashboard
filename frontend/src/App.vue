<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div id="app-container">
    <header class="app-header">
      <div class="logo">
        <RouterLink to="/">
          <h2>Biology Progress Dashboard</h2>
        </RouterLink>
      </div>
      <nav class="main-nav">
        <RouterLink to="/">Dashboard</RouterLink>
        <!-- --- ADD THIS NEW LINK --- -->
        <RouterLink to="/admin">Admin</RouterLink>
      </nav>
    </header>
    
    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<style>
/* Global styles from before remain the same */
body{margin:0;background-color:#2c3e50;color:#ecf0f1;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}#app-container{display:flex;flex-direction:column;min-height:100vh}main.app-main{flex-grow:1;padding:20px 40px}.app-header{display:flex;justify-content:space-between;align-items:center;padding:10px 40px;background-color:#34495e;border-bottom:2px solid #76D7C4}.logo a{text-decoration:none;color:#ecf0f1}.logo h2{margin:0;font-weight:600}.main-nav a{color:#bdc3c7;text-decoration:none;margin-left:20px;padding:8px 12px;border-radius:5px;transition:background-color .2s ease,color .2s ease}.main-nav a:hover{background-color:#2c3e50;color:#fff}.main-nav a.router-link-exact-active{color:#fff;background-color:#16a085}
</style>