import streamlit as st
import requests
from bs4 import BeautifulSoup
import nltk
from nltk import word_tokenize, FreqDist
from collections import Counter
import re

# 下载NLTK数据（首次跑）
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

st.set_page_config(page_title="SEO Auditor", page_icon="🔍")
st.title("🔍 2025 SEO优化工具 | Simple SEO Auditor")
st.write("输入URL或内容，AI帮您审计关键词、meta和意图匹配！基于最新趋势（AI Overviews + E-E-A-T）。")

tab1, tab2 = st.tabs(["URL审计", "内容审计"])

with tab1:
    url = st.text_input("输入网站URL（e.g., your-site.com）")
    if st.button("🚀 审计URL", type="primary") and url:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.find('title').text if soup.find('title') else "无标题"
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            desc = meta_desc['content'] if meta_desc else "无描述"
            
            # 简单关键词提取（标题/描述）
            title_words = re.findall(r'\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b', title)
            desc_words = re.findall(r'\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b', desc)
            site_keywords = list(set(title_words + desc_words))[:3]  # Top3关键词
            
            # 长度检查
            title_len = len(title)
            desc_len = len(desc)
            
            st.success("审计完成！")
            st.markdown("### 📊 当前状态")
            st.write(f"标题：{title} (长度: {title_len}字，理想50-60)")
            st.write(f"描述：{desc} (长度: {desc_len}字，理想150-160)")
            
            # 动态建议（基于关键词，避免垃圾示例）
            suggestions = []
            if title_len < 50:
                kw_example = site_keywords[0] if site_keywords else "核心关键词"
                suggestions.append(f"标题太短：加关键词如'{kw_example} Montreal 2025'提升点击。")
            if desc_len < 150:
                kw_example = site_keywords[0] if site_keywords else "意图词"
                suggestions.append(f"描述太短：加意图词如'最佳{ kw_example }推荐'。")
            if not any(word in title.lower() for word in ['2025', 'montreal', 'ai']):
                suggestions.append("缺少本地/时效关键词：加'2025 Montreal SEO'匹配AI Overviews。")
            if "payhip.com" in url.lower():
                suggestions.append("Payhip专属：加自定义meta + schema markup，提升产品snippet。")
            
            st.markdown("### 💡 优化建议 (E-E-A-T + 意图)")
            for sug in suggestions:
                st.write(f"- {sug}")
            
            st.download_button("💾 下载报告", data=f"标题: {title}\n描述: {desc}\n关键词: {site_keywords}\n建议: {suggestions}", file_name="seo_url_report.txt")
        except Exception as e:
            st.error(f"抓取失败：{str(e)}。检查URL或Cloudflare挡住（试加User-Agent）。")

with tab2:
    text = st.text_area("输入内容（e.g., 产品描述）", height=150)
    if st.button("🚀 审计内容", type="primary") and text:
        # 关键词分析
        words = word_tokenize(text.lower())
        filtered_words = [w for w in words if len(w) > 3 and w.isalpha()]
        freq = FreqDist(filtered_words)
        top_keywords = freq.most_common(5)
        
        # 意图得分 (0-10: 密度 + 问题词 + 来源)
        keyword_density = len(set([k[0] for k in top_keywords])) / len(set(filtered_words)) * 5 if filtered_words else 0
        has_question = bool(re.search(r'为什么|如何|什么|最佳|recommend|how|why', text, re.IGNORECASE))
        has_source = bool(re.search(r'根据|来源|data|according|source', text, re.IGNORECASE))
        intent_score = int(keyword_density + (3 if has_question else 0) + (2 if has_source else 0))
        intent_score = min(10, intent_score)  # 封顶10
        
        st.success("审计完成！")
        st.markdown("### 📊 关键词Top5")
        for kw, count in top_keywords:
            st.write(f"- {kw}: {count}次 (密度: {count/len(filtered_words)*100:.1f}%)")
        
        st.markdown("### 📈 意图匹配得分")
        st.metric("总分 (0-10)", intent_score, delta=None)
        st.write(f"分解：关键词密度 {keyword_density:.1f}/5 | 问题导向 {3 if has_question else 0}/3 | 来源权威 {2 if has_source else 0}/2")
        
        # 动态建议
        suggestions = [
            f"加问题句如'为什么选{top_keywords[0][0]}？'提升意图匹配。",
            "融入来源如'根据Yelp 2025数据'，加强E-E-A-T。",
            f"目标密度：主关键词'{top_keywords[0][0]}' 2-3%，长尾1%（AI Overviews友好）。"
        ]
        st.markdown("### 💡 优化建议")
        for sug in suggestions:
            st.write(f"- {sug}")
        
        st.download_button("💾 下载报告", data=f"关键词: {top_keywords}\n得分: {intent_score}\n建议: {suggestions}", file_name="seo_content_report.txt")

st.sidebar.info("基于2025趋势：AI意图 + E-E-A-T | 扩展：加Semrush API。")
