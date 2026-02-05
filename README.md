# 光影收藏夹- 专业图片集管理展示平台
 
## 项目概述 
 
这是一个专业的图片集管理和展示平台，支持RAW格式存储和博客功能?
 
## 技术栈 
 
- **前端**: Vue 3 + TypeScript + Element Plus 
- **后端**: FastAPI + Python 3.14.2
- **数据库*: PostgreSQL 16
- **缓存**: Redis 7
- **部署**: Docker + Nginx 


## 快速构建
- **后端**
- python 3.14.2
- postgresql 16
- redis 7
- docker-compose up -d
- cd backend
- pip install -r requirements.txt
- **前端**
- npm install
- npm run build
- npm run dev
- 注意修改start-dev中环境名称conda activate private-website

## 快速启动
- start-dev.bat  启动开发环境



backend/
├── app/
│   ├── __init__.py                # 包初始化
│   ├── core/                      # 核心配置
│   │   ├── __init__.py
│   │   ├── db.py                  # 数据库连接（PostgreSQL+Redis）+ Base类
│   │   └── dependencies.py        # 权限依赖（JWT认证+角色校验）
│   ├── models/                    # 数据库模型（ORM）
│   │   ├── __init__.py
│   │   ├── user.py                # 用户表模型（users）
│   │   ├── album.py               # 图片集表模型（albums）
│   │   ├── image.py               # 图片表模型（images）
│   │   ├── blog.py                # 博客/评论表模型（blog_posts/comments）
│   ├── services/                  # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── user_service.py        # 用户相关业务（注册/权限/资料管理）
│   │   ├── album_service.py       # 图片集业务（创建/管理/配额校验）
│   │   ├── image_service.py       # 图片业务（上传/处理/EXIF提取）
│   │   ├── blog_service.py        # 博客业务（发布/编辑/评论管理）
│   │   └── search_service.py      # 搜索业务（全文/高级筛选）
│   ├── api/                       # API接口层（v1版本）
│   │   ├── __init__.py
│   │   ├── auth_api.py            # 用户认证接口（注册/登录/个人信息）
│   │   ├── album_api.py           # 图片集接口（CRUD/密码保护）
│   │   ├── image_api.py           # 图片接口（上传/排序/删除）
│   │   ├── blog_api.py            # 博客接口（发布/评论/附件）
│   │   ├── search_api.py          # 搜索接口（全文/高级筛选）
│   │   └── admin_api.py           # 管理员接口（用户管理/系统统计）
│   └── utils/                     # 工具函数
│       ├── __init__.py
│       ├── file_utils.py          # 文件处理（RAW/JPG匹配/压缩包解析）
│       ├── exif_utils.py          # EXIF元数据提取
│       └── security_utils.py       # 密码加密/敏感词过滤
├── alembic/                       # 数据库迁移（SQLAlchemy迁移工具）
│   ├── versions/                  # 迁移版本文件
│   └── env.py                     # 迁移配置
├── .env                           # 环境变量（数据库地址/密钥等）
├── .env.example                   # 环境变量示例
├── requirements.txt               # 后端依赖清单
├── Dockerfile                     # Docker部署配置
├── docker-compose.yml             # 容器编排（PostgreSQL+Redis+应用）
├── main.py                        # 项目入口（FastAPI初始化+路由注册）
└── README.md                      # 后端开发/部署说明


