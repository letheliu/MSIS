<template>
  <div class="template-editor">
    <el-card>
      <template #header>
        <span>编辑公文 - {{ template?.name }}</span>
      </template>

      <el-form :model="form" label-width="100px">
        <el-form-item label="标题" required>
          <el-input v-model="form.title" placeholder="输入公文标题" />
        </el-form-item>

        <el-form-item label="内容" required>
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="12"
            placeholder="输入公文内容"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="generateDocument" :loading="generating">
            生成文档
          </el-button>
          <el-button @click="$router.back()">返回</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-dialog v-model="previewVisible" title="预览" width="800px">
      <div class="preview-content">
        <pre>{{ generatedContent }}</pre>
      </div>
      <template #footer>
        <el-button @click="copyContent">复制</el-button>
        <el-button type="primary" @click="previewVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const route = useRoute()
const template = ref(null)
const form = ref({ title: '', content: '' })
const generating = ref(false)
const generatedContent = ref('')
const previewVisible = ref(false)

onMounted(async () => {
  const templateId = route.params.id
  await loadTemplate(templateId)
})

const loadTemplate = async (id) => {
  try {
    const response = await axios.get('/api/templates')
    template.value = response.data.templates.find(t => t.id === parseInt(id))
  } catch (error) {
    ElMessage.error('加载模板失败')
  }
}

const generateDocument = async () => {
  if (!form.value.title || !form.value.content) {
    ElMessage.warning('请填写标题和内容')
    return
  }

  generating.value = true
  try {
    const response = await axios.post(`/api/templates/${template.value.id}/render`, form.value)
    generatedContent.value = response.data.content
    previewVisible.value = true
  } catch (error) {
    ElMessage.error('生成文档失败')
  } finally {
    generating.value = false
  }
}

const copyContent = () => {
  navigator.clipboard.writeText(generatedContent.value)
  ElMessage.success('已复制到剪贴板')
}
</script>

<style scoped>
.preview-content {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 4px;
}
.preview-content pre {
  white-space: pre-wrap;
  font-family: 'SimSun', serif;
  font-size: 16px;
}
</style>
