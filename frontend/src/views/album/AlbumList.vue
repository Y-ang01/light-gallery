<template>
  <div class="album-list-container">
    <div class="page-header">
      <h2 class="page-title">图片集管理</h2>
      <div class="header-actions">
        <el-button type="primary" icon="Plus" @click="goToCreateAlbum"> 创建图片集 </el-button>
        <el-button type="text" icon="Trash" @click="goToRecycleAlbum">
          回收站
          <el-badge :value="recycleCount" class="badge" />
        </el-button>
      </div>
    </div>

    <!-- 筛选工具栏 -->
    <div class="filter-toolbar">
      <el-select
        v-model="filterPermission"
        placeholder="全部权限"
        class="permission-select"
        @change="fetchAlbumList"
      >
        <el-option label="全部" value="" />
        <el-option label="公开" value="PUBLIC" />
        <el-option label="密码保护" value="PROTECTED" />
        <el-option label="私密" value="PRIVATE" />
      </el-select>

      <el-input
        v-model="searchKeyword"
        placeholder="搜索图片集名称..."
        class="search-input"
        @keyup.enter="fetchAlbumList"
      >
        <template #append>
          <el-button icon="Search" @click="fetchAlbumList" />
        </template>
      </el-input>
    </div>

    <!-- 图片集列表 -->
    <div class="album-grid">
      <!-- 创建图片集卡片 -->
      <el-card class="album-card create-card" @click="goToCreateAlbum">
        <div class="create-album">
          <el-icon class="create-icon">
            <Plus />
          </el-icon>
          <p class="create-text">创建图片集</p>
        </div>
      </el-card>

      <!-- 图片集卡片 -->
      <el-card
        v-for="album in albumList"
        :key="album.id"
        class="album-card"
        @click="goToAlbumDetail(album.id)"
      >
        <div class="album-cover">
          <el-image
            :src="album.cover_image_id ? getImageUrl(album.cover_image_id) : defaultCover"
            fit="cover"
          >
            <div class="image-placeholder" slot="error">
              <el-icon class="placeholder-icon">
                <Collection />
              </el-icon>
            </div>
          </el-image>
          <div class="album-count">
            <el-icon class="count-icon">
              <Picture />
            </el-icon>
            <span class="count-text">{{ album.image_count }}张</span>
          </div>
        </div>
        <div class="album-info">
          <h3 class="album-name">{{ album.name }}</h3>
          <div class="album-meta">
            <span class="album-permission">
              <el-icon class="permission-icon">
                <Lock v-if="album.permission === 'PRIVATE'" />
                <LockFilled v-else-if="album.permission === 'PROTECTED'" />
                <Unlock v-else />
              </el-icon>
              {{ getPermissionText(album.permission) }}
            </span>
            <span class="album-time">
              {{ formatDateTime(album.created_at, 'YYYY-MM-DD') }}
            </span>
          </div>
        </div>
        <div class="album-actions">
          <el-button type="text" icon="Edit" @click.stop="handleEditAlbum(album)" />
          <el-button type="text" icon="Delete" @click.stop="handleDeleteAlbum(album.id)" />
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-if="albumList.length === 0 && !isLoading">
      <el-empty description="暂无图片集" class="empty-album">
        <el-button type="primary" @click="goToCreateAlbum"> 创建图片集 </el-button>
      </el-empty>
    </div>

    <!-- 加载状态 -->
    <div class="loading-state" v-if="isLoading">
      <el-loading type="spinner" text="加载中..." />
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="total > 0 && !isLoading">
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="currentPage"
        :page-sizes="[12, 24, 36]"
        :page-size="pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAlbumStore } from '@/store/modules/album'
import { formatDateTime } from '@/utils/format'

// 导入图标
import {
  Plus,
  Collection,
  Picture,
  Lock,
  LockFilled,
  Unlock,
  Edit,
  Delete,
  Trash,
} from '@element-plus/icons-vue'

// 状态管理
const albumStore = useAlbumStore()
const router = useRouter()

// 响应式数据
const currentPage = ref(1)
const pageSize = ref(12)
const filterPermission = ref('')
const searchKeyword = ref('')
const isLoading = ref(false)

// 默认封面图
const defaultCover = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

