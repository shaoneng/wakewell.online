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
BASE_URL = "https://wakewell.online" # 您的网站基础URL

# 核心关键词库
KEYWORDS = [
    "Deep sleep benefits", "REM sleep importance", "Fixing sleep schedule",
    "What is sleep inertia", "How sleep cycles work", "Napping effectively",
    "Foods that help sleep", "Blue light and sleep", "Creating a sleep sanctuary",
    "Morning grogginess cure", "Natural sleep aids",
    # Original Keywords
    "Deep sleep benefits", "REM sleep importance", "Fixing sleep schedule",
    "What is sleep inertia", "How sleep cycles work", "Napping effectively",
    "Foods that help sleep", "Blue light and sleep", "Creating a sleep sanctuary",
    "Morning grogginess cure", "Natural sleep aids",

    # Expanded Keywords: Sleep Quality & Stages
    "what are the stages of sleep", "how much deep sleep do you need",
    "benefits of deep sleep for brain", "what happens during REM sleep",
    "how to increase deep sleep naturally", "deep sleep vs light sleep",
    "importance of REM sleep for memory", "symptoms of not enough deep sleep",
    "REM sleep and dreams", "how to get more REM sleep",
    "best mattress for deep sleep", "apps to track sleep cycles",
    "sleep trackers with REM monitoring", "supplements to improve deep sleep",
    "best pillows for restorative sleep", "can you get too much deep sleep",
    "link between deep sleep and Alzheimer's", "does alcohol affect deep sleep",
    "how rem sleep affects learning and creativity",

    # Expanded Keywords: Sleep Schedule & Cycles
    "how to fix a broken sleep schedule", "how to reset your internal clock",
    "what is circadian rhythm", "how long is a sleep cycle in adults",
    "waking up in the middle of a sleep cycle", "how to get over sleep inertia fast",
    "why do I feel so tired when I wake up", "tips for waking up refreshed",
    "how to create a consistent sleep routine", "weekend sleep schedule vs weekday",
    "best sunrise alarm clocks", "light therapy lamps for circadian rhythm",
    "sleep coaching services review", "apps for managing sleep schedules",
    "how to fix sleep schedule for shift workers", "how long does it take to fix sleep schedule",
    "is it better to wake up at the end of a sleep cycle", "foods that help fight morning grogginess",

    # Expanded Keywords: Sleep Environment & Habits
    "how long should a power nap be", "best time of day to nap",
    "benefits of napping for productivity", "how does blue light affect melatonin",
    "how to block blue light from screens", "ideal bedroom temperature for sleep",
    "how to create a relaxing bedtime routine", "bedroom design for better sleep",
    "effects of noise on sleep quality", "blue light blocking glasses review",
    "best blackout curtains for bedroom", "top rated white noise machines",
    "best earplugs for sleeping", "aromatherapy diffusers for relaxation",
    "napping vs coffee for afternoon slump", "is it bad to nap for 2 hours",
    "creating a sleep sanctuary on a budget", "do blue light filters on phones actually work",

    # Expanded Keywords: Diet & Natural Aids
    "what to eat before bed for better sleep", "foods that disrupt sleep",
    "the role of magnesium in sleep", "melatonin-rich foods",
    "herbal teas for sleep", "natural alternatives to sleeping pills",
    "benefits of meditation for sleep", "yoga poses for better sleep",
    "is melatonin safe to take every night", "best magnesium supplements for sleep",
    "top rated melatonin gummies", "valerian root dosage for sleep",
    "best chamomile tea brands", "meditation apps for sleep",
    "recipe for a sleep-inducing smoothie", "does drinking warm milk actually help you sleep",
    "side effects of natural sleep aids", "can you combine melatonin and magnesium"

]

# --- 完整的HTML页面模板 (无变化) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-WQ3BLQSMKQ"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'G-WQ3BLQSMKQ');
    </script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>__PAGE_TITLE__ | WakeWell</title>
    <meta name="description" content="__META_DESCRIPTION__">
    <link rel="canonical" href="__CANONICAL_URL__">
    <link rel="icon" href="../data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100%22><text y=%22.9em%22 font-size=%2290%22>🌙</text></svg>">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['Nunito', 'sans-serif'],
                    }},
                }}
            }}
        }}
    </script>
