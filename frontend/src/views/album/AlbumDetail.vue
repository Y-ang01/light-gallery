<script setup lang="ts">
// （接上文）获取图片集详情
const fetchAlbumDetail = async () => {
  try {
    isLoading.value = true

    // 尝试获取图片集详情（无密码）
    const success = await albumStore.fetchAlbumDetail(albumId.value)

    if (success) {
      const album = albumStore.currentAlbum
      if (!album) return

      // 检查是否为所有者
      isOwner.value = album.user_id === userStore.userInfo.id

      // 检查是否需要密码
      if (album.permission === 'PROTECTED' && !isOwner.value) {
        isPasswordProtected.value = true
        passwordDialogVisible.value = true
      } else {
        isPasswordProtected.value = false
        // 获取图片列表
        await fetchAlbumImages()
      }
    } else {
      ElMessage.error('获取图片集详情失败')
      router.back()
    }
  } catch (error) {
    console.error('获取图片集详情失败:', error)
    ElMessage.error('获取图片集详情失败')
    router.back()
  } finally {
    isLoading.value = false
  }
}

// 获取图片列表
const fetchAlbumImages = async (page = 1, pageSize = 20) => {
  try {
    isLoading.value = true
    await imageStore.fetchAlbumImages(albumId.value, page, pageSize)
  } catch (error) {
    console.error('获取图片列表失败:', error)
    ElMessage.error('获取图片列表失败')
  } finally {
    isLoading.value = false
  }
}

// 验证图片集密码
const handleVerifyPassword = async () => {
  try {
    await passwordFormRef.value?.validate()
    const success = await albumStore.verifyAlbumPwd(albumId.value, passwordForm.value.password)

    if (success) {
      passwordDialogVisible.value = false
      isPasswordProtected.value = false
      await fetchAlbumImages()
    } else {
      ElMessage.error('密码错误，请重试')
    }
  } catch (error) {
    console.error('密码验证失败:', error)
    ElMessage.error('密码验证失败')
  }
}

// 打开上传弹窗
const openUploadDialog = () => {
  uploadFileList.value = []
  uploadProgress.value = 0
  uploadDialogVisible.value = true
}

// 文件上传前校验
const beforeUpload = (file: File) => {
  const fileSize = file.size
  const fileType = file.type || file.name.split('.').pop() || ''

  // 校验文件类型
  const supportTypes = ['image/jpeg', 'image/png', 'image/raw', 'raw', 'cr2', 'nef', 'arw']
  const isSupportType = supportTypes.some(type =>
    fileType.toLowerCase().includes(type) || file.name.toLowerCase().endsWith(`.${type}`)
  )

  if (!isSupportType) {
    ElMessage.error('不支持的文件类型，仅支持JPG、PNG、RAW格式')
    return false
  }

  // 校验文件大小
  const isJpg = fileType.includes('jpeg') || fileType.includes('jpg') || file.name.toLowerCase().endsWith('.jpg') || file.name.toLowerCase().endsWith('.jpeg')
  const isRaw = fileType.includes('raw') || file.name.toLowerCase().endsWith('.raw') || file.name.toLowerCase().endsWith('.cr2') || file.name.toLowerCase().endsWith('.nef') || file.name.toLowerCase().endsWith('.arw')

  if (isJpg && fileSize > 50 * 1024 * 1024) {
    ElMessage.error('JPG文件最大支持50MB')
    return false
  }

  if (isRaw && fileSize > 200 * 1024 * 1024) {
    ElMessage.error('RAW文件最大支持200MB')
    return false
  }

  return true
}

// 处理文件选择
const handleFileChange = (uploadFile: any, list: any[]) => {
  uploadFileList.value = list
}

// 处理上传
const handleUpload = async () => {
  try {
    isUploading.value = true
    const files = uploadFileList.value.map(item => item.raw)

    const success = await imageStore.uploadImagesAction(albumId.value, files)

    if (success) {
      ElMessage.success('图片上传成功')
      uploadDialogVisible.value = false
      await fetchAlbumImages()
      // 更新图片集信息
      await albumStore.fetchAlbumDetail(albumId.value)
    } else {
      ElMessage.error('图片上传失败')
    }
  } catch (error) {
    console.error('上传图片失败:', error)
    ElMessage.error('图片上传失败')
  } finally {
    isUploading.value = false
    uploadProgress.value = 0
  }
}

// 切换排序模式
const toggleSortMode = () => {
  isSortMode.value = !isSortMode.value
  if (!isSortMode.value && selectedImageIds.value.length > 0) {
    selectedImageIds.value = []
  }
}

// 处理图片选择
const handleImageSelect = () => {
  // 空处理，仅用于触发响应式更新
}

// 拖拽排序相关
const handleDragStart = (id: string) => {
  dragSourceId.value = id
}

const handleDrop = (targetId: string) => {
  if (dragSourceId.value === targetId) return

  // 重新排序
  const newImageList = [...imageList.value]
  const sourceIndex = newImageList.findIndex(item => item.id === dragSourceId.value)
  const targetIndex = newImageList.findIndex(item => item.id === targetId)

  if (sourceIndex !== -1 && targetIndex !== -1) {
    const [dragged] = newImageList.splice(sourceIndex, 1)
    newImageList.splice(targetIndex, 0, dragged)

    // 获取排序后的ID列表
    const imageIds = newImageList.map(item => item.id)
    imageStore.updateImageSortAction(imageIds)
  }
}

