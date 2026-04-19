<template>
  <div class="home">
    <el-card class="welcome-card">
      <h2>欢迎使用 MSIS</h2>
      <p>基于 Sirchmunk 的内网军队公文写作助手</p>
    </el-card>

    <el-row :gutter="20" class="feature-grid">
      <el-col :span="8">
        <el-card @click="$router.push('/search')" class="feature-card">
          <template #header>智能检索</template>
          <p>从公文库中快速检索相关文档</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card @click="$router.push('/templates')" class="feature-card">
          <template #header>模板库</template>
          <p>使用预设模板快速生成公文</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="feature-card">
          <template #header>辅助校对</template>
          <p>公文格式和用语规范性检查</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
</script>

<style scoped>
.welcome-card {
  margin-bottom: 30px;
  text-align: center;
}
.feature-grid {
  margin-top: 20px;
}
.feature-card {
  cursor: pointer;
  transition: transform 0.2s;
}
.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
</style>
