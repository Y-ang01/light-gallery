-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 用户表 (users)
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

-- 图片集表 (albums)
CREATE TABLE albums (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    cover_image_url VARCHAR(500),
    is_public BOOLEAN DEFAULT TRUE,
    is_password_protected BOOLEAN DEFAULT FALSE,
    password_hash VARCHAR(255),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 图片表 (images)
CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    album_id UUID NOT NULL REFERENCES albums(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    raw_file_url VARCHAR(500),
    file_size BIGINT,
    mime_type VARCHAR(100),
    exif_data JSONB,
    uploader_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 博客文章表 (blog_posts)
CREATE TABLE blog_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    content_md TEXT,
    content_html TEXT,
    pdf_url VARCHAR(500),
    is_published BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT TRUE,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 评论表 (comments)
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES blog_posts(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    parent_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    like_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引创建
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_albums_owner_id ON albums(owner_id);
CREATE INDEX idx_images_album_id ON images(album_id);
CREATE INDEX idx_blog_posts_author_id ON blog_posts(author_id);
CREATE INDEX idx_blog_posts_published ON blog_posts(is_published, created_at DESC);
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);

-- 测试数据（可选）
INSERT INTO users (email, username, password_hash, role) VALUES
('admin@lightgallery.com', 'admin', '$2b$12$YourHashedPasswordHere', 'ADMIN'),
('author@lightgallery.com', 'photographer', '$2b$12$YourHashedPasswordHere', 'AUTHOR'),
('user@lightgallery.com', 'visitor', '$2b$12$YourHashedPasswordHere', 'USER');