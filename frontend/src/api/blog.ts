import { request } from '@/utils/request'

// 创建博客
export const createBlogPost = (
  title: string,
  content: string,
  isDraft = false,
  isPrivate = false,
  coverImageUrl?: string,
  tags: string[] = [],
) => {
  return request.post('/blog/posts', {
    title,
    content,
    is_draft: isDraft,
    is_private: isPrivate,
    cover_image_url: coverImageUrl,
    tags,
  })
}

// 获取博客列表
export const getBlogList = (
  page = 1,
  pageSize = 10,
  keyword?: string,
  sort = 'created_at',
  order = 'desc',
  isPrivate?: boolean,
  isDraft = false,
) => {
  return request.get('/blog/posts', {
    params: {
      page,
      page_size: pageSize,
      keyword,
      sort,
      order,
      is_private: isPrivate,
      is_draft: isDraft,
    },
  })
}

// 获取博客详情
export const getBlogDetail = (blogId: string) => {
  return request.get(`/blog/posts/${blogId}`)
}

// 更新博客
export const updateBlogPost = (
  blogId: string,
  data: {
    title?: string
    content?: string
    is_draft?: boolean
    is_private?: boolean
    cover_image_url?: string
    tags?: string[]
  },
) => {
  return request.put(`/blog/posts/${blogId}`, data)
}

// 删除博客
export const deleteBlogPost = (blogId: string) => {
  return request.delete(`/blog/posts/${blogId}`)
}

// 获取博客评论
export const getBlogComments = (blogId: string, page = 1, pageSize = 20) => {
  return request.get(`/blog/posts/${blogId}/comments`, {
    params: {
      page,
      page_size: pageSize,
    },
  })
}

// 创建评论
export const createComment = (blogId: string, content: string, parentId?: string) => {
  return request.post(`/blog/posts/${blogId}/comments`, {
    content,
    parent_id: parentId,
  })
}

// 删除评论
export const deleteComment = (commentId: string) => {
  return request.delete(`/blog/comments/${commentId}`)
}

// 上传博客附件
export const uploadBlogAttachment = (
  formData: FormData,
  onProgress?: (progress: number) => void,
) => {
  return request.post('/blog/upload-attachment', formData, {
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
