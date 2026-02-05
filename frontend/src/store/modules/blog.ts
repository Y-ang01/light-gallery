import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  createBlogPost,
  getBlogList,
  getBlogDetail,
  updateBlogPost,
  deleteBlogPost,
  createComment,
  getBlogComments,
  deleteComment,
  uploadBlogAttachment,
} from '@/api/blog'

// 博客类型
export interface BlogPost {
  id: string
  title: string
  content: string
  user_id: string
  cover_image_url?: string
  is_draft: boolean
  is_private: boolean
  tags: string[]
  view_count: number
  comment_count: number
  created_at: string
  updated_at: string
  author_username?: string
}

// 评论类型
export interface Comment {
  id: string
  content: string
  post_id: string
  user_id: string
  parent_id?: string
  created_at: string
  updated_at: string
  author_username?: string
  replies?: Comment[]
}

export const useBlogStore = defineStore('blog', () => {
  // 状态
  const blogList = ref<BlogPost[]>([])
  const currentBlog = ref<BlogPost | null>(null)
  const commentList = ref<Comment[]>([])
  const draftList = ref<BlogPost[]>([])
  const total = ref<number>(0)
  const totalPages = ref<number>(0)
  const commentTotal = ref<number>(0)
  const isLoading = ref<boolean>(false)

  // 方法
  // 创建博客
  const createBlogPostAction = async (
    title: string,
    content: string,
    isDraft = false,
    isPrivate = false,
    coverImageUrl?: string,
    tags: string[] = [],
  ) => {
    try {
      isLoading.value = true
      const response = await createBlogPost(title, content, isDraft, isPrivate, coverImageUrl, tags)

      if (response.code === 200) {
        await fetchBlogList()
        if (isDraft) {
          await fetchDraftList()
        }
        return true
      }
      return false
    } catch (error) {
      console.error('创建博客失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 获取博客列表
  const fetchBlogList = async (
    page = 1,
    pageSize = 10,
    keyword?: string,
    sort = 'created_at',
    order = 'desc',
    isPrivate?: boolean,
  ) => {
    try {
      isLoading.value = true
      const response = await getBlogList(page, pageSize, keyword, sort, order, isPrivate)

      if (response.code === 200) {
        blogList.value = response.data.items
        total.value = response.data.total
        totalPages.value = response.data.total_pages
        return true
      }
      return false
    } catch (error) {
      console.error('获取博客列表失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 获取草稿箱
  const fetchDraftList = async (page = 1, pageSize = 10) => {
    try {
      isLoading.value = true
      const response = await getBlogList(
        page,
        pageSize,
        undefined,
        'created_at',
        'desc',
        undefined,
        true,
      )

      if (response.code === 200) {
        draftList.value = response.data.items
        total.value = response.data.total
        totalPages.value = response.data.total_pages
        return true
      }
      return false
    } catch (error) {
      console.error('获取草稿箱失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 获取博客详情
  const fetchBlogDetail = async (blogId: string) => {
    try {
      isLoading.value = true
      const response = await getBlogDetail(blogId)

      if (response.code === 200) {
        currentBlog.value = response.data
        // 获取评论
        await fetchBlogComments(blogId)
        return true
      }
      return false
    } catch (error) {
      console.error('获取博客详情失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 更新博客
  const updateBlogPostAction = async (
    blogId: string,
    data: Partial<{
      title: string
      content: string
      is_draft: boolean
      is_private: boolean
      cover_image_url: string
      tags: string[]
    }>,
  ) => {
    try {
      isLoading.value = true
      const response = await updateBlogPost(blogId, data)

      if (response.code === 200) {
        currentBlog.value = response.data
        await fetchBlogList()
        if (data.is_draft) {
          await fetchDraftList()
        }
        return true
      }
      return false
    } catch (error) {
      console.error('更新博客失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 删除博客
  const deleteBlogPostAction = async (blogId: string) => {
    try {
      isLoading.value = true
      const response = await deleteBlogPost(blogId)

      if (response.code === 200) {
        await fetchBlogList()
        await fetchDraftList()
        return true
      }
      return false
    } catch (error) {
      console.error('删除博客失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 获取博客评论
  const fetchBlogComments = async (blogId: string, page = 1, pageSize = 20) => {
    try {
      isLoading.value = true
      const response = await getBlogComments(blogId, page, pageSize)

      if (response.code === 200) {
        commentList.value = response.data.items
        commentTotal.value = response.data.total
        return true
      }
      return false
    } catch (error) {
      console.error('获取评论失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 创建评论
  const createCommentAction = async (blogId: string, content: string, parentId?: string) => {
    try {
      isLoading.value = true
      const response = await createComment(blogId, content, parentId)

      if (response.code === 200) {
        await fetchBlogComments(blogId)
        return true
      }
      return false
    } catch (error) {
      console.error('创建评论失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 删除评论
  const deleteCommentAction = async (commentId: string) => {
    try {
      isLoading.value = true
      const response = await deleteComment(commentId)

      if (response.code === 200) {
        if (currentBlog.value) {
          await fetchBlogComments(currentBlog.value.id)
        }
        return true
      }
      return false
    } catch (error) {
      console.error('删除评论失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 上传博客附件
  const uploadBlogAttachmentAction = async (file: File) => {
    try {
      isLoading.value = true
      const formData = new FormData()
      formData.append('file', file)

      const response = await uploadBlogAttachment(formData)

      if (response.code === 200) {
        return response.data.url
      }
      return ''
    } catch (error) {
      console.error('上传附件失败:', error)
      return ''
    } finally {
      isLoading.value = false
    }
  }

  return {
    blogList,
    currentBlog,
    commentList,
    draftList,
    total,
    totalPages,
    commentTotal,
    isLoading,
    createBlogPostAction,
    fetchBlogList,
    fetchDraftList,
    fetchBlogDetail,
    updateBlogPostAction,
    deleteBlogPostAction,
    fetchBlogComments,
    createCommentAction,
    deleteCommentAction,
    uploadBlogAttachmentAction,
  }
})
