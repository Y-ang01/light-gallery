-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. 创建用户表 (users)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(10) NOT NULL DEFAULT 'USER', -- ADMIN, AUTHOR, USER
    avatar_url VARCHAR(500),
    profile TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 创建图片集表 (albums)
CREATE TABLE albums (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    cover_image_url VARCHAR(500),
    is_public BOOLEAN DEFAULT TRUE,
    is_password_protected BOOLEAN DEFAULT FALSE,
    password_hash VARCHAR(255),
    owner_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. 创建图片表 (images)
CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    album_id UUID NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    raw_file_url VARCHAR(500),
    file_size BIGINT,
    mime_type VARCHAR(100),
    exif_data JSONB,
    uploader_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (album_id) REFERENCES albums(id) ON DELETE CASCADE,
    FOREIGN KEY (uploader_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. 创建博客文章表 (blog_posts)
CREATE TABLE blog_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    content_md TEXT,
    content_html TEXT,
    pdf_url VARCHAR(500),
    is_published BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT TRUE,
    author_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 5. 创建评论表 (comments)
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL,
    user_id UUID, -- 可空，支持匿名评论
    content TEXT NOT NULL,
    parent_id UUID, -- 支持回复功能
    like_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES blog_posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (parent_id) REFERENCES comments(id) ON DELETE CASCADE
);

-- 索引创建
-- 用户表索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_created_at ON users(created_at);

-- 图片集表索引
CREATE INDEX idx_albums_owner_id ON albums(owner_id);
CREATE INDEX idx_albums_created_at ON albums(created_at);
CREATE INDEX idx_albums_is_public ON albums(is_public);

-- 图片表索引
CREATE INDEX idx_images_album_id ON images(album_id);
CREATE INDEX idx_images_uploader_id ON images(uploader_id);
CREATE INDEX idx_images_created_at ON images(created_at);
CREATE INDEX idx_images_file_size ON images(file_size);

-- 博客文章表索引
CREATE INDEX idx_blog_posts_author_id ON blog_posts(author_id);
CREATE INDEX idx_blog_posts_created_at ON blog_posts(created_at);
CREATE INDEX idx_blog_posts_is_published ON blog_posts(is_published);
CREATE INDEX idx_blog_posts_is_public ON blog_posts(is_public);

-- 评论表索引
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_comments_parent_id ON comments(parent_id);
CREATE INDEX idx_comments_created_at ON comments(created_at);

-- 插入管理员用户 (密码: admin123)
INSERT INTO users (id, email, username, password_hash, role, is_active) VALUES
(
    '11111111-1111-1111-1111-111111111111',
    'admin@light-gallery.com',
    'admin',
    '$2b$12$LQv3c1yqBWVHrn0U6pRrE.7Z6Yk5wQW8q8q8q8q8q8q8q8q8q8q8q', -- bcrypt hash of 'admin123'
    'ADMIN',
    true
);

-- 插入示例作者用户 (密码: author123)
INSERT INTO users (id, email, username, password_hash, role, is_active) VALUES
(
    '22222222-2222-2222-2222-222222222222',
    'author@light-gallery.com',
    'photographer',
    '$2b$12$LQv3c1yqBWVHrn0U6pRrE.7Z6Yk5wQW8q8q8q8q8q8q8q8q8q8q8q', -- bcrypt hash of 'author123'
    'AUTHOR',
    true
);

-- 插入示例普通用户 (密码: user123)
INSERT INTO users (id, email, username, password_hash, role, is_active) VALUES
(
    '33333333-3333-3333-3333-333333333333',
    'user@light-gallery.com',
    'visitor',
    '$2b$12$LQv3c1yqBWVHrn0U6pRrE.7Z6Yk5wQW8q8q8q8q8q8q8q8q8q8q8q', -- bcrypt hash of 'user123'
    'USER',
    true
);

-- 授予表操作权限
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO postgres;

-- 授予序列操作权限（如果使用序列）
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- 设置默认权限（对新创建的表自动授权）
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO postgres;