# データベース設計書

## 1. データベース概要

### 使用技術
- **データベース**: PostgreSQL 15.x（Supabase）
- **認証**: Supabase Auth（JWT トークン）
- **セキュリティ**: Row Level Security (RLS)
- **リアルタイム**: PostgreSQL Realtime

### 設計原則
1. **正規化**: 第3正規形まで正規化
2. **パフォーマンス**: 適切なインデックス設計
3. **セキュリティ**: RLS による行レベルセキュリティ
4. **拡張性**: 将来の機能拡張を考慮した設計

## 2. テーブル設計

### 2.1 認証・ユーザー関連

#### users テーブル
```sql
-- ユーザー基本情報
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT auth.uid(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  avatar_url TEXT,
  bio TEXT,
  website TEXT,
  location TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS ポリシー
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- ユーザーは自分の情報のみ閲覧・更新可能
CREATE POLICY "Users can view own profile" ON users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
  FOR UPDATE USING (auth.uid() = id);

-- インデックス
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
```

#### user_profiles テーブル
```sql
-- ユーザー詳細プロフィール（拡張情報）
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  birth_date DATE,
  phone TEXT,
  company TEXT,
  job_title TEXT,
  skills TEXT[],
  preferences JSONB DEFAULT '{}',
  settings JSONB DEFAULT '{}',
  is_public BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS ポリシー
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own profile" ON user_profiles
  FOR ALL USING (auth.uid() = user_id);

-- 公開プロフィールは誰でも閲覧可能
CREATE POLICY "Public profiles are viewable" ON user_profiles
  FOR SELECT USING (is_public = true);

-- インデックス
CREATE UNIQUE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_public ON user_profiles(is_public) WHERE is_public = true;
```

### 2.2 コンテンツ管理

#### posts テーブル
```sql
-- 投稿
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  content TEXT,
  excerpt TEXT,
  slug TEXT UNIQUE,
  status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
  featured_image TEXT,
  tags TEXT[],
  metadata JSONB DEFAULT '{}',
  view_count INTEGER DEFAULT 0,
  like_count INTEGER DEFAULT 0,
  comment_count INTEGER DEFAULT 0,
  published_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS ポリシー
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- 公開投稿は誰でも閲覧可能
CREATE POLICY "Published posts are viewable" ON posts
  FOR SELECT USING (status = 'published');

-- 投稿者は自分の投稿を管理可能
CREATE POLICY "Users can manage own posts" ON posts
  FOR ALL USING (auth.uid() = user_id);

-- インデックス
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_status ON posts(status);
CREATE INDEX idx_posts_published_at ON posts(published_at DESC) WHERE status = 'published';
CREATE INDEX idx_posts_slug ON posts(slug) WHERE slug IS NOT NULL;
CREATE INDEX idx_posts_tags ON posts USING GIN(tags);

-- 全文検索インデックス
CREATE INDEX idx_posts_search ON posts USING GIN(
  to_tsvector('japanese', title || ' ' || COALESCE(content, ''))
);
```

#### comments テーブル
```sql
-- コメント
CREATE TABLE comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  parent_id UUID REFERENCES comments(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  is_approved BOOLEAN DEFAULT true,
  like_count INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS ポリシー
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;

-- 承認済みコメントは誰でも閲覧可能
CREATE POLICY "Approved comments are viewable" ON comments
  FOR SELECT USING (is_approved = true);

-- 認証ユーザーはコメント作成可能
CREATE POLICY "Authenticated users can create comments" ON comments
  FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);

-- コメント作成者は自分のコメントを編集・削除可能
CREATE POLICY "Users can manage own comments" ON comments
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own comments" ON comments
  FOR DELETE USING (auth.uid() = user_id);

-- インデックス
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_comments_parent_id ON comments(parent_id);
CREATE INDEX idx_comments_created_at ON comments(created_at);
```

### 2.3 インタラクション

#### likes テーブル
```sql
-- いいね
CREATE TABLE likes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 複合ユニーク制約（1ユーザー1投稿1いいね）
ALTER TABLE likes ADD CONSTRAINT unique_user_post_like 
  UNIQUE (user_id, post_id);

-- RLS ポリシー
ALTER TABLE likes ENABLE ROW LEVEL SECURITY;

-- 認証ユーザーはいいねの作成・削除可能
CREATE POLICY "Users can manage own likes" ON likes
  FOR ALL USING (auth.uid() = user_id);

-- インデックス
CREATE INDEX idx_likes_post_id ON likes(post_id);
CREATE INDEX idx_likes_user_id ON likes(user_id);
```

