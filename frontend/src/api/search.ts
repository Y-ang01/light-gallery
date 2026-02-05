import { request } from '@/utils/request'

// 全文搜索
export const fullTextSearch = (keyword: string, type?: string, page = 1, pageSize = 10) => {
  return request.get('/search/full-text', {
    params: {
      keyword,
      type,
      page,
      page_size: pageSize,
    },
  })
}

// 高级搜索
export const advancedSearch = (params: {
  keyword?: string
  type?: string
  start_time?: string
  end_time?: string
  permission?: string
  file_type?: string[]
  exif_camera?: string
  tags?: string[]
  page?: number
  page_size?: number
  sort?: string
  order?: string
}) => {
  return request.get('/search/advanced', {
    params: {
      page: 1,
      page_size: 10,
      sort: 'created_at',
      order: 'desc',
      ...params,
    },
  })
}

// 筛选图片集
export const filterAlbums = (params: {
  permission?: string
  create_time?: string
  image_count_min?: number
  image_count_max?: number
  page?: number
  page_size?: number
}) => {
  return request.get('/search/filter/albums', {
    params: {
      page: 1,
      page_size: 10,
      ...params,
    },
  })
}

// 筛选图片
export const filterImages = (params: {
  album_id?: string
  file_type?: string[]
  size_min?: number
  size_max?: number
  exif_camera?: string
  exif_iso?: number[]
  page?: number
  page_size?: number
}) => {
  return request.get('/search/filter/images', {
    params: {
      page: 1,
      page_size: 10,
      ...params,
    },
  })
}
