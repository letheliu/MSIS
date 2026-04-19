<template>
  <div class="templates-page">
    <el-card>
      <template #header>模板库</template>

      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>

      <el-row v-else :gutter="20" class="template-grid">
        <el-col
          v-for="template in templates"
          :key="template.id"
          :span="8"
        >
          <el-card @click="useTemplate(template)" class="template-card">
            <h3>{{ template.name }}</h3>
            <p>{{ template.description }}</p>
            <el-tag>{{ getTypeLabel(template.type) }}</el-tag>
          </el-card>
        </el-col>
      </el-row>

      <el-empty v-if="!loading && templates.length === 0" description="暂无模板" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const templates = ref([])
const loading = ref(false)

const typeLabels = {
  command: '命令',
  report: '报告',
  notice: '通知',
  summary: '总结',
  memo: '纪要'
}

onMounted(async () => {
  await loadTemplates()
})

const loadTemplates = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/templates')
    templates.value = response.data.templates
  } catch (error) {
    console.error('加载模板失败:', error)
    ElMessage.error('加载模板失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const getTypeLabel = (type) => {
  return typeLabels[type] || type
}

const useTemplate = (template) => {
  router.push(`/templates/${template.id}/edit`)
}
</script>

<style scoped>
.loading-container {
  padding: 20px;
}

.template-grid {
  margin-top: 20px;
}

.template-card {
  cursor: pointer;
  transition: transform 0.2s;
  margin-bottom: 20px;
}

.template-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.template-card h3 {
  margin: 0 0 10px 0;
}

.template-card p {
  margin: 0 0 15px 0;
  color: #606266;
}
</style>
