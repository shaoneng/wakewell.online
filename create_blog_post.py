import google.generativeai as genai
import os
import random
import re
from datetime import datetime
from bs4 import BeautifulSoup

# --- 配置 ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY") 
BLOG_POST_DIR = "blog-post"
BLOG_LIST_FILE = "blog.html"

# 核心关键词库
KEYWORDS = [
    "Deep sleep benefits", "REM sleep importance", "Fixing sleep schedule",
    "What is sleep inertia", "How sleep cycles work", "Napping effectively",
    "Foods that help sleep", "Blue light and sleep", "Creating a sleep sanctuary",
    "Morning grogginess cure", "Natural sleep aids"
]

# --- Gemini API 设置 ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def clean_llm_output(raw_html):
    """
    清理大语言模型输出，确保只返回纯净的HTML正文部分。
    它会移除所有在第一个HTML标签之前的内容。
    """
    # 使用正则表达式找到第一个HTML标签（如<h1>, <p>）的位置
    match = re.search(r'<[a-zA-Z][a-zA-Z0-9]*.*?>', raw_html)
    if match:
        # 返回从第一个标签开始的所有内容
        return raw_html[match.start():]
    # 如果没有找到HTML标签，则可能返回的是错误信息或纯文本，按原样返回
    return raw_html

def update_blog_list(new_post_filename, title, description):
    """
    打开blog.html，添加新文章到列表顶部并保存。
    """
    print(f"正在更新博客列表: {BLOG_LIST_FILE}")
    try:
        with open(BLOG_LIST_FILE, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        main_section = soup.find('main')
        if not main_section:
            print("错误: 在 blog.html 中未找到 <main> 标签。")
            return

        article = soup.new_tag('article', **{'class': 'group border-t border-slate-200 pt-8'})
        
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
        
        # 将新文章插入到<main>标签内的最前面
        main_section.insert(0, article)

        with open(BLOG_LIST_FILE, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        
        print("博客列表更新成功！")

    except Exception as e:
        print(f"更新 blog.html 时发生错误: {e}")


def generate_blog_post():
    """
    生成一篇新的博客文章，清理内容，保存并更新列表。
    """
    print("开始博客生成流程...")
    
    today_keywords = random.sample(KEYWORDS, 2)
    print(f"今日关键词: {', '.join(today_keywords)}")

    # --- 这是关键：一个非常精确的Prompt ---
    prompt = f"""
    You are a sleep science writer for the WakeWell.online blog.
    Your task is to write a blog post about "{today_keywords[0]}" and "{today_keywords[1]}".

    **IMPORTANT INSTRUCTIONS:**
    1.  Your response MUST BE ONLY the raw HTML content for the article body.
    2.  Start your response DIRECTLY with the `<h1>` tag for the title. Do NOT include any introductory text, conversation, markdown fences (```html), or any text before the first `<h1>` tag.
    3.  Use the following Tailwind CSS classes precisely for styling:
        - For the main title: `<h1 class="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight">`
        - For section headers: `<h2 class="text-3xl font-bold text-slate-900 mt-12">`
        - For main paragraphs: `<p class="text-slate-600 leading-relaxed mt-4">`
        - For lists: `<ul class="list-disc list-inside text-slate-600 mt-4 space-y-2">`
        - For bold text: `<strong class="text-slate-700">`
    4.  The article should be between 500 and 700 words.
    5.  The first paragraph after the `<h1>` title will be used as the summary on the blog list page. Make it engaging.
    """

    try:
        print("正在调用 Gemini API...")
        response = model.generate_content(prompt)
        
        if not response.text:
            print("错误: Gemini API 未返回有效内容。")
            return

        # --- 关键步骤：清理输出 ---
        print("清理AI输出内容...")
        clean_html_content = clean_llm_output(response.text)

        # 使用BeautifulSoup从清理后的HTML中可靠地提取标题和描述
        post_soup = BeautifulSoup(clean_html_content, 'html.parser')
        title_tag = post_soup.find('h1')
        first_paragraph_tag = post_soup.find('p')

        if not title_tag or not first_paragraph_tag:
            print("错误: 生成的内容格式不正确，无法找到 h1 或 p 标签。")
            print("--- 返回的原始数据 ---")
            print(response.text)
            print("----------------------")
            return
            
        title = title_tag.get_text(strip=True)
        description = first_paragraph_tag.get_text(strip=True)

        # 创建文件名
        slug = title.lower().replace(' ', '-').replace(':', '').replace('?', '').replace("'", "")
        file_name = f"{datetime.now().strftime('%Y-%m-%d')}-{slug[:40]}.html"
        file_path = os.path.join(BLOG_POST_DIR, file_name)

        # 保存清理后的HTML内容
        os.makedirs(BLOG_POST_DIR, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(clean_html_content)
        
        print(f"成功！文章已保存到: {file_path}")

        # 更新博客列表页面
        update_blog_list(file_name, title, description)

    except Exception as e:
        print(f"执行过程中发生错误: {e}")


if __name__ == "__main__":
    generate_blog_post()
