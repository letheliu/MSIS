<template>
  <div id="app">
    <el-container>
      <el-header class="header">
        <h1>MSIS - 内网军队公文写作助手</h1>
        <el-menu
          :default-active="$route.path"
          mode="horizontal"
          background-color="#409EFF"
          text-color="#ffffff"
          active-text-color="#ffd04b"
          class="nav-menu"
          router
        >
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/search">检索</el-menu-item>
          <el-menu-item index="/templates">模板库</el-menu-item>
          <el-menu-item index="/documents">文档库</el-menu-item>
        </el-menu>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
</script>

<style scoped>
.header {
  background-color: #409EFF;
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
}
.header h1 {
  margin: 0 20px 0 0;
  font-size: 20px;
  white-space: nowrap;
}
.nav-menu {
  border: none;
  flex: 1;
}
.nav-menu.el-menu--horizontal {
  border-bottom: none;
}
</style>
