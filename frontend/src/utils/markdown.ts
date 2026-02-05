import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

// 初始化markdown解析器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: (str, lang) => {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return `<pre class="hljs"><code>${hljs.highlight(str, { language: lang, ignoreIllegals: true }).value}</code></pre>`
      } catch (__) {
        // 忽略高亮错误
      }
    }

    return `<pre class="hljs"><code>${md.utils.escapeHtml(str)}</code></pre>`
  },
})

// 自定义渲染规则
// 图片渲染优化
const defaultImageRender =
  md.renderer.rules.image ||
  function (tokens, idx, options, env, self) {
    return self.renderToken(tokens, idx, options)
  }

md.renderer.rules.image = function (tokens, idx, options, env, self) {
  const token = tokens[idx]
  const srcIndex = token.attrIndex('src')
  const alt = token.content

  // 添加图片样式类
  token.attrPush(['class', 'markdown-image'])
  // 添加alt属性
  token.attrPush(['alt', alt])
  // 添加loading属性
  token.attrPush(['loading', 'lazy'])

  return defaultImageRender(tokens, idx, options, env, self)
}

// 链接渲染优化
const defaultLinkRender =
  md.renderer.rules.link_open ||
  function (tokens, idx, options, env, self) {
    return self.renderToken(tokens, idx, options)
  }

md.renderer.rules.link_open = function (tokens, idx, options, env, self) {
  const token = tokens[idx]

  // 添加链接样式类
  token.attrPush(['class', 'markdown-link'])
  // 外部链接新窗口打开
  const hrefIndex = token.attrIndex('href')
  if (hrefIndex >= 0) {
    const href = token.attrs![hrefIndex][1]
    if (href && !href.startsWith('/') && !href.startsWith('#')) {
      token.attrPush(['target', '_blank'])
      token.attrPush(['rel', 'noopener noreferrer'])
    }
  }

  return defaultLinkRender(tokens, idx, options, env, self)
}

/**
 * 解析markdown内容
 * @param content markdown内容
 * @returns HTML字符串
 */
export const renderMarkdown = (content: string): string => {
  if (!content) return ''
  return md.render(content)
}

/**
 * 解析markdown内容为纯文本
 * @param content markdown内容
 * @returns 纯文本
 */
export const markdownToText = (content: string): string => {
  if (!content) return ''

  // 先渲染为HTML，再去除标签
  const html = md.render(content)
  const text = html
    .replace(/<[^>]*>/g, '') // 去除所有HTML标签
    .replace(/&nbsp;/g, ' ') // 替换空格
    .replace(/&gt;/g, '>')
    .replace(/&lt;/g, '<')
    .replace(/&amp;/g, '&')
    .trim()

  return text
}

/**
 * 获取markdown内容的摘要
 * @param content markdown内容
 * @param length 摘要长度
 * @returns 摘要文本
 */
export const getMarkdownSummary = (content: string, length = 150): string => {
  const text = markdownToText(content)

  if (text.length <= length) {
    return text
  }

  return text.substring(0, length) + '...'
}

export default md
