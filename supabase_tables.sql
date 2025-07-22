-- Supabase SQL Editor'da çalıştırılacak tablolar
-- Bu kodları Supabase Dashboard > SQL Editor'a kopyalayıp çalıştırın

-- 1. Map Data Tablosu
CREATE TABLE IF NOT EXISTS map_data (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    phone VARCHAR(50),
    website TEXT,
    rating DECIMAL(3,2),
    reviews_count INTEGER,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    category VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, address)
);

-- 2. Instagram Data Tablosu
CREATE TABLE IF NOT EXISTS instagram_data (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    bio TEXT,
    followers_count BIGINT,
    following_count BIGINT,
    posts_count BIGINT,
    profile_pic_url TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    is_private BOOLEAN DEFAULT FALSE,
    external_url TEXT,
    category VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Facebook Data Tablosu
CREATE TABLE IF NOT EXISTS facebook_data (
    id BIGSERIAL PRIMARY KEY,
    page_name VARCHAR(255) UNIQUE NOT NULL,
    page_id VARCHAR(100),
    description TEXT,
    likes_count BIGINT,
    followers_count BIGINT,
    page_url TEXT,
    profile_pic_url TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    category VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255),
    website TEXT,
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Twitter Data Tablosu
CREATE TABLE IF NOT EXISTS twitter_data (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    bio TEXT,
    followers_count BIGINT,
    following_count BIGINT,
    tweets_count BIGINT,
    profile_pic_url TEXT,
    banner_url TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    is_private BOOLEAN DEFAULT FALSE,
    location VARCHAR(255),
    website TEXT,
    join_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. LinkedIn Data Tablosu
CREATE TABLE IF NOT EXISTS linkedin_data (
    id BIGSERIAL PRIMARY KEY,
    profile_name VARCHAR(255) NOT NULL,
    headline VARCHAR(500),
    summary TEXT,
    connections_count INTEGER,
    profile_url TEXT,
    profile_pic_url TEXT,
    location VARCHAR(255),
    industry VARCHAR(255),
    current_company VARCHAR(255),
    current_position VARCHAR(255),
    education TEXT,
    skills TEXT,
    experience_years INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(profile_name, current_company)
);

-- 6. TikTok Data Tablosu
CREATE TABLE IF NOT EXISTS tiktok_data (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    bio TEXT,
    followers_count BIGINT,
    following_count BIGINT,
    likes_count BIGINT,
    videos_count BIGINT,
    profile_pic_url TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    is_private BOOLEAN DEFAULT FALSE,
    external_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Demo veriler ekleme (opsiyonel)
-- Tabloları oluşturduktan sonra bu INSERT komutlarını da çalıştırabilirsiniz

-- Map Data Demo Veriler
INSERT INTO map_data (name, address, phone, website, rating, reviews_count, category, latitude, longitude) VALUES
('Cafe İstanbul', 'Beyoğlu, İstanbul', '0212 123 4567', 'https://cafeistanbul.com', 4.5, 234, 'Kafe', 41.0082, 28.9784),
('Teknoloji Mağazası', 'Çankaya, Ankara', '0312 456 7890', 'https://teknoloji.com', 4.2, 189, 'Elektronik', 39.9334, 32.8597),
('Spor Salonu', 'Konak, İzmir', '0232 789 0123', 'https://sporsalonu.com', 4.7, 456, 'Fitness', 38.4237, 27.1428),
('Restoran Lezzet', 'Nilüfer, Bursa', '0224 345 6789', 'https://restoranl.com', 4.3, 312, 'Restoran', 40.1826, 29.0665),
('Kuaför Salon', 'Muratpaşa, Antalya', '0242 678 9012', 'https://kuaforsalon.com', 4.6, 167, 'Güzellik', 36.8969, 30.7133);

-- Instagram Data Demo Veriler
INSERT INTO instagram_data (username, full_name, bio, followers_count, following_count, posts_count, is_verified, category) VALUES
('teknoloji_rehberi', 'Teknoloji Rehberi', 'En son teknoloji haberleri ve incelemeler', 234000, 1200, 456, true, 'Teknoloji'),
('yemek_dunyasi', 'Yemek Dünyası', 'Lezzetli tarifler ve restoran önerileri', 189000, 890, 1200, false, 'Yemek'),
('spor_motivasyon', 'Spor Motivasyon', 'Günlük antrenman ve motivasyon', 345000, 567, 789, true, 'Spor'),
('seyahat_gunlugu', 'Seyahat Günlüğü', 'Dünyadan seyahat deneyimleri', 123000, 2100, 678, false, 'Seyahat'),
('moda_trendleri', 'Moda Trendleri', 'En son moda trendleri ve stil önerileri', 456000, 1800, 2100, true, 'Moda');

-- Facebook Data Demo Veriler
INSERT INTO facebook_data (page_name, description, likes_count, followers_count, category, phone, website, address, is_verified) VALUES
('Teknoloji Dünyası', 'Teknoloji haberlerinin merkezi', 125000, 142000, 'Teknoloji', '0212 123 4567', 'https://teknolojidunyasi.com', 'Istanbul', true),
('Yemek Tarifleri', 'Ev yapımı lezzetli tarifler', 89000, 95000, 'Yemek & İçecek', '0312 456 7890', 'https://yemektarifleri.com', 'Ankara', false),
('Spor Haberleri', 'Türkiye ve dünyadan spor haberleri', 203000, 225000, 'Spor', null, 'https://sporhaberleri.com', 'Istanbul', true),
('Gezi Rehberi', 'Türkiye turları ve seyahat tavsiyeleri', 67000, 73000, 'Seyahat', null, 'https://gezirehberi.com', 'Izmir', false),
('Moda Trendleri', 'En güncel moda haberleri', 156000, 178000, 'Moda & Güzellik', null, 'https://modatrendleri.com', 'Istanbul', true);

-- Twitter Data Demo Veriler
INSERT INTO twitter_data (username, display_name, bio, followers_count, following_count, tweets_count, is_verified, location) VALUES
('istanbul_daily', 'Istanbul Daily News', 'Daily news from Istanbul', 234000, 1200, 15600, true, 'Istanbul'),
('turkish_tech', 'Turkish Tech Community', 'Technology community in Turkey', 89000, 567, 8900, false, 'Ankara'),
('bosphorus_view', 'Bosphorus View', 'Beautiful views of Bosphorus', 156000, 234, 12300, true, 'Istanbul'),
('turkish_cuisine', 'Turkish Cuisine', 'Traditional Turkish food recipes', 78000, 445, 5400, false, 'Izmir'),
('ankara_events', 'Ankara Events', 'Events happening in Ankara', 45000, 678, 3200, false, 'Ankara');

-- LinkedIn Data Demo Veriler
INSERT INTO linkedin_data (profile_name, headline, current_company, current_position, connections_count, experience_years, industry, location) VALUES
('Ahmet Yılmaz', 'Software Engineer at Turkish Airlines', 'Turkish Airlines', 'Software Engineer', 1200, 8, 'Aviation', 'Istanbul'),
('Elif Demir', 'Data Scientist at Turkcell', 'Turkcell', 'Data Scientist', 890, 5, 'Telecommunications', 'Ankara'),
('Mehmet Kaya', 'Product Manager at Garanti BBVA', 'Garanti BBVA', 'Product Manager', 1500, 12, 'Finance', 'Istanbul'),
('Zeynep Özkan', 'UX Designer at Trendyol', 'Trendyol', 'UX Designer', 734, 6, 'E-commerce', 'Istanbul'),
('Can Erdoğan', 'Marketing Manager at Getir', 'Getir', 'Marketing Manager', 2100, 7, 'Technology', 'Istanbul');

-- TikTok Data Demo Veriler
INSERT INTO tiktok_data (username, display_name, bio, followers_count, following_count, likes_count, videos_count, is_verified) VALUES
('yemekkanalim', 'Yemek Kanalım', 'En lezzetli tarifler burada', 2300000, 1200, 45600000, 1200, true),
('dansci_murat', 'Dansçı Murat', 'Dans ve eğlence', 890000, 567, 23400000, 567, false),
('teknoaliinfo', 'TeknoAli', 'Teknoloji ve telefon incelemeleri', 1500000, 789, 34200000, 890, true),
('komeditime', 'Komedi Time', 'Günlük komedi içerikleri', 3100000, 234, 67800000, 2300, true),
('seyahattutkusu', 'Seyahat Tutkusu', 'Dünyayı gezip görmeyi seviyorum', 756000, 1800, 18900000, 423, false);
