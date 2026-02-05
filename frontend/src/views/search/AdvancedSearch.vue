<template>
  <el-card class="search-card">
    <h2 class="card-title">高级搜索</h2>
    <el-form :model="searchForm" ref="searchFormRef" label-width="120px">
      <el-form-item label="搜索关键词">
        <el-input v-model="searchForm.keyword" placeholder="输入关键词（可选）" />
      </el-form-item>

      <el-form-item label="搜索类型">
        <el-select v-model="searchForm.type" placeholder="请选择搜索类型">
          <el-option label="全部" value="" />
          <el-option label="图片集" value="album" />
          <el-option label="图片" value="image" />
          <el-option label="博客" value="blog" />
        </el-select>
      </el-form-item>

      <el-form-item label="时间范围">
        <el-date-picker
          v-model="searchForm.timeRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
        />
      </el-form-item>

      <el-form-item label="权限类型" v-if="searchForm.type === 'album' || !searchForm.type">
        <el-select v-model="searchForm.permission" placeholder="请选择权限类型">
          <el-option label="全部" value="" />
          <el-option label="公开" value="public" />
          <el-option label="密码保护" value="protected" />
          <el-option label="私密" value="private" />
        </el-select>
      </el-form-item>

      <el-form-item label="文件类型" v-if="searchForm.type === 'image' || !searchForm.type">
        <el-select v-model="searchForm.fileType" placeholder="请选择文件类型" multiple>
          <el-option label="JPG/JPEG" value="image/jpeg" />
          <el-option label="PNG" value="image/png" />
          <el-option label="RAW" value="image/raw" />
          <el-option label="CR2" value="image/cr2" />
          <el-option label="NEF" value="image/nef" />
          <el-option label="ARW" value="image/arw" />
        </el-select>
      </el-form-item>

      <el-form-item label="相机型号" v-if="searchForm.type === 'image' || !searchForm.type">
        <el-input v-model="searchForm.camera" placeholder="输入相机型号（可选）" />
      </el-form-item>

      <el-form-item label="标签" v-if="searchForm.type === 'blog' || !searchForm.type">
        <el-tag-input v-model="searchForm.tags" placeholder="输入标签，按Enter确认" />
      </el-form-item>

      <el-form-item label=" ">
        <el-button type="primary" @click="handleSearch" :loading="loading"> 开始搜索 </el-button>
        <el-button type="text" @click="resetForm" style="margin-left: 10px"> 重置 </el-button>
      </el-form-item>
    </el-form>

    <!-- 搜索结果 -->
    <div class="search-result" v-if="searchResult.length > 0">
      <div class="result-header">
        <h3>搜索结果（共 {{ total }} 条）</h3>
        <el-select
          v-model="resultSort"
          placeholder="排序方式"
          class="sort-select"
          @change="handleSort"
        >
          <el-option label="最新创建" value="created_at_desc" />
          <el-option label="最早创建" value="created_at_asc" />
          <el-option label="热门程度" value="view_count_desc" />
        </el-select>
      </div>

      <div class="result-tabs">
        <el-tabs v-model="activeResultTab">
          <el-tab-pane label="图片集" name="album" v-if="hasAlbumResult">
            <el-card class="result-item" v-for="item in albumResult" :key="item.id">
              <div class="item-header">
                <el-image
                  :src="item.cover_image_url || defaultCover"
                  class="item-cover"
                  fit="cover"
                />
                <div class="item-info">
                  <h4 class="item-name">{{ item.name }}</h4>
                  <p class="item-desc">{{ item.description || '无描述' }}</p>
                  <div class="item-meta">
                    <span>创建时间：{{ formatDate(item.created_at) }}</span>
                    <span>图片数量：{{ item.image_count }}</span>
                    <span>权限：{{ getPermissionText(item.permission) }}</span>
                  </div>
                </div>
              </div>
              <div class="item-actions">
                <el-button type="text" @click="goToAlbumDetail(item.id)"> 查看详情 </el-button>
              </div>
            </el-card>
          </el-tab-pane>

          <el-tab-pane label="图片" name="image" v-if="hasImageResult">
            <div class="image-grid">
              <el-card class="image-item" v-for="item in imageResult" :key="item.id">
                <el-image
                  :src="item.thumbnail_path || item.file_path"
                  :preview-src-list="[item.file_path]"
                  class="image-thumbnail"
                  fit="cover"
                />
                <div class="image-info">
                  <p class="image-name">{{ item.filename }}</p>
                  <p class="image-meta">
                    {{ item.file_type }} · {{ formatFileSize(item.file_size) }}
                  </p>
                </div>
                <div class="image-actions">
                  <el-button type="text" icon="Download" @click="downloadImage(item.id)" />
                  <el-button type="text" icon="Eye" @click="previewImage(item.file_path)" />
                </div>
              </el-card>
            </div>
          </el-tab-pane>

          <el-tab-pane label="博客" name="blog" v-if="hasBlogResult">
            <el-card class="result-item" v-for="item in blogResult" :key="item.id">
              <div class="item-header">
                <el-image
                  :src="item.cover_image_url || defaultCover"
                  class="blog-cover"
                  fit="cover"
                />
                <div class="item-info">
                  <h4 class="item-name">{{ item.title }}</h4>
                  <p class="item-desc">{{ item.content.substring(0, 100) }}...</p>
                  <div class="item-meta">
                    <span>作者：{{ item.author_username }}</span>
                    <span>创建时间：{{ formatDate(item.created_at) }}</span>
                    <span>阅读量：{{ item.view_count }}</span>
                    <span>评论数：{{ item.comment_count }}</span>
                  </div>
                  <div class="item-tags">
                    <el-tag v-for="tag in item.tags" :key="tag" size="small">
                      {{ tag }}
                    </el-tag>
                  </div>
                </div>
              </div>
              <div class="item-actions">
                <el-button type="text" @click="goToBlogDetail(item.id)"> 阅读全文 </el-button>
              </div>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 分页 -->
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="currentPage"
        :page-sizes="[10, 20, 50]"
        :page-size="pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        class="pagination"
      />
    </div>

    <!-- 空结果 -->
    <div class="empty-result" v-if="searchPerformed && searchResult.length === 0">
      <el-empty description="未找到符合条件的结果" />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElForm, ElImagePreview } from 'element-plus'
