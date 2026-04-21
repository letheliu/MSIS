<template>
  <div class="documents-page">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>文档库配置</span>
        </div>
      </template>
      <el-form :model="configForm" label-width="120px">
        <el-form-item label="文档库路径">
          <el-input v-model="configForm.document_path" placeholder="文档库存储路径" />
        </el-form-item>
        <el-form-item label="自动索引">
          <el-switch v-model="configForm.auto_reindex" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="updateConfig">更新配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="upload-card">
      <template #header>
        <div class="card-header">
          <span>上传文档</span>
        </div>
      </template>
      <el-upload
        ref="uploadRef"
        :action="uploadUrl"
        :headers="uploadHeaders"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :before-upload="beforeUpload"
        :file-list="fileList"
        :auto-upload="false"
        drag
        multiple
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持格式: .txt, .md, .json, .docx, .pdf
          </div>
        </template>
      </el-upload>
      <div style="margin-top: 16px;">
        <el-button type="primary" @click="startUpload">开始上传</el-button>
        <el-button @click="clearFiles">清空列表</el-button>
      </div>
    </el-card>

    <el-card class="list-card">
      <template #header>
        <div class="card-header">
          <span>已索引文档</span>
          <el-button type="primary" size="small" @click="refreshDocuments" :loading="loading">
            <el-icon><refresh /></el-icon> 刷新
          </el-button>
        </div>
      </template>
      <el-table :data="documents" style="width: 100%">
        <el-table-column prop="name" label="文件名" />
        <el-table-column prop="size" label="大小" width="120">
          <template #default="{ row }">
            {{ formatSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="deleteDocument(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="documents.length === 0" class="empty-tip">
        暂无已索引文档
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Refresh } from '@element-plus/icons-vue'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

const configForm = ref({
  document_path: '',
  auto_reindex: true
})

const documents = ref([])
const loading = ref(false)
const uploadUrl = `${API_BASE}/api/documents/upload`
const uploadHeaders = {}
const uploadRef = ref(null)
const fileList = ref([])

// 获取配置
const fetchConfig = async () => {
  try {
    const response = await axios.get(`${API_BASE}/api/documents/config`)
    configForm.value = {
      document_path: response.data.document_path,
      auto_reindex: response.data.auto_reindex
    }
  } catch (error) {
    ElMessage.error('获取配置失败')
  }
}

// 更新配置
const updateConfig = async () => {
  try {
    await axios.put(`${API_BASE}/api/documents/config`, configForm.value)
    ElMessage.success('配置更新成功')
  } catch (error) {
    ElMessage.error('配置更新失败')
  }
}

// 获取文档列表
const fetchDocuments = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE}/api/documents/list`)
    documents.value = response.data.documents
  } catch (error) {
    ElMessage.error('获取文档列表失败')
  } finally {
    loading.value = false
  }
}

// 刷新文档列表
const refreshDocuments = async () => {
  await fetchDocuments()
  ElMessage.success('刷新成功')
}

// 上传前验证
const beforeUpload = (file) => {
  const allowedTypes = ['.txt', '.md', '.json', '.docx', '.pdf']
  const fileName = file.name.toLowerCase()
  const isValid = allowedTypes.some(type => fileName.endsWith(type))
  if (!isValid) {
    ElMessage.error('只支持 .txt, .md, .json, .docx, .pdf 格式的文件')
    return false
  }
  return true
}

// 开始上传
const startUpload = () => {
  uploadRef.value?.submit()
}

// 上传成功
const handleUploadSuccess = (response, file) => {
  if (response.success) {
    ElMessage.success(`上传成功: ${file.name}`)
    fetchDocuments()
  } else {
    ElMessage.error(`上传失败: ${file.name} - ${response.error || '未知错误'}`)
  }
}

// 上传失败
const handleUploadError = (error, file) => {
  ElMessage.error(`上传失败: ${file.name}`)
}

// 清空文件列表
const clearFiles = () => {
  fileList.value = []
}

// 删除文档
const deleteDocument = async (doc) => {
  try {
    await ElMessage.info('删除功能需要后端 API 支持')
    // TODO: 实现删除 API 调用
    // await axios.delete(`${API_BASE}/api/documents/${doc.name}`)
    // fetchDocuments()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 格式化文件大小
const formatSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

onMounted(() => {
  fetchConfig()
  fetchDocuments()
})
</script>

<style scoped>
.documents-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.config-card,
.upload-card,
.list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.empty-tip {
  text-align: center;
  padding: 40px;
  color: #909399;
}

:deep(.el-upload-dragger) {
  width: 100%;
}
</style>