frontend/
├── public/                        # 静态资源（无需编译）
│   ├── favicon.ico                # 网站图标
│   └── index.html                 # 入口HTML模板
├── src/
│   ├── api/                       # API接口封装
│   │   ├── __init__.py
│   │   ├── auth.ts                # 认证接口（登录/注册/个人信息）
│   │   ├── album.ts               # 图片集接口
│   │   ├── image.ts                # 图片接口（上传/下载）
│   │   ├── blog.ts                 # 博客接口（发布/评论）
│   │   ├── search.ts               # 搜索接口
│   │   └── admin.ts                # 管理员接口
│   ├── assets/                    # 静态资源（需编译）
│   │   ├── icons/                  # 图标资源
│   │   ├── styles/                # 样式文件
│   │   │   ├── global.scss        # 全局样式
│   │   │   ├── element-plus.scss  # Element Plus样式覆盖
│   │   │   └── variables.scss     # 样式变量
│   │   └── images/                # 图片资源（默认封面等）
│   ├── components/                # 公共组件
│   │   ├── __init__.py
│   │   ├── common/                # 通用组件
│   │   │   ├── PageHeader.vue     # 页面头部组件
│   │   │   ├── EmptyState.vue      # 空状态组件
│   │   │   ├── Loading.vue        # 加载组件
│   │   │   └── Pagination.vue      # 分页组件
│   │   ├── album/                  # 图片集相关组件
│   │   │   ├── AlbumCard.vue       # 图片集卡片
│   │   │   ├── ImageGrid.vue       # 图片网格展示
│   │   │   ├── ImageWaterfall.vue  # 图片瀑布流展示
│   │   │   └── AlbumPassword.vue   # 密码验证组件
│   │   ├── blog/                  # 博客相关组件
│   │   │   ├── MarkdownEditor.vue  # Markdown编辑器
│   │   │   ├── BlogCard.vue       # 博客卡片
│   │   │   └── CommentList.vue     # 评论列表组件
│   │   └── upload/                 # 上传相关组件
│   │       ├── ImageUpload.vue     # 图片上传（支持拖拽/批量）
│   │       ├── ZipUpload.vue       # 压缩包上传组件
│   │       └── UploadProgress.vue  # 上传进度组件
│   ├── layout/                     # 布局组件
│   │   ├── __init__.py
│   │   ├── index.vue              # 全局布局（侧边栏+顶部导航）
│   │   ├── Sidebar.vue             # 侧边栏组件
│   │   └── Header.vue              # 顶部导航组件
│   ├── router/                     # 路由配置
│   │   ├── __init__.py
│   │   └── index.ts               # 路由规则（含权限守卫）
│   ├── store/                      # 状态管理（Pinia）
│   │   ├── __init__.py
│   │   └── modules/
│   │       ├── user.ts             # 用户状态（登录/个人信息）
│   │       ├── album.ts            # 图片集状态（列表/当前图片集）
│   │       ├── blog.ts             # 博客状态（草稿/发布）
│   │       └── app.ts              # 应用状态（主题/加载状态）
│   ├── types/                      # TypeScript类型定义
│   │   ├── __init__.py
│   │   ├── user.ts                 # 用户相关类型
│   │   ├── album.ts                # 图片集相关类型
│   │   ├── image.ts                # 图片相关类型
│   │   └── blog.ts                 # 博客相关类型
│   ├── utils/                      # 工具函数
│   │   ├── __init__.py
│   │   ├── request.ts              # Axios封装（请求/响应拦截）
│   │   ├── permission.ts           # 权限工具（角色判断/路由守卫）
│   │   ├── format.ts               # 格式化工具（日期/文件大小）
│   │   └── markdown.ts             # Markdown渲染工具
│   ├── views/                      # 页面组件
│   │   ├── __init__.py
│   │   ├── auth/                   # 认证页面
│   │   │   ├── Login.vue           # 登录页
│   │   │   └── Register.vue        # 注册页
│   │   ├── home/                   # 首页
│   │   │   └── Home.vue            # 首页（展示推荐/公告）
│   │   ├── album/                  # 图片集页面
│   │   │   ├── AlbumList.vue       # 图片集列表页
│   │   │   ├── AlbumCreate.vue     # 图片集创建页
│   │   │   ├── AlbumDetail.vue     # 图片集详情页
│   │   │   └── AlbumRecycle.vue    # 图片集回收站
│   │   ├── blog/                   # 博客页面
│   │   │   ├── BlogList.vue        # 博客列表页
│   │   │   ├── BlogCreate.vue      # 博客发布页
│   │   │   ├── BlogDetail.vue      # 博客详情页
│   │   │   └── BlogDraft.vue       # 草稿箱页面
│   │   ├── user/                   # 个人中心页面
│   │   │   ├── Profile.vue         # 个人资料页
│   │   │   ├── AvatarUpload.vue    # 头像上传页
│   │   │   └── PrivacySetting.vue  # 隐私设置页
│   │   ├── search/                 # 搜索页面
│   │   │   ├── SearchResult.vue    # 搜索结果页
│   │   │   └── AdvancedSearch.vue  # 高级搜索页
│   │   ├── admin/                  # 管理员页面
│   │   │   ├── UserManage.vue      # 用户管理页
│   │   │   ├── SystemStats.vue     # 系统统计页
│   │   │   └── SensitiveWord.vue    # 敏感词管理页
│   │   └── common/                 # 公共页面
│   │       ├── NotFound.vue        # 404页面
│   │       └── Forbidden.vue        # 无权限页面
│   ├── App.vue                     # 根组件（路由出口）
│   ├── main.ts                     # 入口文件（Vue初始化+依赖注册）
│   └── env.d.ts                    # 环境变量类型声明
├── .env.development                # 开发环境变量
├── .env.production                 # 生产环境变量
├── .eslintrc.js                    # ESLint配置
├── .prettierrc                     # Prettier配置
├── tsconfig.json                   # TypeScript配置
├── tsconfig.node.json              # Node类型配置
├── vite.config.ts                  # Vite构建配置
├── package.json                    # 前端依赖清单
├── package-lock.json               # 依赖锁文件
├── Dockerfile                      # Docker部署配置
└── README.md                      # 前端开发/部署说明


deploy/
├── nginx/                          # Nginx配置（反向代理+静态资源）
│   ├── nginx.conf                  # 核心配置（前端静态资源+API反向代理）
│   └── mime.types                  # MIME类型配置
├── docker-compose.prod.yml         # 生产环境容器编排（应用+数据库+Redis）
├── backup-script/                  # 备份脚本
│   ├── db-backup.bat               # 数据库每周全量备份脚本（Windows批处理）
│   └── backup-clean.bat            # 备份清理脚本（保留30天）
└── README.md                       # 生产环境部署手册（Windows Server）