import * as searchApi from '@/api/search'
import { AlbumPermission } from '@/utils/permission'

const router = useRouter()
const searchFormRef = ref<InstanceType<typeof ElForm> | null>(null)
const loading = ref(false)
const searchPerformed = ref(false)

// 默认封面图
const defaultCover = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

// 搜索表单
const searchForm = ref({
  keyword: '',
  type: '',
  timeRange: [] as Date[],
  permission: '',
  fileType: [] as string[],
  camera: '',
  tags: [] as string[],
})

// 分页参数
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 排序参数
const resultSort = ref('created_at_desc')

// 搜索结果
const searchResult = ref<any[]>([])
const activeResultTab = ref('album')

// 分类结果
const albumResult = computed(() => {
  return searchResult.value.filter((item) => item.type === 'album')
})

const imageResult = computed(() => {
  return searchResult.value.filter((item) => item.type === 'image')
})

const blogResult = computed(() => {
  return searchResult.value.filter((item) => item.type === 'blog')
})

// 是否有对应类型结果
const hasAlbumResult = computed(() => albumResult.value.length > 0)
const hasImageResult = computed(() => imageResult.value.length > 0)
const hasBlogResult = computed(() => blogResult.value.length > 0)

// 格式化日期
const formatDate = (dateStr?: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString()
}

// 格式化文件大小
const formatFileSize = (size?: number) => {
  if (!size) return '0B'
  if (size < 1024) return `${size}B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(2)}KB`
  return `${(size / (1024 * 1024)).toFixed(2)}MB`
}

// 获取权限文本
const getPermissionText = (permission?: string) => {
  switch (permission) {
    case 'public':
      return '公开'
    case 'protected':
      return '密码保护'
    case 'private':
      return '私密'
    default:
      return '未知'
  }
}

