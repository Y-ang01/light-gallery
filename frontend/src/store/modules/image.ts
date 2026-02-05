import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  uploadImages,
  getAlbumImages,
  getImageDetail,
  updateImageSort,
  deleteImage,
  batchDeleteImages,
  getImageExif,
} from '@/api/image'

// 图片类型
export interface Image {
  id: string
  filename: string
  file_path: string
  thumbnail_path: string
  file_type: string
  file_size: number
  album_id: string
  user_id: string
  exif_data: Record<string, any>
  sort_order: number
  is_deleted: boolean
  created_at: string
  updated_at: string
}

export const useImageStore = defineStore('image', () => {
  // 状态
  const imageList = ref<Image[]>([])
  const currentImage = ref<Image | null>(null)
  const exifData = ref<Record<string, any>>({})
  const total = ref<number>(0)
  const totalPages = ref<number>(0)
  const uploadProgress = ref<number>(0)
  const isLoading = ref<boolean>(false)

  // 方法
  // 上传图片
  const uploadImagesAction = async (albumId: string, files: File[]) => {
    try {
      isLoading.value = true
      const formData = new FormData()

      files.forEach((file) => {
        formData.append('files', file)
      })

      const response = await uploadImages(albumId, formData, (progress) => {
        uploadProgress.value = progress
      })

      if (response.code === 200) {
        // 重新获取图片列表
        await fetchAlbumImages(albumId)
        return true
      }
      return false
    } catch (error) {
      console.error('上传图片失败:', error)
      return false
    } finally {
      isLoading.value = false
      uploadProgress.value = 0
    }
  }

  // 获取图片集图片列表
  const fetchAlbumImages = async (albumId: string, page = 1, pageSize = 20) => {
    try {
      isLoading.value = true
      const response = await getAlbumImages(albumId, page, pageSize)

      if (response.code === 200) {
        imageList.value = response.data.items
        total.value = response.data.total
        totalPages.value = response.data.total_pages
        return true
      }
      return false
    } catch (error) {
      console.error('获取图片列表失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 获取图片详情
  const fetchImageDetail = async (imageId: string) => {
    try {
      isLoading.value = true
      const response = await getImageDetail(imageId)

      if (response.code === 200) {
        currentImage.value = response.data
        // 获取EXIF信息
        await fetchImageExif(imageId)
        return true
      }
      return false
    } catch (error) {
      console.error('获取图片详情失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 获取图片EXIF信息
  const fetchImageExif = async (imageId: string) => {
    try {
      const response = await getImageExif(imageId)

      if (response.code === 200) {
        exifData.value = response.data
        return true
      }
      return false
    } catch (error) {
      console.error('获取EXIF信息失败:', error)
      return false
    }
  }

  // 更新图片排序
  const updateImageSortAction = async (imageIds: string[]) => {
    try {
      isLoading.value = true
      const response = await updateImageSort(imageIds)

      if (response.code === 200) {
        // 重新获取图片列表
        if (imageList.value.length > 0) {
          await fetchAlbumImages(imageList.value[0].album_id)
        }
        return true
      }
      return false
    } catch (error) {
      console.error('更新图片排序失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 删除图片
  const deleteImageAction = async (imageId: string) => {
    try {
      isLoading.value = true
      const response = await deleteImage(imageId)

      if (response.code === 200) {
        // 重新获取图片列表
        if (currentImage.value) {
          await fetchAlbumImages(currentImage.value.album_id)
        }
        return true
      }
      return false
    } catch (error) {
      console.error('删除图片失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 批量删除图片
  const batchDeleteImagesAction = async (imageIds: string[]) => {
    try {
      isLoading.value = true
      const response = await batchDeleteImages(imageIds)

      if (response.code === 200) {
        // 重新获取图片列表
        if (imageList.value.length > 0) {
          await fetchAlbumImages(imageList.value[0].album_id)
        }
        return true
      }
      return false
    } catch (error) {
      console.error('批量删除图片失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  return {
    imageList,
    currentImage,
    exifData,
    total,
    totalPages,
    uploadProgress,
    isLoading,
    uploadImagesAction,
    fetchAlbumImages,
    fetchImageDetail,
    fetchImageExif,
    updateImageSortAction,
    deleteImageAction,
    batchDeleteImagesAction,
  }
})
