import { request } from '@/utils/request'

// 上传图片
export const uploadImages = (
  albumId: string,
  formData: FormData,
  onProgress?: (progress: number) => void,
) => {
  return request.post(`/upload/images/${albumId}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total) {
        const percent = (progressEvent.loaded / progressEvent.total) * 100
        onProgress?.(percent)
      }
    },
  })
}

// 上传博客图片
export const uploadBlogImage = (formData: FormData, onProgress?: (progress: number) => void) => {
  return request.post('/upload/blog-image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total) {
        const percent = (progressEvent.loaded / progressEvent.total) * 100
        onProgress?.(percent)
      }
    },
  })
}

// 获取图片集图片列表
export const getAlbumImages = (albumId: string, page = 1, pageSize = 20) => {
  return request.get(`/images/album/${albumId}`, {
    params: {
      page,
      page_size: pageSize,
    },
  })
}

// 获取图片详情
export const getImageDetail = (imageId: string) => {
  return request.get(`/images/${imageId}`)
}

// 获取图片EXIF信息
export const getImageExif = (imageId: string) => {
  return request.get(`/images/${imageId}/exif`)
}

// 下载图片
export const downloadImage = (imageId: string) => {
  return request.get(`/images/${imageId}/download`, {
    responseType: 'blob',
  })
}

// 批量下载图片
export const batchDownloadImages = (imageIds: string[]) => {
  return request.post('/images/batch-download', {
    image_ids: imageIds,
  })
}

// 更新图片排序
export const updateImageSort = (imageIds: string[]) => {
  return request.put('/images/sort', {
    image_ids: imageIds,
  })
}

// 删除图片
export const deleteImage = (imageId: string) => {
  return request.delete(`/images/${imageId}`)
}

// 批量删除图片
export const batchDeleteImages = (imageIds: string[]) => {
  return request.post('/images/batch-delete', {
    image_ids: imageIds,
  })
}