#### follows テーブル
```sql
-- フォロー関係
CREATE TABLE follows (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  follower_id UUID REFERENCES users(id) ON DELETE CASCADE,
  following_id UUID REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 複合ユニーク制約
ALTER TABLE follows ADD CONSTRAINT unique_follow_relationship 
  UNIQUE (follower_id, following_id);

-- 自分自身をフォローできない制約
ALTER TABLE follows ADD CONSTRAINT no_self_follow 
  CHECK (follower_id != following_id);

-- RLS ポリシー
ALTER TABLE follows ENABLE ROW LEVEL SECURITY;

-- フォロー関係は誰でも閲覧可能
CREATE POLICY "Follows are viewable" ON follows
  FOR SELECT USING (true);

-- 認証ユーザーはフォロー関係の作成・削除可能
CREATE POLICY "Users can manage own follows" ON follows
  FOR INSERT TO authenticated WITH CHECK (auth.uid() = follower_id);

CREATE POLICY "Users can delete own follows" ON follows
  FOR DELETE USING (auth.uid() = follower_id);

-- インデックス
CREATE INDEX idx_follows_follower_id ON follows(follower_id);
CREATE INDEX idx_follows_following_id ON follows(following_id);
```

## 3. ビュー定義

### 3.1 投稿詳細ビュー
```sql
-- 投稿詳細（作成者情報含む）
CREATE VIEW post_details AS
SELECT 
  p.id,
  p.title,
  p.content,
  p.excerpt,
  p.slug,
  p.status,
  p.featured_image,
  p.tags,
  p.view_count,
  p.like_count,
  p.comment_count,
  p.published_at,
  p.created_at,
  p.updated_at,
  u.name as author_name,
  u.avatar_url as author_avatar,
  u.id as author_id
FROM posts p
LEFT JOIN users u ON p.user_id = u.id;
```

### 3.2 ユーザー統計ビュー
```sql
-- ユーザー統計情報
CREATE VIEW user_stats AS
SELECT 
  u.id,
  u.name,
  u.avatar_url,
  u.created_at,
  COUNT(DISTINCT p.id) as post_count,
  COUNT(DISTINCT l.id) as like_count,
  COUNT(DISTINCT c.id) as comment_count,
  COUNT(DISTINCT f1.id) as follower_count,
  COUNT(DISTINCT f2.id) as following_count
FROM users u
LEFT JOIN posts p ON u.id = p.user_id AND p.status = 'published'
LEFT JOIN likes l ON u.id = l.user_id
LEFT JOIN comments c ON u.id = c.user_id
LEFT JOIN follows f1 ON u.id = f1.following_id
LEFT JOIN follows f2 ON u.id = f2.follower_id
GROUP BY u.id, u.name, u.avatar_url, u.created_at;
```

## 4. 関数とトリガー

### 4.1 更新日時自動更新
```sql
-- 更新日時を自動で設定する関数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 各テーブルにトリガーを適用
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_posts_updated_at BEFORE UPDATE ON posts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_comments_updated_at BEFORE UPDATE ON comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 4.2 カウンター更新関数
```sql
-- いいね数更新関数
CREATE OR REPLACE FUNCTION update_like_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE posts SET like_count = like_count + 1 
        WHERE id = NEW.post_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE posts SET like_count = like_count - 1 
        WHERE id = OLD.post_id;
        RETURN OLD;
    END IF;
END;
$$ language 'plpgsql';

-- いいねテーブルにトリガーを適用
CREATE TRIGGER update_post_like_count
    AFTER INSERT OR DELETE ON likes
    FOR EACH ROW EXECUTE FUNCTION update_like_count();

-- コメント数更新関数
CREATE OR REPLACE FUNCTION update_comment_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE posts SET comment_count = comment_count + 1 
        WHERE id = NEW.post_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE posts SET comment_count = comment_count - 1 
        WHERE id = OLD.post_id;
        RETURN OLD;
    END IF;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_post_comment_count
    AFTER INSERT OR DELETE ON comments
    FOR EACH ROW EXECUTE FUNCTION update_comment_count();
```

## 5. セキュリティ設計

### 5.1 RLS ポリシーの階層設計
```sql
-- 管理者権限の確認関数
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM user_profiles 
        WHERE user_id = auth.uid() 
        AND (settings->>'role')::text = 'admin'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 管理者は全てのデータを管理可能
CREATE POLICY "Admins can manage all posts" ON posts
  FOR ALL USING (is_admin());
