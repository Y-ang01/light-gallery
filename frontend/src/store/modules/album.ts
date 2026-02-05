import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  createAlbum,
  getAlbumList,
  getAlbumDetail,
  updateAlbum,
  deleteAlbum,
  restoreAlbum,
  getRecycleAlbums,
  verifyAlbumPassword,
} from '@/api/album'

// 图片集类型
export interface Album {
  id: string
  name: string
  description: string
  user_id: string
  permission: 'PUBLIC' | 'PROTECTED' | 'PRIVATE'
  password_hash?: string
  cover_image_id?: string
  image_count: number
  is_deleted: boolean
  created_at: string
  updated_at: string
}

// 分页结果类型
export interface PaginationResult<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export const useAlbumStore = defineStore('album', () => {
  // 状态
  const albumList = ref<Album[]>([])
  const currentAlbum = ref<Album | null>(null)
  const recycleAlbumList = ref<Album[]>([])
  const total = ref<number>(0)
  const totalPages = ref<number>(0)
  const isLoading = ref<boolean>(false)

  // 方法
  // 获取图片集列表
  const fetchAlbumList = async (page = 1, pageSize = 10, permission?: string) => {
    try {
      isLoading.value = true
      const response = await getAlbumList(page, pageSize, permission)

      if (response.code === 200) {
        albumList.value = response.data.items
        total.value = response.data.total
        totalPages.value = response.data.total_pages
        return true
      }
      return false
    } catch (error) {
      console.error('获取图片集列表失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 创建图片集
  const createAlbumAction = async (
    name: string,
    description?: string,
    permission: string = 'PUBLIC',
    password?: string,
  ) => {
    try {
      isLoading.value = true
      const response = await createAlbum(name, description, permission, password)

      if (response.code === 200) {
        // 重新获取列表
        await fetchAlbumList()
        return true
      }
      return false
    } catch (error) {
      console.error('创建图片集失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 获取图片集详情
  const fetchAlbumDetail = async (albumId: string, password?: string) => {
    try {
      isLoading.value = true
      const response = await getAlbumDetail(albumId, password)

      if (response.code === 200) {
        currentAlbum.value = response.data
        return true
      }
      return false
    } catch (error) {
      console.error('获取图片集详情失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 更新图片集
  const updateAlbumAction = async (
    albumId: string,
    data: Partial<{
      name: string
      description: string
      permission: string
      password: string
      cover_image_id: string
    }>,
  ) => {
    try {
      isLoading.value = true
      const response = await updateAlbum(albumId, data)

      if (response.code === 200) {
        currentAlbum.value = response.data
        await fetchAlbumList()
        return true
      }
      return false
    } catch (error) {
      console.error('更新图片集失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 删除图片集
  const deleteAlbumAction = async (albumId: string) => {
    try {
      isLoading.value = true
      const response = await deleteAlbum(albumId)

      if (response.code === 200) {
        await fetchAlbumList()
        return true
      }
      return false
    } catch (error) {
      console.error('删除图片集失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 获取回收站图片集
  const fetchRecycleAlbums = async (page = 1, pageSize = 10) => {
    try {
      isLoading.value = true
      const response = await getRecycleAlbums(page, pageSize)

      if (response.code === 200) {
        recycleAlbumList.value = response.data.items
        total.value = response.data.total
        totalPages.value = response.data.total_pages
        return true
      }
      return false
    } catch (error) {
      console.error('获取回收站图片集失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 恢复图片集
  const restoreAlbumAction = async (albumId: string) => {
    try {
      isLoading.value = true
      const response = await restoreAlbum(albumId)

      if (response.code === 200) {
        await fetchRecycleAlbums()
        return true
      }
      return false
    } catch (error) {
      console.error('恢复图片集失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 验证图片集密码
  const verifyAlbumPwd = async (albumId: string, password: string) => {
    try {
      const response = await verifyAlbumPassword(albumId, password)
      return response.code === 200
    } catch (error) {
      console.error('验证图片集密码失败:', error)
      return false
    }
  }

  return {
    albumList,
    currentAlbum,
    recycleAlbumList,
    total,
    totalPages,
    isLoading,
    fetchAlbumList,
    createAlbumAction,
    fetchAlbumDetail,
    updateAlbumAction,
    deleteAlbumAction,
    fetchRecycleAlbums,
    restoreAlbumAction,
    verifyAlbumPwd,
  }
})