// 处理搜索
const handleSearch = async () => {
  try {
    loading.value = true
    searchPerformed.value = true
    currentPage.value = 1

    // 构造搜索参数
    const params = {
      keyword: searchForm.value.keyword,
      type: searchForm.value.type,
      start_time: searchForm.value.timeRange[0]
        ? searchForm.value.timeRange[0].toISOString().split('T')[0]
        : undefined,
      end_time: searchForm.value.timeRange[1]
        ? searchForm.value.timeRange[1].toISOString().split('T')[0]
        : undefined,
      permission: searchForm.value.permission,
      file_type: searchForm.value.fileType.length > 0 ? searchForm.value.fileType : undefined,
      exif_camera: searchForm.value.camera,
      tags: searchForm.value.tags.length > 0 ? searchForm.value.tags : undefined,
      page: currentPage.value,
      pageSize: pageSize.value,
      sort: resultSort.value.split('_')[0],
      order: resultSort.value.split('_')[1],
    }

    // 调用高级搜索接口
    const res = await searchApi.advancedSearch(params)
    searchResult.value = res.data.items
    total.value = res.data.total

    // 自动切换到第一个有结果的标签
    if (hasAlbumResult.value) {
      activeResultTab.value = 'album'
    } else if (hasImageResult.value) {
      activeResultTab.value = 'image'
    } else if (hasBlogResult.value) {
      activeResultTab.value = 'blog'
    }
  } catch (error) {
    ElMessage.error('搜索失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 重置表单
const resetForm = () => {
  searchFormRef.value?.resetFields()
  searchForm.value = {
    keyword: '',
    type: '',
    timeRange: [],
    permission: '',
    fileType: [],
    camera: '',
    tags: [],
  }
  searchResult.value = []
  searchPerformed.value = false
  total.value = 0
}

// 处理排序变化
const handleSort = () => {
  handleSearch()
}

// 处理每页条数变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  handleSearch()
}

// 处理页码变化
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  handleSearch()
}

// 前往图片集详情
const goToAlbumDetail = (albumId: string) => {
  router.push(`/albums/${albumId}`)
}

// 前往博客详情
const goToBlogDetail = (blogId: string) => {
  router.push(`/blogs/${blogId}`)
}

// 下载图片
const downloadImage = (imageId: string) => {
  import('@/api/image').then(({ downloadImage }) => {
    downloadImage(imageId)
      .then((res) => {
        const blob = new Blob([res.data])
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `image_${imageId}.jpg`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      })
      .catch((err) => {
        ElMessage.error('下载失败')
      })
  })
}

// 预览图片
const previewImage = (imageUrl: string) => {
  ElImagePreview({
    urlList: [imageUrl],
    zIndex: 3000,
  })
}
</script>

<style scoped>
.search-card {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.card-title {
  margin: 0 0 20px 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.search-result {
  margin-top: 30px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.result-header h3 {
  margin: 0;
  color: #2c3e50;
}

.sort-select {
  width: 180px;
}

.result-tabs {
  margin-bottom: 20px;
}

.result-item {
  margin-bottom: 15px;
  transition: box-shadow 0.3s ease;
}

.result-item:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.item-header {
  display: flex;
  gap: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.item-cover {
  width: 120px;
  height: 120px;
  border-radius: 8px;
}

.blog-cover {
  width: 100px;
  height: 100px;
  border-radius: 8px;
}

.item-info {
  flex: 1;
}

.item-name {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}

.item-name:hover {
  color: #1989fa;
}

.item-desc {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 14px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #999;
  margin-bottom: 10px;
}

.item-tags {
  display: flex;
  gap: 5px;
}

.item-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 10px;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.image-item {
  overflow: hidden;
}

.image-thumbnail {
  width: 100%;
  height: 150px;
  cursor: pointer;
}

.image-info {
  padding: 10px;
}

.image-name {
  margin: 0 0 5px 0;
  font-size: 14px;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-meta {
  margin: 0;
  font-size: 12px;
  color: #999;
}

.image-actions {
  display: flex;
  justify-content: flex-end;
  gap: 5px;
  padding: 0 10px 10px;
}

.empty-result {
  margin-top: 50px;
  text-align: center;
  padding: 50px 0;
}

.pagination {
  text-align: center;
  margin-top: 30px;
}
</style>