```

### 5.2 機密情報の暗号化
```sql
-- 機密情報テーブル（暗号化）
CREATE TABLE user_secrets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  encrypted_data TEXT, -- pgcrypto で暗号化
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 暗号化関数の例
CREATE OR REPLACE FUNCTION encrypt_sensitive_data(data TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN encode(
        encrypt(data::bytea, 'encryption_key', 'aes'), 
        'base64'
    );
END;
$$ LANGUAGE plpgsql;
```

## 6. パフォーマンス最適化

### 6.1 重要なインデックス
```sql
-- 複合インデックス
CREATE INDEX idx_posts_user_status_published ON posts(user_id, status, published_at DESC)
WHERE status = 'published';

-- 部分インデックス
CREATE INDEX idx_posts_featured ON posts(featured_image)
WHERE featured_image IS NOT NULL;

-- JSON インデックス
CREATE INDEX idx_user_profiles_skills ON user_profiles USING GIN(skills);
CREATE INDEX idx_posts_metadata ON posts USING GIN(metadata);
```

### 6.2 マテリアライズドビュー
```sql
-- 人気投稿のマテリアライズドビュー
CREATE MATERIALIZED VIEW popular_posts AS
SELECT 
    p.id,
    p.title,
    p.slug,
    p.like_count,
    p.comment_count,
    p.view_count,
    p.published_at,
    u.name as author_name,
    (p.like_count * 2 + p.comment_count * 3 + p.view_count * 0.1) as popularity_score
FROM posts p
JOIN users u ON p.user_id = u.id
WHERE p.status = 'published'
ORDER BY popularity_score DESC;

-- インデックス
CREATE INDEX idx_popular_posts_score ON popular_posts(popularity_score DESC);

-- 定期更新のスケジュール（cronジョブで実行）
-- REFRESH MATERIALIZED VIEW popular_posts;
```

## 7. データマイグレーション

### 7.1 初期データ投入
```sql
-- デフォルトユーザー作成（開発環境用）
INSERT INTO users (id, email, name, avatar_url) VALUES 
('12345678-1234-1234-1234-123456789012', 'admin@example.com', '管理者', 'https://example.com/avatar.jpg')
ON CONFLICT (id) DO NOTHING;

-- サンプル投稿作成
INSERT INTO posts (user_id, title, content, status, published_at) VALUES 
('12345678-1234-1234-1234-123456789012', 'サンプル投稿', 'これはサンプル投稿です。', 'published', NOW())
ON CONFLICT DO NOTHING;
```

### 7.2 マイグレーション管理
```sql
-- マイグレーション履歴テーブル
CREATE TABLE migrations (
  id SERIAL PRIMARY KEY,
  version TEXT UNIQUE NOT NULL,
  description TEXT,
  executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- マイグレーション実行記録
INSERT INTO migrations (version, description) VALUES 
('20240101_001', '初期テーブル作成'),
('20240101_002', 'RLSポリシー設定'),
('20240101_003', 'インデックス作成');
```

## 8. バックアップとリストア

### 8.1 バックアップ戦略
```bash
# 定期バックアップスクリプト（Supabase CLI使用）
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# データベースダンプ
supabase db dump --file "${BACKUP_DIR}/backup_${DATE}.sql"

# 古いバックアップの削除（30日以上）
find ${BACKUP_DIR} -name "backup_*.sql" -mtime +30 -delete
```

### 8.2 災害復旧手順
```sql
-- Point-in-Time Recovery の設定
-- Supabase では自動的に設定されているが、確認コマンド
SELECT name, setting FROM pg_settings 
WHERE name IN ('wal_level', 'archive_mode', 'archive_command');
```

## 9. 監視とメンテナンス

### 9.1 パフォーマンス監視クエリ
```sql
-- 実行時間の長いクエリ
SELECT 
    query,
    mean_exec_time,
    calls,
    total_exec_time,
    stddev_exec_time
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;

-- テーブルサイズ監視
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public'
ORDER BY tablename, attname;
```

### 9.2 定期メンテナンス
```sql
-- 統計情報の更新
ANALYZE;

-- インデックスの再構築（必要に応じて）
REINDEX TABLE posts;

-- 不要データの削除
DELETE FROM posts 
WHERE status = 'draft' 
AND updated_at < NOW() - INTERVAL '1 year';
```

## 10. 型定義（JSDoc用）

### 10.1 テーブル型定義
```javascript
/**
 * @typedef {Object} User
 * @property {string} id - ユーザーID
 * @property {string} email - メールアドレス
 * @property {string|null} name - 表示名
 * @property {string|null} avatar_url - アバター画像URL
 * @property {string|null} bio - 自己紹介
 * @property {string} created_at - 作成日時
 * @property {string} updated_at - 更新日時
 */

/**
 * @typedef {Object} Post
 * @property {string} id - 投稿ID
 * @property {string} user_id - 投稿者ID
 * @property {string} title - タイトル
 * @property {string|null} content - 本文
 * @property {string|null} excerpt - 抜粋
 * @property {string|null} slug - URL スラッグ
 * @property {'draft'|'published'|'archived'} status - ステータス
 * @property {string[]|null} tags - タグ配列
 * @property {number} view_count - 閲覧数
 * @property {number} like_count - いいね数
 * @property {number} comment_count - コメント数
 * @property {string|null} published_at - 公開日時
 * @property {string} created_at - 作成日時
 * @property {string} updated_at - 更新日時
 */
```

## 11. まとめ

このデータベース設計の特徴：

1. **セキュリティファースト**: RLS による行レベルセキュリティ
2. **パフォーマンス重視**: 適切なインデックス設計
3. **拡張性**: 将来の機能追加を考慮した柔軟な設計
4. **整合性**: 外部キー制約とトリガーによるデータ整合性
5. **監視可能**: パフォーマンス監視とメンテナンス機能

### 関連ドキュメント
- [API設計](./03_api_design.md)
- [Supabase統合ガイド](../03_library_docs/03_supabase_integration.md)
- [セキュリティ設計](./07_error_handling_design.md)