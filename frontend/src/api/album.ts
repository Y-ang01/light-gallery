import { request } from '@/utils/request'

// 创建图片集
export const createAlbum = (
  name: string,
  description?: string,
  permission = 'PUBLIC',
  password?: string,
) => {
  return request.post('/albums', {
    name,
    description,
    permission,
    password,
  })
}

// 获取图片集列表
export const getAlbumList = (page = 1, pageSize = 10, permission?: string) => {
  return request.get('/albums', {
    params: {
      page,
      page_size: pageSize,
      permission,
    },
  })
}

// 获取图片集详情
export const getAlbumDetail = (albumId: string, password?: string) => {
  return request.get(`/albums/${albumId}`, {
    params: {
      password,
    },
  })
}

// 更新图片集
export const updateAlbum = (
  albumId: string,
  data: {
    name?: string
    description?: string
    permission?: string
    password?: string
    cover_image_id?: string
  },
) => {
  return request.put(`/albums/${albumId}`, data)
}

// 删除图片集
export const deleteAlbum = (albumId: string) => {
  return request.delete(`/albums/${albumId}`)
}

// 验证图片集密码
export const verifyAlbumPassword = (albumId: string, password: string) => {
  return request.post(`/albums/${albumId}/verify-password`, {
    password,
  })
}

// 设置图片集密码
export const setAlbumPassword = (albumId: string, password: string) => {
  return request.post(`/albums/${albumId}/password`, {
    password,
  })
}

// 获取回收站图片集
export const getRecycleAlbums = (page = 1, pageSize = 10) => {
  return request.get('/albums/recycle', {
    params: {
      page,
      page_size: pageSize,
    },
  })
}

// 恢复图片集
export const restoreAlbum = (albumId: string) => {
  return request.post(`/albums/${albumId}/restore`)
}
