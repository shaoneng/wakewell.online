import google.generativeai as genai
import os
import random
from datetime import datetime
from bs4 import BeautifulSoup # Import BeautifulSoup

# --- 配置 ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY") 
BLOG_POST_DIR = "blog-post"
BLOG_LIST_FILE = "blog.html" # Path to your blog list page

# 核心关键词库
KEYWORDS = [
    "Deep sleep benefits", "REM sleep importance", "Fixing sleep schedule",
    "What is sleep inertia", "How sleep cycles work", "Napping effectively",
    "Foods that help sleep", "Blue light and sleep", "Creating a sleep sanctuary",
    "Morning grogginess cure", "Natural sleep aids"
]

# --- Gemini API 设置 ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-pro')

def update_blog_list(new_post_filename, title, description):
    """
    Opens blog.html, adds the new post to the top of the list, and saves it.
    """
    print(f"正在更新博客列表: {BLOG_LIST_FILE}")
    try:
        with open(BLOG_LIST_FILE, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        main_section = soup.find('main')
        if not main_section:
            print("错误: 在 blog.html 中未找到 <main> 标签。")
            return

        # Create the new article HTML structure
        article = soup.new_tag('article', **{'class': 'group'})
        
        h2 = soup.new_tag('h2', **{'class': 'text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight'})
        h2_link = soup.new_tag('a', href=f'./blog-post/{new_post_filename}', **{'class': 'hover:text-sky-500 transition-colors duration-300'})
        h2_link.string = title
        h2.append(h2_link)
        
        p = soup.new_tag('p', **{'class': 'mt-3 text-slate-600 leading-relaxed max-w-3xl'})
        p.string = description
        
        read_more_link = soup.new_tag('a', href=f'./blog-post/{new_post_filename}', **{'class': 'inline-block mt-4 font-bold text-sky-500 group-hover:text-sky-600 transition-colors duration-300'})
        read_more_link.string = "Read More →"

        article.append(h2)
        article.append(p)
        article.append(read_more_link)

        # Add a little space before the new article
        main_section.insert(0, soup.new_tag('hr', **{'class': 'my-12 border-t border-slate-200'}))
        main_section.insert(0, article)

        with open(BLOG_LIST_FILE, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        
        print("博客列表更新成功！")

    except Exception as e:
        print(f"更新 blog.html 时发生错误: {e}")


def generate_blog_post():
    """
    Generates a new blog post, saves it, and updates the blog list page.
    """
    print("开始全自动博客发布流程...")
    
    today_keywords = random.sample(KEYWORDS, 2)
    print(f"今日关键词: {', '.join(today_keywords)}")

    prompt = f"""
    You are an expert sleep scientist and a friendly, engaging blog writer. Your goal is to write a blog post for the WakeWell.online website.

    Today's main keywords are: "{today_keywords[0]}", "{today_keywords[1]}".

    Please perform the following tasks:
    1.  Generate a compelling, SEO-friendly title for the blog post. The title should be no more than 60 characters.
    2.  Generate a meta description for the blog post. The description should be no more than 155 characters and should serve as the introductory paragraph.
    3.  Write a blog post of approximately 500-700 words.
    4.  The content must be 100% original, accurate, and easy to understand for a general audience.
    5.  Structure the article in clean HTML format. Use a main <h1> for the title. Use the meta description as the first <p> tag. Use multiple <h2> tags for section headings. Use <p>, <ul>, <ol>, and <strong> tags where appropriate.
    6.  Do not include <!DOCTYPE>, <html>, <head>, or <body> tags. Only provide the content that would go inside the <body> of an article page.
    """

    try:
        print("正在调用 Gemini API...")
        response = model.generate_content(prompt)
        
        if not response.text:
            print("错误: Gemini API 未返回有效内容。")
            return
            
        content = response.text
        
        # Use BeautifulSoup to reliably extract title and description from the generated content
        post_soup = BeautifulSoup(content, 'html.parser')
        title_tag = post_soup.find('h1')
        description_tag = post_soup.find('p')

        if not title_tag or not description_tag:
            print("错误: 生成的内容格式不正确，无法找到 h1 或 p 标签。")
            return
            
        title = title_tag.get_text(strip=True)
        description = description_tag.get_text(strip=True)

        # Create a clean, SEO-friendly filename
        slug = title.lower().replace(' ', '-').replace(':', '').replace('?', '').replace("'", "")
        today_str = datetime.now().strftime('%Y-%m-%d')
        file_name = f"{today_str}-{slug[:40]}.html" # Truncate slug to avoid long filenames
        file_path = os.path.join(BLOG_POST_DIR, file_name)

        os.makedirs(BLOG_POST_DIR, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"成功！文章已保存到: {file_path}")

        # Automatically update the blog list page
        update_blog_list(file_name, title, description)

    except Exception as e:
        print(f"执行过程中发生错误: {e}")


if __name__ == "__main__":
    generate_blog_post()