// 处理图片点击（预览）
const handleImageClick = (imageId: string) => {
  if (isSortMode.value) return

  const image = imageList.value.find(item => item.id === imageId)
  if (image) {
    ElImagePreview({
      urlList: [image.file_path],
      initialIndex: 0,
      zIndex: 3000
    })
  }
}

// 处理图片下载
const handleDownload = async (imageId: string) => {
  try {
    const image = imageList.value.find(item => item.id === imageId)
    if (!image) {
      ElMessage.error('图片不存在')
      return
    }

    // 创建下载链接
    const link = document.createElement('a')
    link.href = image.file_path
    link.download = image.filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    ElMessage.success('下载已开始')
  } catch (error) {
    console.error('下载图片失败:', error)
    ElMessage.error('下载图片失败')
  }
}

// 处理图片删除
const handleDelete = async (imageId: string) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除该图片吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const success = await imageStore.deleteImageAction(imageId)
    if (success) {
      ElMessage.success('图片删除成功')
      await fetchAlbumImages(currentPage.value, pageSize.value)
      // 更新图片集信息
      await albumStore.fetchAlbumDetail(albumId.value)
    } else {
      ElMessage.error('图片删除失败')
    }
  } catch (error) {
    // 取消删除
  }
}

// 处理批量删除
const handleBatchDelete = async () => {
  try {
    if (selectedImageIds.value.length === 0) {
      ElMessage.warning('请选择要删除的图片')
      return
    }

    await ElMessageBox.confirm(
      `确定要删除选中的${selectedImageIds.value.length}张图片吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const success = await imageStore.batchDeleteImagesAction(selectedImageIds.value)
    if (success) {
      ElMessage.success('图片删除成功')
      selectedImageIds.value = []
      isSortMode.value = false
      await fetchAlbumImages(currentPage.value, pageSize.value)
      // 更新图片集信息
      await albumStore.fetchAlbumDetail(albumId.value)
    } else {
      ElMessage.error('图片删除失败')
    }
  } catch (error) {
    // 取消删除
  }
}

// 处理分页大小变化
const handleSizeChange = (size: number) => {
  fetchAlbumImages(1, size)
}

// 处理页码变化
const handleCurrentChange = (page: number) => {
  fetchAlbumImages(page, pageSize.value)
}

// 前往编辑图片集
const goToEditAlbum = () => {
  ElMessage.info('编辑图片集功能开发中')
  // 实际项目中应跳转到编辑页面
  // router.push(`/albums/${albumId.value}/edit`)
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 获取权限文本
const getPermissionText = (permission: string) => {
  switch (permission) {
    case 'PUBLIC':
      return '公开（所有人可见）'
    case 'PROTECTED':
      return '密码保护（输入密码可见）'
    case 'PRIVATE':
      return '私密（仅自己可见）'
    default:
      return '未知权限'
  }
}

// 监听上传进度
watch(
  () => imageStore.uploadProgress,
  (progress) => {
    uploadProgress.value = progress
  }
)
</script>

<style scoped lang="scss">
.album-detail-container {
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

.header-info {
  flex: 1;
  min-width: 300px;
}

.album-title {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 20px;
  font-weight: 600;
}

.album-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 14px;
  color: #666;
}

.album-permission,
.album-count,
.album-time {
  display: flex;
  align-items: center;
  gap: 6px;
}

.permission-icon,
.count-icon {
  font-size: 16px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.image-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.toolbar-left {
  display: flex;
  gap: 16px;
}

.toolbar-right {
  display: flex;
  gap: 16px;
}

.view-mode-select {
  width: 140px;
}

.el-button.active {
  color: #1989fa !important;
  font-weight: 600;
}

// 网格视图
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.image-item {
  position: relative;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s;
  cursor: pointer;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
  }
}

.image-checkbox {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 10;
}

.image-thumbnail {
  width: 100%;
  height: 150px;
}

.image-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 150px;
  background-color: #f5f7fa;
}

.placeholder-icon {
  font-size: 48px;
  color: #ccc;
}

.image-info {
  padding: 12px;
}

.image-name {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #2c3e50;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-size {
  margin: 0;
  font-size: 12px;
  color: #999;
}

.image-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s;
  z-index: 10;
}

.image-item:hover .image-actions {
  opacity: 1;
}

// 列表视图
.image-table {
  width: 100%;
  margin-bottom: 30px;
}

.table-image {
  width: 80px;
  height: 60px;
  border-radius: 4px;
}

// 瀑布流视图
.image-waterfall {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.waterfall-item {
  position: relative;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s;
  cursor: pointer;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
  }
}

.waterfall-image {
  width: 100%;
  height: auto;
}

.waterfall-info {
  padding: 12px;
}

.image-meta {
  margin: 0;
  font-size: 12px;
  color: #999;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.empty-images {
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

// 上传弹窗样式
.upload-progress {
  margin-top: 16px;
}

.progress-text {
  margin: 8px 0 0 0;
  text-align: center;
  font-size: 14px;
  color: #666;
}

// 响应式适配
@media (max-width: 768px) {
  .image-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  }

  .image-waterfall {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  }

  .album-meta {
    gap: 8px;
  }

  .header-actions {
    margin-top: 10px;
  }
}
</style>