</head>
<body class="bg-slate-50 text-slate-800 font-sans p-4 sm:p-6 lg:p-8">
    <div class="bg-white rounded-3xl shadow-2xl shadow-slate-200 p-6 sm:p-10 w-full max-w-3xl text-left mx-auto my-8 sm:my-12">
        <article class="prose lg:prose-xl max-w-none">
            <header>
                <div class="mb-6">
                    <a href="../blog.html" class="text-sky-500 hover:text-sky-700 transition-colors duration-300 no-underline">&larr; Back to Blog</a>
                </div>
                __ARTICLE_CONTENT__
            </header>
        </article>
        <footer class="mt-12 pt-8 border-t border-slate-200">
            <nav class="flex justify-center items-center space-x-4 text-sm text-slate-500 mb-4">
                <a href="../index.html" class="hover:text-sky-500 transition-colors">Calculator</a>
                <a href="../blog.html" class="hover:text-sky-500 transition-colors font-bold">Blog</a>
                <a href="#" class="hover:text-sky-500 transition-colors">About Us</a>
                <a href="#" class="hover:text-sky-500 transition-colors">Privacy Policy</a>
            </nav>
            <p class="text-xs text-slate-400 text-center">© 2024 WakeWell. All rights reserved.</p>
        </footer>
    </div>
    <style>
        .prose {{ color: #334155; }}
        .prose h1, .prose h2, .prose h3, .prose h4, .prose strong {{ color: #0f172a; }}
        .prose a {{ color: #0ea5e9; text-decoration: none; transition: color 0.3s; }}
        .prose a:hover {{ color: #0284c7; }}
        .prose ul > li::before {{ background-color: #38bdf8; }}
        .prose ol > li::before {{ color: #38bdf8; }}
    </style>
</body>
</html>
"""

# --- Gemini API 设置 (无变化) ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- Helper 函数 (无变化) ---
def clean_llm_output(raw_html):
    match = re.search(r'<[a-zA-Z][a-zA-Z0-9]*.*?>', raw_html)
    if match:
        return raw_html[match.start():]
    return raw_html

def update_blog_list(new_post_filename, title, description):
    print(f"正在更新博客列表: {BLOG_LIST_FILE}")
    try:
        with open(BLOG_LIST_FILE, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        main_section = soup.find('main')
        if not main_section: return
        article = soup.new_tag('article', **{'class': 'group border-t border-slate-200 pt-8 mt-8'})
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
        main_section.insert(0, article)
        with open(BLOG_LIST_FILE, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        print("博客列表更新成功！")
    except Exception as e:
        print(f"更新 blog.html 时发生错误: {e}")

# --- 主函数 (Prompt已更新) ---
def generate_blog_post():
    print("开始博客生成流程...")
    today_keywords = random.sample(KEYWORDS, 2)
    
    # --- 这是关键：Prompt中增加了关于超链接的指令 ---
    prompt = f"""
    You are a sleep science writer for WakeWell.online.
    Write a blog post about "{today_keywords[0]}" and "{today_keywords[1]}".

    **IMPORTANT INSTRUCTIONS:**
    1.  Your response MUST BE ONLY the raw HTML content for the article body, starting DIRECTLY with the `<h1>` tag.
    2.  Do NOT include any introductory text, conversation, or markdown fences (```html).
    3.  **NEW:** Where appropriate in the article, naturally integrate a prominent link to our main tool, the Sleep Calculator. Use this exact HTML for the link: `<a href="../index.html" class="text-sky-500 hover:underline">Sleep Calculator</a>`.
    4.  Use these exact Tailwind CSS classes for other elements:
        - Title: `<h1 class="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight">`
        - Section Headers: `<h2 class="text-3xl font-bold text-slate-900 mt-12">`
        - Paragraphs: `<p class="text-slate-600 leading-relaxed mt-4">`
    5.  The first paragraph after the `<h1>` title will be the meta description.
    """

    try:
        print("正在调用 Gemini API...")
        response = model.generate_content(prompt)
        if not response.text:
            print("错误: Gemini API 未返回有效内容。")
            return

        print("清理并解析AI输出...")
        article_content_html = clean_llm_output(response.text)
        
        post_soup = BeautifulSoup(article_content_html, 'html.parser')
        title_tag = post_soup.find('h1')
        description_tag = title_tag.find_next_sibling('p') if title_tag else None

        if not title_tag or not description_tag:
            print("错误: 生成的内容格式不正确。")
            return
            
        title = title_tag.get_text(strip=True)
        description = description_tag.get_text(strip=True)
        
        print("正在填充页面模板...")
        slug = title.lower().replace(' ', '-').replace(':', '').replace('?', '').replace("'", "")
        file_name = f"{datetime.now().strftime('%Y-%m-%d')}-{slug[:40]}.html"
        
        final_html = HTML_TEMPLATE
        final_html = final_html.replace("__PAGE_TITLE__", title)
        final_html = final_html.replace("__META_DESCRIPTION__", description)
        final_html = final_html.replace("__CANONICAL_URL__", f"{BASE_URL}/blog-post/{file_name}")
        
        # 动态插入发布日期
        published_date_html = f'<p class="mt-4 text-lg text-slate-600">Published on {datetime.now().strftime("%B %d, %Y")}</p>'
        # 将生成的文章正文（包含标题）和动态生成的日期组合起来
        full_article_content = f'{title_tag.prettify()}{published_date_html}{"".join(str(tag) for tag in title_tag.find_next_siblings())}'
        final_html = final_html.replace("__ARTICLE_CONTENT__", full_article_content)

        file_path = os.path.join(BLOG_POST_DIR, file_name)
        os.makedirs(BLOG_POST_DIR, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(final_html)
        
        print(f"成功！完整HTML页面已保存到: {file_path}")
        update_blog_list(file_name, title, description)

    except Exception as e:
        print(f"执行过程中发生错误: {e}")

if __name__ == "__main__":
    generate_blog_post()
