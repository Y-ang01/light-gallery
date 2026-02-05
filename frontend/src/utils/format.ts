/**
 * 格式化日期时间
 * @param date 日期
 * @param format 格式
 * @returns 格式化后的日期字符串
 */
export const formatDateTime = (
  date: Date | string | number,
  format = 'YYYY-MM-DD HH:mm:ss',
): string => {
  if (!date) return ''

  const d = new Date(date)

  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', year.toString())
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 格式化文件大小
 * @param bytes 字节数
 * @returns 格式化后的文件大小字符串
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes < 0) return '0 B'

  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let unitIndex = 0
  let size = bytes

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }

  return `${size.toFixed(2)} ${units[unitIndex]}`
}

/**
 * 防抖函数
 * @param func 执行函数
 * @param delay 延迟时间
 * @returns 防抖函数
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay = 300,
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout

  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => {
      func(...args)
    }, delay)
  }
}

/**
 * 节流函数
 * @param func 执行函数
 * @param interval 间隔时间
 * @returns 节流函数
 */
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  interval = 300,
): ((...args: Parameters<T>) => void) => {
  let lastTime = 0

  return (...args: Parameters<T>) => {
    const now = Date.now()

    if (now - lastTime >= interval) {
      func(...args)
      lastTime = now
    }
  }
}

/**
 * 深拷贝
 * @param obj 要拷贝的对象
 * @returns 拷贝后的对象
 */
export const deepClone = <T>(obj: T): T => {
  if (obj === null || typeof obj !== 'object') {
    return obj
  }

  if (obj instanceof Date) {
    return new Date(obj.getTime()) as unknown as T
  }

  if (obj instanceof Array) {
    return obj.map((item) => deepClone(item)) as unknown as T
  }

  if (obj instanceof Object) {
    const clonedObj = {} as { [key: string]: any }

    Object.keys(obj).forEach((key) => {
      clonedObj[key] = deepClone((obj as { [key: string]: any })[key])
    })

    return clonedObj as T
  }

  return obj
}

/**
 * 生成随机字符串
 * @param length 长度
 * @returns 随机字符串
 */
export const randomString = (length = 8): string => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''

  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }

  return result
}
