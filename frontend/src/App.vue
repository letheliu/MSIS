<template>
  <div id="app">
    <el-container>
      <el-header class="header">
        <h1>MSIS - 内网军队公文写作助手</h1>
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
}
.header h1 {
  margin: 0;
  font-size: 20px;
}
</style>