// 计算属性
const albumList = computed(() => albumStore.albumList)
const total = computed(() => albumStore.total)
const recycleCount = computed(() => albumStore.recycleAlbumList.length)

// 方法
// 初始化加载
onMounted(() => {
  fetchAlbumList()
  fetchRecycleAlbums()
})

// 获取图片集列表
const fetchAlbumList = () => {
  isLoading.value = true
  albumStore
    .fetchAlbumList(currentPage.value, pageSize.value, filterPermission.value)
    .finally(() => {
      isLoading.value = false
    })
}

// 获取回收站图片集
const fetchRecycleAlbums = () => {
  albumStore.fetchRecycleAlbums()
}

// 处理分页大小变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchAlbumList()
}

// 处理页码变化
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchAlbumList()
}

// 前往创建图片集
const goToCreateAlbum = () => {
  router.push('/albums/create')
}

// 前往图片集详情
const goToAlbumDetail = (albumId: string) => {
  router.push(`/albums/${albumId}`)
}

// 前往回收站
const goToRecycleAlbum = () => {
  router.push('/albums/recycle')
}

// 处理编辑图片集
const handleEditAlbum = (album: any) => {
  ElMessage.info('编辑功能开发中')
  // 实际项目中应打开编辑弹窗或跳转到编辑页面
}

// 处理删除图片集
const handleDeleteAlbum = async (albumId: string) => {
  try {
    await ElMessageBox.confirm('确定要删除该图片集吗？删除后将移至回收站', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    const success = await albumStore.deleteAlbumAction(albumId)
    if (success) {
      ElMessage.success('删除成功')
      fetchAlbumList()
      fetchRecycleAlbums()
    } else {
      ElMessage.error('删除失败')
    }
  } catch (error) {
    // 取消删除
  }
}

// 获取权限文本
const getPermissionText = (permission: string) => {
  switch (permission) {
    case 'PUBLIC':
      return '公开'
    case 'PROTECTED':
      return '密码保护'
    case 'PRIVATE':
      return '私密'
    default:
      return '未知'
  }
}

// 获取图片URL（简化版，实际项目应从接口获取完整URL）
const getImageUrl = (imageId: string) => {
  return `/static/thumbnails/${imageId}.jpg`
}
</script>

<style scoped lang="scss">
.album-list-container {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
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

.badge {
  background-color: #f56c6c !important;
}

.filter-toolbar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  align-items: center;
}

.permission-select {
  width: 160px;
}

.search-input {
  flex: 1;
  max-width: 400px;
}

.album-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.album-card {
  height: 100%;
  border-radius: 8px !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  cursor: pointer;
  overflow: hidden;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
  }
}

.create-card {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f8f9fa !important;
  border: 1px dashed #dcdfe6 !important;
}

.create-album {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 0;
}

.create-icon {
  font-size: 32px;
  color: #1989fa;
  margin-bottom: 12px;
}

.create-text {
  font-size: 16px;
  color: #666;
}

.album-cover {
  position: relative;
  width: 100%;
  height: 160px;
  border-radius: 8px 8px 0 0;
  overflow: hidden;
}

.album-cover img {
  width: 100%;
  height: 100%;
}

.image-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background-color: #f5f7fa;
}

.placeholder-icon {
  font-size: 48px;
  color: #ccc;
}

.album-count {
  position: absolute;
  bottom: 0;
  right: 0;
  display: flex;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.5);
  color: #fff;
  padding: 4px 8px;
  font-size: 12px;
  border-radius: 4px 0 0 0;
}

.count-icon {
  margin-right: 4px;
  font-size: 14px;
}

.album-info {
  padding: 16px;
}

.album-name {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 500;
  color: #2c3e50;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.album-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
}

.album-permission {
  display: flex;
  align-items: center;
}

.permission-icon {
  margin-right: 4px;
  font-size: 14px;
}

.album-actions {
  display: flex;
  justify-content: flex-end;
  padding: 0 16px 16px;
  gap: 8px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.empty-album {
  --el-empty-padding: 0 !important;
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

// 响应式适配
@media (max-width: 768px) {
  .album-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  }

  .album-cover {
    height: 120px;
  }

  .album-name {
    font-size: 14px;
  }

  .album-meta {
    flex-direction: column;
    gap: 4px;
  }
}
</style>
