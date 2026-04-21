<template>
  <div class="create-page">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="config-panel">
          <template #header>
            <span>创作配置</span>
          </template>

          <el-form label-position="top">
            <el-form-item label="公文类型">
              <el-select v-model="form.docType" placeholder="选择公文类型" style="width: 100%">
                <el-option label="通知" value="notice" />
                <el-option label="命令" value="command" />
                <el-option label="报告" value="report" />
                <el-option label="总结" value="summary" />
                <el-option label="纪要" value="memo" />
              </el-select>
            </el-form-item>

            <el-form-item label="主题/标题">
              <el-input v-model="form.topic" placeholder="输入公文主题" />
            </el-form-item>

            <el-form-item label="参考文档">
              <el-select
                v-model="form.referenceDocs"
                multiple
                placeholder="选择参考文档（可选）"
                style="width: 100%"
              >
                <el-option
                  v-for="doc in documents"
                  :key="doc.name"
                  :label="doc.name"
                  :value="doc.name"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="字数要求">
              <el-input-number v-model="form.wordCount" :min="200" :max="5000" :step="100" style="width: 100%" />
            </el-form-item>

            <el-form-item label="风格">
              <el-select v-model="form.style" style="width: 100%">
                <el-option label="正式" value="正式" />
                <el-option label="简洁" value="简洁" />
                <el-option label="详细" value="详细" />
              </el-select>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="startGeneration" :loading="isGenerating" style="width: 100%">
                {{ isGenerating ? '正在创作...' : '开始创作' }}
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card class="preview-panel">
          <template #header>
            <div class="preview-header">
              <span>内容预览</span>
              <div v-if="generatedContent">
                <el-button size="small" @click="startGeneration" :loading="isGenerating">重新生成</el-button>
                <el-button size="small" type="warning" @click="optimizeContent" :loading="isOptimizing">优化建议</el-button>
                <el-button size="small" type="success" @click="copyContent">复制内容</el-button>
              </div>
            </div>
          </template>

          <div v-if="!generatedContent && !isGenerating" class="empty-state">
            <el-empty description="配置创作参数后点击「开始创作」" />
          </div>

          <div v-else class="content-area">
            <div class="streaming-content" v-html="renderedContent"></div>
            <el-button
              v-if="isGenerating"
              type="danger"
              size="small"
              @click="stopGeneration"
              style="margin-top: 12px"
            >
              停止生成
            </el-button>
          </div>

          <div v-if="sources.length > 0" class="sources-section">
            <el-divider>参考来源</el-divider>
            <el-tag v-for="src in sources" :key="src" size="small" style="margin-right: 8px">
              {{ src }}
            </el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const form = ref({
  docType: 'notice',
  topic: '',
  referenceDocs: [],
  wordCount: 800,
  style: '正式',
})

const documents = ref([])
const generatedContent = ref('')
const isGenerating = ref(false)
const isOptimizing = ref(false)
const sources = ref([])
const currentTaskId = ref(null)
const abortController = ref(null)

const renderedContent = computed(() => {
  return generatedContent.value.replace(/\n/g, '<br>')
})

onMounted(() => {
  loadDocuments()
})

async function loadDocuments() {
  try {
    const res = await axios.get('/api/documents/list')
    documents.value = res.data.documents || []
  } catch (e) {
    console.error('Failed to load documents:', e)
  }
}

async function startGeneration() {
  if (!form.value.topic) {
    ElMessage.warning('请输入公文主题')
    return
  }

  stopGeneration()

  isGenerating.value = true
  generatedContent.value = ''
  sources.value = []

  try {
    const createRes = await axios.post('/api/generation/create', {
      topic: form.value.topic,
      doc_type: form.value.docType,
      reference_docs: form.value.referenceDocs,
      parameters: {
        word_count: form.value.wordCount,
        style: form.value.style,
      },
    })

    currentTaskId.value = createRes.data.task_id
    await streamContent(currentTaskId.value)
  } catch (e) {
    ElMessage.error('创建失败: ' + (e.response?.data?.detail || e.message))
    isGenerating.value = false
  }
}

async function streamContent(taskId) {
  abortController.value = new AbortController()

  try {
    const response = await fetch(`/api/generation/${taskId}/stream`, {
      signal: abortController.value.signal,
    })

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const text = decoder.decode(value, { stream: true })
      const lines = text.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.done) {
              isGenerating.value = false
              break
            }
            if (data.token) {
              generatedContent.value += data.token
            }
          } catch (e) {
            // ignore parse errors
          }
        }
      }
    }
  } catch (e) {
    if (e.name !== 'AbortError') {
      ElMessage.error('流式读取失败: ' + e.message)
    }
  } finally {
    isGenerating.value = false
  }
}

function stopGeneration() {
  if (abortController.value) {
    abortController.value.abort()
    abortController.value = null
  }
  isGenerating.value = false
}

async function optimizeContent() {
  if (!currentTaskId.value || !generatedContent.value) return

  isOptimizing.value = true
  const prevContent = generatedContent.value
  generatedContent.value = '--- 优化建议 ---\n\n'

  try {
    const response = await fetch(`/api/generation/${currentTaskId.value}/optimize`, {
      method: 'POST',
    })

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const text = decoder.decode(value, { stream: true })
      const lines = text.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.done) break
            if (data.token) {
              generatedContent.value += data.token
            }
          } catch (e) {
            // ignore
          }
        }
      }
    }

    generatedContent.value += '\n\n--- 原文 ---\n\n' + prevContent
  } catch (e) {
    ElMessage.error('优化失败: ' + e.message)
  } finally {
    isOptimizing.value = false
  }
}

function copyContent() {
  navigator.clipboard.writeText(generatedContent.value).then(() => {
    ElMessage.success('已复制到剪贴板')
  })
}
</script>

<style scoped>
.create-page {
  padding: 0;
}

.config-panel {
  min-height: 500px;
}

.preview-panel {
  min-height: 500px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.content-area {
  white-space: pre-wrap;
  line-height: 1.8;
  font-size: 14px;
}

.streaming-content {
  min-height: 200px;
}

.sources-section {
  margin-top: 16px;
}
</style>
