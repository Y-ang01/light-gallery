<!-- src/views/blog/BlogDraft.vue -->
<template>
  <div class="blog-draft-container">
    <div class="page-header">
      <el-button type="text" icon="ArrowLeft" class="back-button" @click="goBack"> 返回 </el-button>
      <h2 class="page-title">博客草稿箱</h2>
      <div class="header-actions">
        <el-button type="primary" icon="Edit" @click="goToCreate"> 新建草稿 </el-button>
      </div>
    </div>

    <!-- 筛选工具栏 -->
    <div class="filter-toolbar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索草稿标题..."
        class="search-input"
        @keyup.enter="fetchDrafts"
      >
        <template #append>
          <el-button icon="Search" @click="fetchDrafts" />
        </template>
      </el-input>

      <el-select
        v-model="sortType"
        placeholder="排序方式"
        class="sort-select"
        @change="fetchDrafts"
      >
        <el-option label="最新创建" value="created_at_desc" />
        <el-option label="最早创建" value="created_at_asc" />
        <el-option label="最近修改" value="updated_at_desc" />
      </el-select>
    </div>

    <!-- 草稿列表 -->
    <el-card class="draft-list-card" v-loading="isLoading">
      <el-table :data="draftList" border stripe class="draft-table" @row-click="handleRowClick">
        <el-table-column label="标题" prop="title" min-width="200">
          <template #default="scope">
            <div class="draft-title">
              {{ scope.row.title || '无标题草稿' }}
              <el-tag size="mini" type="info" class="draft-tag"> 草稿 </el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="创建时间" prop="created_at" width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="最后修改" prop="updated_at" width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.updated_at) }}
          </template>
        </el-table-column>

        <el-table-column label="标签" width="200">
          <template #default="scope">
            <el-tag
              v-for="(tag, index) in scope.row.tags"
              :key="index"
              size="small"
              class="tag-item"
            >
              {{ tag }}
            </el-tag>
            <span v-if="scope.row.tags.length === 0" class="empty-tags">无标签</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button
              type="text"
              icon="Edit"
              @click.stop="goToEdit(scope.row.id)"
              class="edit-button"
            >
              编辑
            </el-button>
            <el-button
              type="text"
              icon="Share"
              @click.stop="handlePublish(scope.row.id)"
              class="publish-button"
            >
              发布
            </el-button>
            <el-button
              type="text"
              icon="Delete"
              @click.stop="handleDelete(scope.row.id)"
              class="delete-button"
              danger
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <div class="empty-state" v-if="draftList.length === 0 && !isLoading">
        <el-empty description="暂无草稿" class="empty-drafts">
          <el-button type="primary" @click="goToCreate"> 新建草稿 </el-button>
        </el-empty>
      </div>

      <!-- 分页 -->
      <div class="pagination" v-if="total > 0 && !isLoading">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 30]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useBlogStore } from '@/store/modules/blog'
import { formatDateTime } from '@/utils/format'

// 导入图标
import { ArrowLeft, Edit, Search, Share, Delete } from '@element-plus/icons-vue'

// 状态管理
const blogStore = useBlogStore()
const router = useRouter()

// 响应式数据
const isLoading = ref(false)
const draftList = ref<any[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchKeyword = ref('')
const sortType = ref('updated_at_desc') // created_at_desc / created_at_asc / updated_at_desc

// 方法
onMounted(() => {
  fetchDrafts()
})

// 获取草稿列表
const fetchDrafts = async () => {
  try {
    isLoading.value = true

    // 解析排序参数
    const [sortField, sortOrder] = sortType.value.split('_')

    const success = await blogStore.fetchBlogList(
      currentPage.value,
      pageSize.value,
      searchKeyword.value,
      sortField as 'created_at' | 'updated_at',
      sortOrder as 'asc' | 'desc',
      undefined,
      true, // 只查询草稿
    )

    if (success) {
      draftList.value = blogStore.blogList
      total.value = blogStore.total
    } else {
      ElMessage.error('获取草稿列表失败')
    }
  } catch (error) {
    console.error('获取草稿列表失败:', error)
    ElMessage.error('获取草稿列表失败')
  } finally {
    isLoading.value = false
  }
}

// 处理分页大小变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchDrafts()
}

// 处理页码变化
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchDrafts()
}

// 返回上一页
const goBack = () => {
  router.push('/blog')
}

// 前往新建草稿
const goToCreate = () => {
  router.push('/blog/create')
}

// 前往编辑草稿
const goToEdit = (draftId: string) => {
  router.push(`/blog/edit/${draftId}`)
}

// 表格行点击（前往编辑）
const handleRowClick = (row: any) => {
  goToEdit(row.id)
}

// 发布草稿
const handlePublish = async (draftId: string) => {
  try {
    await ElMessageBox.confirm('确定要发布这篇草稿吗？发布后将变为正式博客', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info',
    })

    // 查找草稿
    const draft = draftList.value.find((item) => item.id === draftId)
    if (!draft) {
      ElMessage.error('草稿不存在')
      return
    }

    // 调用发布接口（更新为非草稿状态）
    const success = await blogStore.updateBlogPostAction(draftId, {
      is_draft: false,
    })

    if (success) {
      ElMessage.success('博客发布成功')
      fetchDrafts() // 刷新草稿列表
    } else {
      ElMessage.error('博客发布失败')
    }
  } catch (error) {
    // 用户取消发布
  }
}

// 删除草稿
const handleDelete = async (draftId: string) => {
  try {
    await ElMessageBox.confirm('确定要删除这篇草稿吗？删除后将无法恢复', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    const success = await blogStore.deleteBlogPostAction(draftId)
    if (success) {
      ElMessage.success('草稿删除成功')
      fetchDrafts() // 刷新草稿列表
    } else {
      ElMessage.error('草稿删除失败')
    }
  } catch (error) {
    // 用户取消删除
  }
}
</script>

<style scoped lang="scss">
.blog-draft-container {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 16px;
  flex-wrap: wrap;
}

.back-button {
  color: #666 !important;
}

.page-title {
  margin: 0;
  color: #2c3e50;
  font-size: 20px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.filter-toolbar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  max-width: 400px;
}

.sort-select {
  width: 160px;
}

.draft-list-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-radius: 8px !important;
  overflow: hidden;
}

.draft-table {
  width: 100%;
}

.draft-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #2c3e50;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.draft-tag {
  margin-left: auto;
}

.tag-item {
  margin-right: 4px;
  background-color: #f5f7fa;
  color: #666;
}

.empty-tags {
  font-size: 12px;
  color: #999;
}

.edit-button {
  color: #1989fa !important;
}

.publish-button {
  color: #67c23a !important;
}

.delete-button {
  color: #f56c6c !important;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
  background-color: #f8f9fa;
}

.empty-drafts {
  --el-empty-padding: 0 !important;
}

.pagination {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

// 响应式适配
@media (max-width: 1200px) {
  .draft-table {
    font-size: 14px;
  }

  .el-table-column {
    min-width: 120px;
  }
}

@media (max-width: 768px) {
  .filter-toolbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .search-input {
    width: 100%;
    max-width: none;
  }

  .sort-select {
    width: 100%;
  }

  .draft-table {
    font-size: 13px;
  }

  .el-table-column.fixed-right {
    position: sticky;
    right: 0;
    background: #fff;
    z-index: 10;
  }
}
</style>
