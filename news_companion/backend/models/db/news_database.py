"""
新闻数据库模块，用于存储和检索新闻
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import logging

class NewsDatabase:
    def __init__(self, db_path: str = "news.db"):
        """初始化数据库连接"""
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """初始化数据库表"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建新闻表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS news (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT UNIQUE,
                        title TEXT,
                        content TEXT,
                        summary TEXT,
                        tags TEXT,  -- JSON array of tags
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建标签表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tags (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE,
                        count INTEGER DEFAULT 1
                    )
                """)
                
                conn.commit()
        except Exception as e:
            logging.error(f"Database initialization error: {str(e)}")
            raise
            
    def add_news(self, url: str, title: str, content: str, summary: str, tags: List[str]) -> bool:
        """添加新闻到数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 存储新闻
                cursor.execute(
                    "INSERT OR REPLACE INTO news (url, title, content, summary, tags) VALUES (?, ?, ?, ?, ?)",
                    (url, title, content, summary, json.dumps(tags, ensure_ascii=False))
                )
                
                # 更新标签统计
                for tag in tags:
                    cursor.execute(
                        "INSERT INTO tags (name) VALUES (?) ON CONFLICT(name) DO UPDATE SET count = count + 1",
                        (tag,)
                    )
                
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Error adding news: {str(e)}")
            return False
            
    def get_similar_news(self, tags: List[str], limit: int = 5) -> List[Dict]:
        """根据标签获取相似新闻"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.create_function("json_contains", 2, lambda x, y: y in json.loads(x))
                cursor = conn.cursor()
                
                # 构建查询条件
                conditions = []
                params = []
                for tag in tags:
                    conditions.append("json_contains(tags, ?)")
                    params.append(tag)
                
                where_clause = " OR ".join(conditions) if conditions else "1"
                
                # 使用标签匹配度和时间戳排序
                query = f"""
                    WITH matched_news AS (
                        SELECT *,
                            (
                                SELECT COUNT(*)
                                FROM json_each(tags) t
                                WHERE t.value IN ({','.join('?' * len(tags))})
                            ) as match_count
                        FROM news
                        WHERE {where_clause}
                    )
                    SELECT 
                        id,
                        url,
                        title,
                        summary,
                        tags,
                        timestamp,
                        match_count
                    FROM matched_news
                    WHERE match_count > 0
                    ORDER BY match_count DESC, timestamp DESC
                    LIMIT ?
                """
                
                cursor.execute(query, params + tags + [limit])
                results = cursor.fetchall()
                
                news_list = []
                for row in results:
                    news_list.append({
                        'id': row[0],
                        'url': row[1],
                        'title': row[2],
                        'summary': row[3],
                        'tags': json.loads(row[4]),
                        'timestamp': row[5],
                        'relevance': row[6]
                    })
                
                return news_list
        except Exception as e:
            logging.error(f"Error getting similar news: {str(e)}")
            return []
            
    def get_popular_tags(self, limit: int = 10) -> List[Dict]:
        """获取热门标签"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name, count FROM tags ORDER BY count DESC LIMIT ?",
                    (limit,)
                )
                return [{'name': row[0], 'count': row[1]} for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error getting popular tags: {str(e)}")
            return []
