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
            
            # 简单建议
            title_len = len(title)
            desc_len = len(desc)
            st.success("审计完成！")
            st.markdown(f"### 📊 当前状态")
            st.write(f"标题：{title} (长度: {title_len}字，理想50-60)")
            st.write(f"描述：{desc} (长度: {desc_len}字，理想150-160)")
            
            suggestions = []
            if title_len < 50:
                suggestions.append("标题太短：加关键词如'蒙特利尔中餐馆'提升点击。")
            if desc_len < 150:
                suggestions.append("描述太短：加意图词如'正宗宫保鸡丁推荐'。")
            if not re.search(r'2025|蒙特利尔', title.lower()):
                suggestions.append("缺少本地/时效关键词：加'2025 Montreal SEO'匹配AI搜索。")
            
            st.markdown("### 💡 优化建议 (E-E-A-T + 意图)")
            for sug in suggestions:
                st.write(f"- {sug}")
            
            st.download_button("💾 下载报告", data=f"标题: {title}\n描述: {desc}\n建议: {suggestions}", file_name="seo_report.txt")
        except Exception as e:
            st.error(f"抓取失败：{str(e)}。检查URL。")

with tab2:
    text = st.text_area("输入内容（e.g., 产品描述）", height=150)
    if st.button("🚀 审计内容", type="primary") and text:
        # 关键词分析
        words = word_tokenize(text.lower())
        filtered_words = [w for w in words if len(w) > 3 and w.isalpha()]
        freq = FreqDist(filtered_words)
        top_keywords = freq.most_common(5)
        
        # 简单意图得分 (0-10: 关键词密度 + 问题词 + 来源)
        keyword_density = len(set([k[0] for k in top_keywords])) / len(set(filtered_words)) * 10 if filtered_words else 0
        has_question = bool(re.search(r'为什么|如何|什么|最佳', text))
        has_source = bool(re.search(r'根据|来源|数据', text))
        intent_score = int((keyword_density + (5 if has_question else 0) + (3 if has_source else 0)) / 1.8)  # 简化10分制
        
        st.success("审计完成！")
        st.markdown("### 📊 关键词Top5")
        for kw, count in top_keywords:
            st.write(f"- {kw}: {count}次 (密度: {count/len(filtered_words)*100:.1f}%)")
        
        st.markdown("### 📈 意图匹配得分")
        st.metric("总分 (0-10)", intent_score, delta=None)
        st.write(f"分解：关键词密度 {keyword_density:.1f}/5 | 问题导向 {5 if has_question else 0}/3 | 来源权威 {3 if has_source else 0}/2")
        
        suggestions = [
            "加问题句如'为什么选这家蒙特利尔中餐馆？'提升意图匹配。",
            "融入来源如'根据Yelp 2025数据'，加强E-E-A-T。",
            "目标密度：主关键词2-3%，长尾1%（AI Overviews友好）。"
        ]
        st.markdown("### 💡 优化建议")
        for sug in suggestions:
            st.write(f"- {sug}")
        
        st.download_button("💾 下载报告", data=f"关键词: {top_keywords}\n得分: {intent_score}\n建议: {suggestions}", file_name="seo_content_report.txt")

st.sidebar.info("基于2025趋势：AI意图 + E-E-A-T | 扩展：加Semrush API。")
