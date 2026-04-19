<template>
  <div class="search-page">
    <el-card>
      <template #header>智能检索</template>

      <el-form :inline="true">
        <el-form-item>
          <el-input
            v-model="searchQuery"
            placeholder="输入关键词搜索公文..."
            style="width: 400px"
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button @click="handleSearch" :icon="Search">搜索</el-button>
            </template>
          </el-input>
        </el-form-item>
      </el-form>

      <el-divider />

      <div v-if="loading" class="loading">
        <el-skeleton :rows="3" animated />
      </div>

      <div v-else-if="searchResults.length > 0" class="results">
        <div
          v-for="result in searchResults"
          :key="result.id"
          class="result-item"
          @click="showDetail(result)"
        >
          <h3>{{ result.title }}</h3>
          <p>{{ result.content }}</p>
          <el-tag size="small">相关度: {{ result.score }}</el-tag>
        </div>
      </div>

      <el-empty v-else-if="searched" description="未找到相关文档" />
    </el-card>

    <el-dialog v-model="detailVisible" title="文档详情" width="600px">
      <div v-if="selectedDoc">
        <h3>{{ selectedDoc.title }}</h3>
        <p>{{ selectedDoc.content }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import axios from 'axios'

const searchQuery = ref('')
const searchResults = ref([])
const loading = ref(false)
const searched = ref(false)
const detailVisible = ref(false)
const selectedDoc = ref(null)

const handleSearch = async () => {
  if (!searchQuery.value.trim()) return

  loading.value = true
  searched.value = true

  try {
    const response = await axios.get('/api/search', {
      params: { q: searchQuery.value }
    })
    searchResults.value = response.data.results
  } catch (error) {
    console.error('搜索失败:', error)
  } finally {
    loading.value = false
  }
}

const showDetail = (doc) => {
  selectedDoc.value = doc
  detailVisible.value = true
}
</script>

<style scoped>
.loading {
  padding: 20px;
}

.result-item {
  padding: 15px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background 0.2s;
}

.result-item:hover {
  background: #f5f7fa;
}

.result-item h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.result-item p {
  margin: 0 0 8px 0;
  color: #606266;
}
</style>
