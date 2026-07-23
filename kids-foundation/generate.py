#!/usr/bin/env python3
"""
Generate Kids Foundation course HTML files from structured JSON data.
Each lesson is a self-contained HTML file with embedded CSS/JS.
Supports 4 Bible translations: CUV, CCB, CSB, ESV.
"""

import json
import os

# ---- Configuration ----
OUTPUT_DIR = "/Users/andyshengruilee/Downloads/AI协同工作区/真道之工/建立根基_Kids课程讲义/kids-foundation"
DATA_DIR = os.path.join(OUTPUT_DIR, "data")
ANSWERS_DIR = os.path.join(DATA_DIR, "answers")

THEME_COLORS = {
    "福音": {"primary": "#f5576c", "secondary": "#f093fb", "icon": "✝️"},
    "主权": {"primary": "#4facfe", "secondary": "#00f2fe", "icon": "👑"},
    "悔改": {"primary": "#43e97b", "secondary": "#38f9d7", "icon": "🔄"},
    "灵修": {"primary": "#fa709a", "secondary": "#fee140", "icon": "📖"},
    "圣灵": {"primary": "#a18cd1", "secondary": "#fbc2eb", "icon": "🕊️"},
    "宣教与使命": {"primary": "#d57eeb", "secondary": "#fccb90", "icon": "🌍"},
    "门徒与带领": {"primary": "#667eea", "secondary": "#764ba2", "icon": "🎯"},
    "属灵家庭和教会生活": {"primary": "#f7971e", "secondary": "#ffd200", "icon": "🏠"},
}


def generate_css(primary_color, secondary_color):
    return f"""    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
            min-height: 100vh; padding: 20px;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        header {{
            background: white; border-radius: 15px 15px 0 0; padding: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        .breadcrumb {{ color: #888; font-size: 0.9em; margin-bottom: 10px; }}
        .breadcrumb a {{ color: {primary_color}; text-decoration: none; }}
        .breadcrumb a:hover {{ text-decoration: underline; }}
        h1 {{ color: #333; margin-bottom: 10px; font-size: 2em; }}
        .section-title-box {{ display: inline-flex; align-items: center; gap: 15px; margin-top: 10px; }}
        .section-label {{
            display: inline-block; border: 2px solid #333; padding: 6px 16px;
            font-size: 1em; font-weight: 500; color: #333;
        }}
        .section-name {{ font-size: 1.2em; color: #333; font-weight: 500; }}

        /* Translation selector */
        .translation-bar {{
            background: #f8f9fa; padding: 12px 40px; display: flex; align-items: center; gap: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05); flex-wrap: wrap;
        }}
        .translation-bar label {{ font-weight: 600; color: #555; font-size: 0.9em; }}
        .translation-btn {{
            padding: 6px 14px; border: 2px solid #ddd; border-radius: 20px; background: white;
            cursor: pointer; font-size: 0.85em; transition: all 0.2s; color: #666;
        }}
        .translation-btn:hover {{ border-color: {primary_color}; color: {primary_color}; }}
        .translation-btn.active {{
            background: {primary_color}; color: white; border-color: {primary_color};
        }}

        .content {{ background: white; padding: 40px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }}
        .teaching-text {{
            background: #fef9e7; border-left: 4px solid #f39c12; padding: 15px 20px;
            border-radius: 0 8px 8px 0; margin-bottom: 25px; color: #555; line-height: 1.8; font-size: 0.95em;
        }}
        .bible-reading {{
            background: #eaf2f8; border-left: 4px solid #2980b9; padding: 12px 20px;
            border-radius: 0 8px 8px 0; margin-bottom: 20px; font-size: 0.95em;
        }}
        .bible-reading strong {{ color: #2980b9; }}

        .question-block {{ margin-bottom: 30px; }}
        .question-header {{ margin-bottom: 12px; display: flex; align-items: flex-start; }}
        .question-number {{ flex-shrink: 0; margin-right: 10px; color: #333; font-size: 1em; font-weight: 600; }}
        .question-text {{ font-size: 1em; color: #333; line-height: 1.6; }}

        .answers-area {{ margin-left: 25px; }}
        .reference-with-blank {{ margin-bottom: 20px; }}
        .reference-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px; }}
        .reference-text {{ color: {primary_color}; font-size: 0.95em; font-weight: 500; }}
        .hint-buttons {{ display: flex; gap: 6px; }}
        .btn-hint-partial, .btn-hint-full {{
            padding: 4px 10px; border: none; border-radius: 5px; font-size: 0.8em;
            cursor: pointer; transition: all 0.2s; color: white;
        }}
        .btn-hint-partial {{ background: #f39c12; }}
        .btn-hint-partial:hover {{ transform: translateY(-1px); box-shadow: 0 3px 10px rgba(243,156,24,0.3); }}
        .btn-hint-full {{ background: {primary_color}; }}
        .btn-hint-full:hover {{ transform: translateY(-1px); box-shadow: 0 3px 10px rgba(0,0,0,0.2); }}

        .answer-input {{
            width: 100%; border: 2px solid #ddd; border-radius: 8px; padding: 12px;
            font-size: 1em; font-family: inherit; resize: vertical; outline: none;
            transition: all 0.3s; line-height: 1.6;
        }}
        .answer-input:focus {{ border-color: {primary_color}; box-shadow: 0 0 0 3px rgba(0,0,0,0.05); }}
        .answer-input.correct {{ border-color: #27ae60; background: rgba(39,174,96,0.05); }}
        .answer-input.incorrect {{ border-color: #e74c3c; background: rgba(231,76,60,0.05); }}
        .answer-input.partial {{ border-color: #f39c12; background: rgba(243,156,18,0.05); }}

        .answer-feedback {{ margin-top: 8px; padding: 8px 12px; border-radius: 5px; font-size: 0.9em; display: none; }}
        .answer-feedback.show {{ display: block; }}
        .answer-feedback.correct {{ background: #d4edda; color: #155724; border-left: 4px solid #27ae60; }}
        .answer-feedback.incorrect {{ background: #f8d7da; color: #721c24; border-left: 4px solid #e74c3c; }}
        .answer-feedback.partial {{ background: #fff3cd; color: #856404; border-left: 4px solid #f39c12; }}

        .standard-answer {{
            display: none; margin-top: 10px; padding: 15px;
            background: #f8f9fa; border-left: 4px solid {primary_color};
            border-radius: 0 5px 5px 0; font-size: 0.95em; color: #555; line-height: 1.6;
        }}
        .standard-answer.show {{ display: block; }}

        /* Verse display box */
        .verse-display {{
            margin-top: 10px; padding: 12px 15px; background: #f0f4ff;
            border-radius: 8px; font-size: 0.9em; line-height: 1.7; display: none;
        }}
        .verse-display.show {{ display: block; }}
        .verse-display .verse-label {{
            font-weight: 600; color: {primary_color}; margin-bottom: 5px; font-size: 0.85em;
        }}
        .verse-display .verse-text {{ color: #444; }}

        .application-section {{
            margin-top: 35px; padding: 25px; background: #f8f9fa; border-radius: 8px;
        }}
        .application-section h3 {{ color: #333; margin-bottom: 10px; font-size: 1.1em; }}
        .application-prompt {{ color: #666; margin-bottom: 15px; line-height: 1.6; font-size: 0.95em; }}
        .application-input {{
            width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px;
            font-size: 1em; font-family: inherit; resize: vertical; min-height: 100px;
        }}
        .application-input:focus {{ outline: none; border-color: {primary_color}; }}

        .action-bar {{
            background: white; padding: 20px 40px; border-radius: 0 0 15px 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1); display: flex;
            justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;
        }}
        .score-display {{ font-size: 1.1em; color: #333; font-weight: 500; }}
        .score-number {{ color: {primary_color}; font-size: 1.4em; font-weight: bold; }}
        .btn {{
            padding: 12px 25px; border: none; border-radius: 8px; font-size: 1em;
            cursor: pointer; transition: all 0.3s; font-weight: 500; color: white;
        }}
        .btn-check {{ background: {primary_color}; }}
        .btn-check:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }}
        .btn-submit {{ background: #27ae60; }}
        .btn-submit:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(39,174,96,0.4); }}

        .navigation {{
            background: white; padding: 20px 40px; margin-top: 20px; border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1); display: flex; justify-content: space-between; gap: 15px;
        }}
        .nav-btn {{
            padding: 12px 25px; border-radius: 8px; text-decoration: none;
            transition: all 0.3s; font-weight: 500; background: {primary_color}; color: white;
        }}
        .nav-btn:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }}
        .home-btn {{ background: #f5f5f5; color: #333; }}
        .home-btn:hover {{ background: #e0e0e0; }}

        .toast {{
            position: fixed; top: 20px; right: 20px; background: white; padding: 15px 25px;
            border-radius: 8px; box-shadow: 0 5px 20px rgba(0,0,0,0.2); display: none;
            z-index: 1000; max-width: 300px;
        }}
        .toast.show {{ display: block; animation: slideIn 0.3s ease; }}
        @keyframes slideIn {{ from {{ transform: translateX(400px); }} to {{ transform: translateX(0); }} }}

        .score-modal {{
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.7); display: none; align-items: center;
            justify-content: center; z-index: 2000;
        }}
        .score-modal.show {{ display: flex; }}
        .score-modal-content {{
            background: white; padding: 40px; border-radius: 15px; text-align: center;
            max-width: 400px; animation: scaleIn 0.3s ease;
        }}
        @keyframes scaleIn {{ from {{ transform: scale(0.7); opacity: 0; }} to {{ transform: scale(1); opacity: 1; }} }}
        .score-modal-content h2 {{ color: #333; margin-bottom: 20px; }}
        .final-score {{ font-size: 4em; color: {primary_color}; font-weight: bold; margin: 20px 0; }}
        .score-message {{ font-size: 1.2em; color: #666; margin-bottom: 30px; }}
        .score-details {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: left; }}
        .score-details p {{ margin: 8px 0; color: #555; }}
        .btn-close-modal {{
            background: {primary_color}; color: white; padding: 12px 30px;
            border: none; border-radius: 8px; font-size: 1em; cursor: pointer; font-weight: 500;
        }}

        @media (max-width: 768px) {{
            body {{ padding: 10px; }}
            header, .content, .action-bar, .translation-bar {{ padding: 20px; }}
            h1 {{ font-size: 1.5em; }}
            .navigation {{ flex-direction: column; padding: 15px; }}
            .nav-btn {{ width: 100%; text-align: center; }}
            .action-bar {{ flex-direction: column; text-align: center; }}
        }}
    </style>"""


def generate_js(lesson_id, prev_page, next_page):
    """Generate the JavaScript block for a lesson page."""
    return f"""    <script>
        let standardAnswers = {{}};
        let currentTranslation = 'cuv';
        const translations = {{
            'cuv': '和合本',
            'ccb': '当代译本',
            'csb': '标准译本',
            'esv': 'ESV'
        }};

        window.addEventListener('load', () => {{
            loadStandardAnswers();
            loadProgress();
            updateProgress();
            // Restore translation preference
            const savedTrans = localStorage.getItem('kidsBibleTranslation');
            if (savedTrans && translations[savedTrans]) {{
                setTranslation(savedTrans);
            }}
        }});

        document.querySelectorAll('.answer-input, .application-input').forEach(input => {{
            input.addEventListener('input', () => updateProgress());
        }});

        async function loadStandardAnswers() {{
            try {{
                const response = await fetch('data/answers/{lesson_id}.json');
                if (!response.ok) {{ console.warn('未找到答案数据文件'); return; }}
                const answerData = await response.json();
                standardAnswers = answerData.answers || {{}};
                console.log('标准答案已加载:', Object.keys(standardAnswers).length, '个');
            }} catch (e) {{ console.error('加载标准答案失败:', e); }}
        }}

        function setTranslation(trans) {{
            currentTranslation = trans;
            localStorage.setItem('kidsBibleTranslation', trans);
            // Update button states
            document.querySelectorAll('.translation-btn').forEach(btn => {{
                btn.classList.toggle('active', btn.dataset.trans === trans);
            }});
            // Update verse displays if any are open
            document.querySelectorAll('.verse-display.show').forEach(div => {{
                const ref = div.dataset.ref;
                showVerseDisplay(ref);
            }});
        }}

        function getVerseText(ref, trans) {{
            // Find the answer entry for this reference
            let answerEntry = null;
            for (const k of Object.keys(standardAnswers)) {{
                if (k.endsWith('_' + ref) && standardAnswers[k].has_data) {{
                    answerEntry = standardAnswers[k];
                    break;
                }}
            }}
            if (!answerEntry) return null;

            // Return the text for the requested translation
            if (trans === 'ccb' && answerEntry.has_ccb) return answerEntry.ccb;
            if (trans === 'csb' && answerEntry.has_csb) return answerEntry.csb;
            if (trans === 'esv' && answerEntry.has_esv) return answerEntry.esv;
            // Fallback to CUV (default text)
            if (trans === 'cuv') return answerEntry.text;
            // For any other translation, try its field or fallback
            if (answerEntry[trans]) return answerEntry[trans];
            return answerEntry.text; // Ultimate fallback to CUV
        }}

        function showVerseDisplay(ref) {{
            const div = document.querySelector(`.verse-display[data-ref="${{ref}}"]`);
            if (!div) return;
            const text = getVerseText(ref, currentTranslation);
            const isFallback = (currentTranslation !== 'cuv') && !(function(){{
                for (const k of Object.keys(standardAnswers)) {{
                    if (k.endsWith('_' + ref) && standardAnswers[k].has_data) {{
                        const e = standardAnswers[k];
                        if (currentTranslation === 'ccb' && e.has_ccb) return true;
                        if (currentTranslation === 'csb' && e.has_csb) return true;
                        if (currentTranslation === 'esv' && e.has_esv) return true;
                    }}
                }}
                return false;
            }})();
            const transLabel = translations[currentTranslation];
            const fallbackNote = (isFallback || !text) ? '' : '';
            if (!text) {{
                div.innerHTML = `<div class="verse-label">${{ref}} (${{transLabel}})</div><div class="verse-text" style="color:#999;">暂无经文数据</div>`;
            }} else {{
                const note = (currentTranslation !== 'cuv' && text === getVerseText(ref, 'cuv')) ?
                    ' <span style="font-size:0.75em;color:#999;">(回退到和合本)</span>' : '';
                div.innerHTML = `<div class="verse-label">${{ref}} (${{transLabel}})${{note}}</div><div class="verse-text">${{text}}</div>`;
            }}
            div.classList.add('show');
        }}

        function toggleVerse(ref) {{
            const div = document.querySelector(`.verse-display[data-ref="${{ref}}"]`);
            if (!div) return;
            if (div.classList.contains('show')) {{
                div.classList.remove('show');
            }} else {{
                showVerseDisplay(ref);
            }}
        }}

        function showFullHint(questionId, ref) {{
            const answerKey = `q${{questionId}}_${{ref}}`;
            const answerInfo = standardAnswers[answerKey];
            if (!answerInfo || !answerInfo.has_data) {{
                showToast('暂无答案数据');
                return;
            }}
            const standardAnswerDiv = document.querySelector(`.standard-answer[data-ref="${{ref}}"]`);
            if (standardAnswerDiv) {{
                if (standardAnswerDiv.classList.contains('show')) {{
                    standardAnswerDiv.classList.remove('show');
                }} else {{
                    standardAnswerDiv.innerHTML = `<strong>📖 标准答案:</strong> ${{answerInfo.text}}`;
                    standardAnswerDiv.classList.add('show');
                }}
            }}
        }}

        function showPartialHint(questionId, ref) {{
            const answerKey = `q${{questionId}}_${{ref}}`;
            const answerInfo = standardAnswers[answerKey];
            if (!answerInfo || !answerInfo.has_data) {{
                showToast('暂无答案数据');
                return;
            }}
            const input = document.querySelector(`textarea[data-question="${{questionId}}"][data-reference="${{ref}}"]`);
            if (!input) return;
            const standardText = answerInfo.text;
            const currentProgress = parseInt(input.dataset.hintProgress || '0');
            const fillPercentage = Math.min(currentProgress + 20, 100);
            const fillLength = Math.floor((standardText.length * fillPercentage) / 100);
            input.value = standardText.substring(0, fillLength);
            input.dataset.hintProgress = fillPercentage;
            if (fillPercentage >= 100) {{ showToast('💡 答案已全部填充'); }}
            else {{ showToast(`💡 已填充 ${{fillPercentage}}% 的答案`); }}
            updateProgress();
        }}

        async function checkAnswers() {{
            await loadStandardAnswers();
            let totalAnswerableQuestions = 0, correctCount = 0, incorrectInputs = [];
            document.querySelectorAll('.answer-input').forEach(input => {{
                const ref = input.dataset.reference;
                const hasAnswer = input.dataset.hasAnswer === 'true';
                if (!ref || !hasAnswer) return;
                const questionId = input.dataset.question;
                const answerKey = `q${{questionId}}_${{ref}}`;
                const answerInfo = standardAnswers[answerKey];
                if (!answerInfo || !answerInfo.has_data) return;
                totalAnswerableQuestions++;
                const userAnswer = input.value.trim();
                const standardAnswer = answerInfo.text || '';
                input.classList.remove('correct', 'incorrect', 'partial');
                const feedbackDiv = input.parentElement.querySelector('.answer-feedback');
                if (userAnswer === '') {{
                    input.classList.add('incorrect');
                    if (feedbackDiv) {{ feedbackDiv.textContent = '✗ 请填写答案'; feedbackDiv.className = 'answer-feedback incorrect show'; }}
                    incorrectInputs.push(input);
                }} else {{
                    const similarity = calculateSimilarity(userAnswer, standardAnswer);
                    if (similarity >= 0.85) {{
                        input.classList.add('correct');
                        if (feedbackDiv) {{ feedbackDiv.textContent = '✓ 正确！'; feedbackDiv.className = 'answer-feedback correct show'; }}
                        correctCount++;
                    }} else if (similarity >= 0.6) {{
                        input.classList.add('partial');
                        if (feedbackDiv) {{ feedbackDiv.textContent = '△ 部分正确，请对照标准答案修改'; feedbackDiv.className = 'answer-feedback partial show'; }}
                        incorrectInputs.push(input);
                    }} else {{
                        input.classList.add('incorrect');
                        if (feedbackDiv) {{ feedbackDiv.textContent = '✗ 不正确，请对照标准答案修改'; feedbackDiv.className = 'answer-feedback incorrect show'; }}
                        incorrectInputs.push(input);
                    }}
                }}
            }});
            if (incorrectInputs.length > 0) {{
                incorrectInputs[0].scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                setTimeout(() => incorrectInputs[0].focus(), 500);
                showToast(`❌ 发现 ${{incorrectInputs.length}} 个错误，已定位到第一个错误`);
            }} else if (correctCount === totalAnswerableQuestions && totalAnswerableQuestions > 0) {{
                showToast('🎉 所有答案都正确！');
            }} else {{
                showToast(`✓ 检查完成 - ${{correctCount}}/${{totalAnswerableQuestions}} 正确`);
            }}
        }}

        async function submitAnswers() {{
            await loadStandardAnswers();
            const questionStats = {{}};
            let totalInputs = 0, correctInputs = 0, partialInputs = 0, incorrectInputs = 0;
            document.querySelectorAll('.answer-input').forEach(input => {{
                const ref = input.dataset.reference;
                const hasAnswer = input.dataset.hasAnswer === 'true';
                if (!ref || !hasAnswer) return;
                const questionId = input.dataset.question;
                const answerKey = `q${{questionId}}_${{ref}}`;
                const answerInfo = standardAnswers[answerKey];
                if (!answerInfo || !answerInfo.has_data) return;
                totalInputs++;
                if (!questionStats[questionId]) questionStats[questionId] = {{ total: 0, correct: 0, partial: 0, incorrect: 0 }};
                questionStats[questionId].total++;
                const similarity = calculateSimilarity(input.value.trim(), answerInfo.text || '');
                if (similarity >= 0.85) {{ correctInputs++; questionStats[questionId].correct++; }}
                else if (similarity >= 0.6) {{ partialInputs++; questionStats[questionId].partial++; }}
                else {{ incorrectInputs++; questionStats[questionId].incorrect++; }}
            }});
            let totalQuestions = Object.keys(questionStats).length, qCorrect = 0, qPartial = 0, qIncorrect = 0;
            Object.values(questionStats).forEach(stats => {{
                const accuracy = stats.total > 0 ? stats.correct / stats.total : 0;
                if (accuracy >= 0.8) qCorrect++;
                else if (accuracy >= 0.4) qPartial++;
                else qIncorrect++;
            }});
            const score = totalInputs > 0 ? Math.round(((correctInputs + partialInputs * 0.6) / totalInputs) * 100) : 0;
            document.getElementById('finalScore').textContent = score + '分';
            const msgEl = document.getElementById('scoreMessage');
            if (totalInputs === 0) msgEl.textContent = '本节暂无可评分的题目';
            else if (score >= 90) msgEl.textContent = '🌟 优秀！你掌握得非常好！';
            else if (score >= 75) msgEl.textContent = '👍 良好！继续加油！';
            else if (score >= 60) msgEl.textContent = '📚 及格！建议再复习一下';
            else msgEl.textContent = '💪 继续努力！多读几遍经文吧';
            document.getElementById('scoreDetails').innerHTML = `
                <p>📊 总题数: ${{totalQuestions}} 题 | 总答案框: ${{totalInputs}} 个</p>
                <p>📋 问题统计: ✅${{qCorrect}} ⚠️${{qPartial}} ❌${{qIncorrect}}</p>
                <p>📝 答案框: ✅${{correctInputs}} ⚠️${{partialInputs}} ❌${{incorrectInputs}}</p>
            `;
            document.getElementById('scoreModal').classList.add('show');
            saveProgress();
        }}

        function closeScoreModal() {{ document.getElementById('scoreModal').classList.remove('show'); }}

        function calculateSimilarity(text1, text2) {{
            const clean1 = text1.replace(/[\\s\\.,;:!?，。；：！？、""''（）【】《》]/g, '');
            const clean2 = text2.replace(/[\\s\\.,;:!?，。；：！？、""''（）【】《》]/g, '');
            if (!clean1 || !clean2) return 0;
            const dp = Array(clean1.length + 1).fill(null).map(() => Array(clean2.length + 1).fill(0));
            for (let i = 1; i <= clean1.length; i++)
                for (let j = 1; j <= clean2.length; j++)
                    dp[i][j] = clean1[i-1] === clean2[j-1] ? dp[i-1][j-1] + 1 : Math.max(dp[i-1][j], dp[i][j-1]);
            return dp[clean1.length][clean2.length] / Math.max(clean1.length, clean2.length);
        }}

        function loadProgress() {{
            const saved = localStorage.getItem('{lesson_id}');
            if (saved) {{
                try {{
                    const data = JSON.parse(saved);
                    document.querySelectorAll('.answer-input').forEach(input => {{
                        const q = input.dataset.question;
                        const ref = input.dataset.reference || 'main';
                        const savedAnswer = data.answers?.[`q${{q}}_${{ref}}`];
                        if (savedAnswer) input.value = savedAnswer;
                    }});
                    const appInput = document.querySelector('.application-input');
                    if (appInput && data.application) appInput.value = data.application;
                }} catch (e) {{}}
            }}
        }}

        function saveProgress() {{
            const data = {{ answers: {{}}, application: '', timestamp: new Date().toISOString() }};
            document.querySelectorAll('.answer-input').forEach(input => {{
                const q = input.dataset.question;
                const ref = input.dataset.reference || 'main';
                data.answers[`q${{q}}_${{ref}}`] = input.value;
            }});
            const appInput = document.querySelector('.application-input');
            if (appInput) data.application = appInput.value;
            localStorage.setItem('{lesson_id}', JSON.stringify(data));
            showToast('✓ 进度已保存');
        }}

        function updateProgress() {{
            let totalFields = 0, filledFields = 0;
            document.querySelectorAll('.answer-input').forEach(input => {{
                totalFields++; if (input.value.trim()) filledFields++;
            }});
            const appInput = document.querySelector('.application-input');
            if (appInput) {{ totalFields++; if (appInput.value.trim()) filledFields++; }}
            document.getElementById('progressDisplay').textContent = (totalFields > 0 ? Math.round((filledFields / totalFields) * 100) : 0) + '%';
        }}

        function showToast(message) {{
            const toast = document.getElementById('toast');
            toast.textContent = message; toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 3000);
        }}
    </script>"""


def generate_question_html(q, with_ref=True):
    """Generate HTML for a single question."""
    qid = q["id"]
    question_text = q["question"]
    refs = q.get("references", [])

    html = f'''
            <div class="question-block" data-question-id="{qid}">
                <div class="question-header">
                    <span class="question-number">{qid}.</span>
                    <span class="question-text">{question_text}</span>
                </div>
                <div class="answers-area">'''

    if refs and with_ref:
        for ref in refs:
            ref_clean = ref.replace(" ", "_").replace(",", "_").replace(":", "_")
            html += f'''
                    <div class="reference-with-blank">
                        <div class="reference-header">
                            <span class="reference-text">{ref}</span>
                            <div class="hint-buttons">
                                <button class="btn-hint-partial" onclick="showPartialHint('{qid}', '{ref}')" title="渐进提示">💡 提示</button>
                                <button class="btn-hint-full" onclick="showFullHint('{qid}', '{ref}')" title="显示完整答案">👁️ 答案</button>
                                <button class="btn-hint-full" onclick="toggleVerse('{ref}')" title="查看经文" style="background:#8e44ad;">📖 经文</button>
                            </div>
                        </div>
                        <textarea class="answer-input" data-question="{qid}" data-reference="{ref}" data-has-answer="true"
                               data-hint-progress="0"
                               placeholder="请填写经文内容..."></textarea>
                        <div class="answer-feedback" data-ref="{ref}"></div>
                        <div class="standard-answer" data-ref="{ref}"></div>
                        <div class="verse-display" data-ref="{ref}"></div>
                    </div>'''
    else:
        # Open-ended question without specific reference
        html += f'''
                    <div class="reference-with-blank">
                        <textarea class="answer-input full-width"
                               rows="3"
                               data-question="{qid}"
                               placeholder="请写下你的答案..."></textarea>
                    </div>'''

    html += '''
                </div>
            </div>'''
    return html


def generate_lesson_html(lesson_data):
    """Generate a complete lesson HTML file."""
    theme = lesson_data["theme"]
    lesson_num = lesson_data["lesson_num"]
    title = lesson_data["title"]
    lesson_id = lesson_data["id"]
    colors = THEME_COLORS.get(theme, {"primary": "#667eea", "secondary": "#764ba2"})

    prev_page = lesson_data.get("prev", "")
    next_page = lesson_data.get("next", "")
    prev_label = lesson_data.get("prev_label", "上一课")
    next_label = lesson_data.get("next_label", "下一课")

    css = generate_css(colors["primary"], colors["secondary"])
    js = generate_js(lesson_id, prev_page, next_page)

    # Build navigation HTML
    nav_html = '<div class="navigation">'
    if prev_page:
        nav_html += f'<a href="{prev_page}" class="nav-btn">← {prev_label}</a>'
    else:
        nav_html += '<div></div>'
    nav_html += f'<a href="index.html" class="nav-btn home-btn">📚 返回目录</a>'
    if next_page:
        nav_html += f'<a href="{next_page}" class="nav-btn">{next_label}</a>'
    else:
        nav_html += '<div></div>'
    nav_html += '</div>'

    # Build translation bar
    trans_bar = '''<div class="translation-bar">
            <label>🌐 圣经译本:</label>'''
    for trans_key, trans_name in [("cuv", "和合本"), ("ccb", "当代译本"), ("csb", "标准译本"), ("esv", "ESV")]:
        active = ' active' if trans_key == 'cuv' else ''
        trans_bar += f'''
            <button class="translation-btn{active}" data-trans="{trans_key}" onclick="setTranslation('{trans_key}')">{trans_name}</button>'''
    trans_bar += '</div>'

    # Build teaching text
    teaching_html = ""
    if lesson_data.get("teaching_text"):
        teaching_html = f'<div class="teaching-text">{lesson_data["teaching_text"]}</div>'

    # Build bible reading prompts
    reading_html = ""
    if lesson_data.get("bible_readings"):
        reading_html = '<div class="bible-reading"><strong>📖 本课经文阅读:</strong><br>'
        for reading in lesson_data["bible_readings"]:
            reading_html += f'　· {reading}<br>'
        reading_html += '</div>'

    # Build questions
    questions_html = ""
    for q in lesson_data.get("questions", []):
        questions_html += generate_question_html(q)

    # Build application
    app_html = ""
    if lesson_data.get("application"):
        app = lesson_data["application"]
        app_html = f'''
            <div class="application-section">
                <h3>🤔 个人应用</h3>
                <p class="application-prompt">{app}</p>
                <textarea class="application-input"
                          placeholder="写下你的思考、感受和具体的行动计划..."
                          rows="5"></textarea>
            </div>'''

    # Assemble full HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | 建立根基 Kids</title>
{css}
</head>
<body>
    <div class="container">
        <header>
            <div class="breadcrumb">
                <a href="index.html">建立根基 Kids</a> /
                {theme} / 第{lesson_num}课
            </div>
            <h1>{title}</h1>
            <div class="section-title-box">
                <span class="section-label">第{lesson_num}课</span>
                <span class="section-name">{theme}</span>
            </div>
        </header>

{trans_bar}

        <div class="content">
{teaching_html}
{reading_html}
{questions_html}
{app_html}
        </div>

        <div class="action-bar">
            <div class="score-display">
                完成度: <span class="score-number" id="progressDisplay">0%</span>
            </div>
            <div>
                <button class="btn btn-check" onclick="checkAnswers()">✓ 检查答案</button>
                <button class="btn btn-submit" onclick="submitAnswers()">📝 提交成绩</button>
            </div>
        </div>

{nav_html}
    </div>

    <div class="toast" id="toast"></div>

    <div class="score-modal" id="scoreModal">
        <div class="score-modal-content">
            <h2>🎉 成绩报告</h2>
            <div class="final-score" id="finalScore">-</div>
            <div class="score-message" id="scoreMessage"></div>
            <div class="score-details" id="scoreDetails"></div>
            <button class="btn-close-modal" onclick="closeScoreModal()">确定</button>
        </div>
    </div>

{js}
</body>
</html>"""
    return html


# ---- Course Data ----

COURSE_DATA = [
    # ===== 福音 =====
    {
        "id": "kids_L1_S1",
        "theme": "福音",
        "lesson_num": 1,
        "title": "罪与神的命令",
        "prev": "", "prev_label": "",
        "next": "kids_L1_S2.html", "next_label": "第2课 →",
        "bible_readings": [
            "创世记 1:1 - 神创造天地",
            "创世记 2:16-17 - 神给亚当的命令",
            "创世记 3:1-13 - 亚当夏娃犯罪",
            "创世记 3:7-10 - 犯罪后的反应",
            "以弗所书 2:1 - 因罪而死的光景",
            "以赛亚书 59:1-2 - 罪使人与神隔绝",
            "耶利米书 17:9 - 罪对人心影响",
            "利未记 11:44 - 神的圣洁",
            "罗马书 7:24 - 保罗的呼喊",
            "罗马书 6:23 - 罪的工价",
        ],
        "teaching_text": "在我们身边的每件事物都有一个起源。神创造的一切都是好的。当神创造了第一个人亚当，祂说那人独居不好，所以创造了第一个女人夏娃。第一对夫妻在伊甸园中享受神所创造的一切。但亚当和夏娃违背了神的命令，吃了分别善恶树的果子，罪就进入了世界。",
        "questions": [
            {"id": 1, "question": "神给了亚当什么命令？", "references": ["创 2:16-17"]},
            {"id": 2, "question": "当你的父母给你立规矩的时候，你通常的反应是怎样的？", "references": []},
            {"id": 3, "question": "接下来发生了什么？即使夏娃和亚当知道神的命令，他们做了什么？", "references": ["创 3:1-13"]},
            {"id": 4, "question": "如果你当时在园中与蛇对话，你会怎么做？", "references": []},
            {"id": 5, "question": "当亚当和夏娃的眼睛明亮了，他们做了什么？他们的反应是怎样的？", "references": ["创 3:7-10"]},
            {"id": 6, "question": "在亚当和夏娃犯罪之后，神做了什么？", "references": ["创 3:8-9"]},
            {"id": 7, "question": "你觉得为什么亚当和夏娃会有这样的反应？", "references": []},
            {"id": 8, "question": "圣经上说，因着罪，我们会在怎样的光景中？", "references": ["弗 2:1"]},
            {"id": 9, "question": "罪对我们和神之间的关系做了什么？", "references": ["赛 59:1-2"]},
            {"id": 10, "question": "罪在我们的心上产生了什么影响？", "references": ["耶 17:9"]},
            {"id": 11, "question": "为什么我们的罪对神来说最终是那么的严重？", "references": ["利 11:44"]},
            {"id": 12, "question": "使徒保罗称呼他自己什么？", "references": ["罗 7:24"]},
            {"id": 13, "question": "罪的工价是什么？", "references": ["罗 6:23"]},
        ],
        "application": "花一些时间想想你做过的一些错事或自己所犯的罪。对于你的罪，你应得的是什么？你会像神一样那么严重地看待罪吗？",
    },
    {
        "id": "kids_L1_S2",
        "theme": "福音",
        "lesson_num": 2,
        "title": "耶稣的救赎",
        "prev": "kids_L1_S1.html", "prev_label": "← 第1课",
        "next": "kids_L2_S1.html", "next_label": "下一主题 →",
        "bible_readings": [
            "哥林多前书 15:3-4",
            "加拉太书 3:13-14",
            "约翰福音 1:18",
            "以弗所书 1:7; 2:13",
            "约翰一书 1:7",
            "彼得前书 2:24",
            "哥林多前书 15:14-19",
            "以西结书 36:26",
            "以弗所书 2:4-6",
            "约翰福音 1:12-13",
            "哥林多后书 5:17",
            "约翰一书 5:4",
            "以弗所书 2:8-9",
            "提多书 3:4-5; 2:11-12",
            "约翰福音 3:3-7",
        ],
        "teaching_text": "罪的惩罚和代价就是死，包括灵性上的和身体上的。但并不是所有的希望都破灭了！即使在亚当和夏娃的故事中，我们也找到了上帝最终解决罪的方法。上帝通过流无辜动物血的方式给他们提供了真正的遮盖。罪被赦免的唯一方式就是通过流血。好消息是：上帝的计划是献出祂终极的祭品——耶稣基督，作为\"神的羔羊\"为全人类的罪献上。",
        "questions": [
            {"id": 1, "question": "耶稣在十字架上为我们成就了什么？", "references": ["林前 15:3-4"]},
            {"id": 2, "question": "耶稣在十字架上为我们成就了什么？（续）", "references": ["加 3:13-14"]},
            {"id": 3, "question": "耶稣的什么独特性使得祂为我们的罪代赎变为可能？", "references": ["约 1:18"]},
            {"id": 4, "question": "耶稣的血为我们成就了什么？", "references": ["弗 1:7"]},
            {"id": 5, "question": "耶稣的血为我们成就了什么？（续）", "references": ["弗 2:13"]},
            {"id": 6, "question": "耶稣的血为我们成就了什么？（续）", "references": ["约一 1:7"]},
            {"id": 7, "question": "耶稣在十字架上为我们成就了什么？", "references": ["彼前 2:24"]},
            {"id": 8, "question": "耶稣的复活有什么意义？如果没有复活又会怎么样？", "references": ["林前 15:14-19"]},
            {"id": 9, "question": "关于我们的心，上帝应许说祂会做什么？", "references": ["结 36:26"]},
            {"id": 10, "question": "当上帝把我们从属灵上的死亡中拯救出来时，祂做了什么？", "references": ["弗 2:4-6"]},
            {"id": 11, "question": "当我们接受耶稣为我们的救主时会发生什么？", "references": ["约 1:12-13"]},
            {"id": 12, "question": "对于那些在基督里面的人，保罗说了什么？", "references": ["林后 5:17"]},
            {"id": 13, "question": "对于从上帝而生的人，他们的结局是什么？", "references": ["约一 5:4"]},
            {"id": 14, "question": "通过自己做好事我们被救赎，这可能吗？我们是如何被救赎的？", "references": ["弗 2:8-9"]},
            {"id": 15, "question": "上帝救赎我们是因为我们做了什么好事吗？如果不是，祂为什么要拯救我们？", "references": ["多 3:4-5"]},
            {"id": 16, "question": "上帝的恩典教导我们去做什么？", "references": ["多 2:11-12"]},
            {"id": 17, "question": "为了能够进入神的国度，耶稣说了什么？", "references": ["约 3:3-7"]},
        ],
        "application": "你应该用你被耶稣赋予的新生命去做什么？认识到我们就是罪人，只有通过耶稣的死和复活我们才可以被拯救。通过转离罪并把我们的信心放在基督身上，来回应祂，并且把祂当成主人一样去跟随祂。",
    },

    # ===== 主权 =====
    {
        "id": "kids_L2_S1",
        "theme": "主权",
        "lesson_num": 1,
        "title": "耶稣是主",
        "prev": "kids_L1_S2.html", "prev_label": "← 上一课",
        "next": "kids_L2_S2.html", "next_label": "第2课 →",
        "bible_readings": [
            "腓立比书 2:6-11", "使徒行传 2:36", "歌罗西书 2:6",
            "路加福音 6:46-49", "马太福音 7:13-20",
            "出埃及记 20:1-17", "马太福音 5:19", "马太福音 7:12",
            "以弗所书 5:3-5", "哥林多前书 6:9-10",
            "约翰福音 14:15,23-24",
        ],
        "teaching_text": "当我们说耶稣是主，我们就是在承认耶稣不仅是天父的独生子，也表明祂自己是神道成肉身。当我们说耶稣是主时，就意味着祂的话语完全是神的话语，必须全然信靠并遵从。这并不意味着救赎取决于我们的完美行为，而是取决于当我们把耶稣当作主来跟从时，我们对耶稣基督全然降服和顺从的态度。",
        "questions": [
            {"id": 1, "question": "保罗如何描述耶稣？", "references": ["腓 2:6-11"]},
            {"id": 2, "question": "关于耶稣，彼得向所有人宣告了什么？", "references": ["徒 2:36"]},
            {"id": 3, "question": "保罗说我们在接受耶稣后应该做些什么？", "references": ["西 2:6"]},
            {"id": 4, "question": "耶稣对那些不服从祂的人讲述了什么例子？", "references": ["路 6:46-49"]},
            {"id": 5, "question": "耶稣对于进入神的国是怎么说的？", "references": ["太 7:13-14"]},
            {"id": 6, "question": "我们如何知道一个人是否是真正跟随耶稣的？", "references": ["太 7:16"]},
            {"id": 7, "question": "对于那些结出坏果子的人，会发生什么？", "references": ["太 7:19"]},
            {"id": 8, "question": "神的十诫都是什么？", "references": ["出 20:1-17"]},
            {"id": 9, "question": "耶稣对于那些忽视律法的人是怎么说的？", "references": ["太 5:19"]},
            {"id": 10, "question": "耶稣说我们应该如何总结所有上帝的律法？", "references": ["太 7:12"]},
            {"id": 11, "question": "哪些事情，对信徒来说是不宜去做的？", "references": ["弗 5:3-5"]},
            {"id": 12, "question": "是什么诱惑基督徒觉得活在罪中也是可以的？", "references": ["林前 6:9-10"]},
            {"id": 13, "question": "对于那些爱耶稣的人，和不爱祂的人，区别是什么？", "references": ["约 14:15,23-24"]},
        ],
        "application": "你做过哪些事情，是你现在意识到是不对的？宣告耶稣是你生命的主，就意味着要用能反映出祂是谁和祂期待的样式来生活。",
    },
    {
        "id": "kids_L2_S2",
        "theme": "主权",
        "lesson_num": 2,
        "title": "团契与圣洁生活",
        "prev": "kids_L2_S1.html", "prev_label": "← 第1课",
        "next": "kids_L3_S1.html", "next_label": "下一主题 →",
        "bible_readings": [
            "哥林多后书 6:14-18", "哥林多前书 5:11",
            "约翰一书 3:14", "马太福音 18:21-22", "约翰福音 17:23",
            "腓立比书 2:3-4", "约翰一书 1:5-6", "约翰一书 3:11",
            "约翰一书 2:9-11", "约翰一书 3:7-10", "约翰一书 4:20",
            "哥林多前书 6:18-20", "诗篇 119:11", "雅各书 5:16",
        ],
        "teaching_text": "圣经讨论了很多关于要有\"团契\"生活。但是团契不仅仅是与其他人一起聊天或者一起聚餐，而是要与其他人一起分享生命。神并不希望我们与非信徒断绝来往，真正的团契是与其他信徒一起经历生命的丰盛。我们与其他信徒关系的质量就是对世上不信之人的最重要的见证。",
        "questions": [
            {"id": 1, "question": "保罗对于与非信徒的\"关系\"，是怎么说的？神对我们的命令是什么？神应许我们的回报是什么？", "references": ["林后 6:14-18"]},
            {"id": 2, "question": "根据圣经，我们应该避免与什么样的人交往？", "references": ["林前 5:11"]},
            {"id": 3, "question": "我们怎么知道自己不会因我们的罪而死，而是在基督里活出新生命？", "references": ["约一 3:14"]},
            {"id": 4, "question": "耶稣说我们要饶恕得罪我们的人多少次？", "references": ["太 18:21-22"]},
            {"id": 5, "question": "当我们彼此活在爱和合一中时，结果会怎样？", "references": ["约 17:23"]},
            {"id": 6, "question": "我们如何能拥有这样的合一？", "references": ["腓 2:3-4"]},
            {"id": 7, "question": "约翰宣告的信息是什么？", "references": ["约一 1:5"]},
            {"id": 8, "question": "约翰对那些声称与神相交却继续行走在黑暗中的人说了什么？", "references": ["约一 1:6"]},
            {"id": 9, "question": "神的命令是什么？", "references": ["约一 3:11"]},
            {"id": 10, "question": "约翰对那些声称爱神却憎恨其他信徒的人说了什么？", "references": ["约一 2:9-11"]},
            {"id": 11, "question": "我们如何能辨别出神的儿女？", "references": ["约一 3:7-10"]},
            {"id": 12, "question": "如果我们说我们爱神，但却恨一个弟兄或姊妹，我们是什么？", "references": ["约一 4:20"]},
            {"id": 13, "question": "当我们面对淫乱（不道德的性行为）时，我们应该做什么？", "references": ["林前 6:18-20"]},
            {"id": 14, "question": "为了不得罪神，我们能做些什么？", "references": ["诗 119:11"]},
            {"id": 15, "question": "我们应该做什么才能行走在责任与透明之中？", "references": ["雅 5:16"]},
        ],
        "application": "对你来说，在这世界中，而不属于这世界意味着什么？宣告耶稣是你生命的主，就意味着要用能反映出祂是谁和祂期待的样式来生活。这不是追求完美，而是在每天的生活中遵从和顺服祂对我们生命的旨意。",
    },

    # ===== 悔改 =====
    {
        "id": "kids_L3_S1",
        "theme": "悔改",
        "lesson_num": 1,
        "title": "真正的转变",
        "prev": "kids_L2_S2.html", "prev_label": "← 上一课",
        "next": "kids_L3_S2.html", "next_label": "第2课 →",
        "bible_readings": [
            "路加福音 15:11-24", "约翰福音 14:6; 16:13; 17:17",
            "罗马书 12:1-2", "歌罗西书 3:8-10",
            "帖撒罗尼迦前书 1:9", "使徒行传 3:19-20",
            "罗马书 1:17", "约翰一书 5:4-5", "雅各书 2:17-18",
        ],
        "teaching_text": "悔改在我们的心中产生的是真正的改变，是神的恩典在我们生活中做工所结的果子。基督徒的目标是像基督一样。如果我们在态度、动机、行为或言语上不像基督，那我们就需要改变。我们需要的是完全的转变，是彻底的翻转。这不是靠人为努力完成的，而是神在我们生命中所做的工。",
        "questions": [
            {"id": 1, "question": "耶稣说，什么会让天堂为之庆祝？", "references": ["路 15:7"]},
            {"id": 2, "question": "浪子对他的父亲说了什么？", "references": ["路 15:21"]},
            {"id": 3, "question": "父亲的回应是什么？", "references": ["路 15:22-24"]},
            {"id": 4, "question": "关于祂是谁，耶稣宣告了什么？", "references": ["约 14:6"]},
            {"id": 5, "question": "我们如何开始发现，圣经所说的真理？", "references": ["约 16:13"]},
            {"id": 6, "question": "我们如何才能在回应神的话语中成长？", "references": ["约 17:17"]},
            {"id": 7, "question": "为了不效法这个世界，我们是如何改变的？", "references": ["罗 12:1-2"]},
            {"id": 8, "question": "为了悔改，我们需要改变哪些事情？", "references": ["西 3:8-10"]},
            {"id": 9, "question": "除了转离罪之外，悔改还包括什么？", "references": ["帖前 1:9"]},
            {"id": 10, "question": "除了转离罪之外，悔改还包括什么？（续）", "references": ["徒 3:19-20"]},
            {"id": 11, "question": "我们要如何活出我们在基督里的新生命？", "references": ["罗 1:17"]},
            {"id": 12, "question": "我们如何克服世界及其所有挑战？", "references": ["约一 5:4-5"]},
            {"id": 13, "question": "我们如何表达我们对耶稣的信心？", "references": ["雅 2:17-18"]},
        ],
        "application": "你的生活中有什么需要改变的吗？你需要改变的态度是什么？哪些习惯需要改变？",
    },
    {
        "id": "kids_L3_S2",
        "theme": "悔改",
        "lesson_num": 2,
        "title": "悔改与偿还",
        "prev": "kids_L3_S1.html", "prev_label": "← 第1课",
        "next": "kids_L4_S1.html", "next_label": "下一主题 →",
        "bible_readings": [
            "使徒行传 17:30", "使徒行传 26:20", "箴言 28:13",
            "路加福音 19:1-10", "路加福音 13:2-5",
            "罗马书 2:4", "哥林多后书 7:10-11",
            "使徒行传 9:35; 11:21; 26:18",
            "约翰福音 6:47", "雅各书 2:19,26",
        ],
        "teaching_text": "\"悔改\"的意思是\"转身\"。不管事情变得多么糟糕，或者你感觉离神有多远，当你悔改（转身）时，你会立刻发现神的爱和怜悯依然在等着你。根据圣经，悔改包括认罪、为罪忧伤、转离罪和愿意补偿。但是没有信心悔改仍然是不完全的，这意味着我们从罪中转过来之后，我们需要转向神。",
        "questions": [
            {"id": 1, "question": "上帝命令谁悔改？", "references": ["徒 17:30"]},
            {"id": 2, "question": "保罗如何告诉他的听众他们怎样可以表现出他们的悔改？", "references": ["徒 26:20"]},
            {"id": 3, "question": "我们应该怎样对待自己的罪，才能得到怜悯？", "references": ["箴 28:13"]},
            {"id": 4, "question": "撒该提出的偿还是什么样的？", "references": ["路 19:8"]},
            {"id": 5, "question": "耶稣说如果我们不悔改会发生什么？", "references": ["路 13:2-5"]},
            {"id": 6, "question": "耶稣是怎么回应撒该的？", "references": ["路 19:9"]},
            {"id": 7, "question": "是什么引导我们悔改？", "references": ["罗 2:4"]},
            {"id": 8, "question": "这两种悲伤是什么，它们会产生什么？", "references": ["林后 7:10"]},
            {"id": 9, "question": "一个瘫痪的人奇迹般痊愈的结果是什么？", "references": ["徒 9:35"]},
            {"id": 10, "question": "保罗说我们离开黑暗时必须转向什么？", "references": ["徒 26:18"]},
            {"id": 11, "question": "有什么证据表明神大能的手与那些宣扬基督的人同在？", "references": ["徒 11:21"]},
            {"id": 12, "question": "除了悔改，敬虔的悲伤还会产生什么？", "references": ["林后 7:11"]},
            {"id": 13, "question": "那些真正相信的人的应许是什么？", "references": ["约 6:47"]},
            {"id": 14, "question": "仅仅说相信上帝就够了吗？", "references": ["雅 2:19"]},
            {"id": 15, "question": "圣经里是怎样描述没有行为的信心的？", "references": ["雅 2:26"]},
        ],
        "application": "你现在的生活中是否有需要补偿的人？在你的生活中，转向上帝是什么样子的？",
    },

    # ===== 灵修 =====
    {
        "id": "kids_L4_S1",
        "theme": "灵修",
        "lesson_num": 1,
        "title": "神的话语",
        "prev": "kids_L3_S2.html", "prev_label": "← 上一课",
        "next": "kids_L4_S2.html", "next_label": "第2课 →",
        "bible_readings": [
            "彼得后书 3:5", "使徒行传 2:42; 6:7",
            "提摩太后书 3:16-17", "约翰福音 1:1,14",
            "希伯来书 4:12", "诗篇 119:89,160",
            "以赛亚书 40:8; 55:11", "马太福音 24:35", "约翰福音 17:17",
            "约书亚记 1:8", "诗篇 1:1-3", "马太福音 4:1-11",
            "诗篇 119:9,11,72,98-100,103,105,127,165",
            "箴言 4:20-22", "诗篇 119:81", "约伯记 23:12", "耶利米书 15:16",
        ],
        "teaching_text": "圣经并不仅仅是告诉我们如何度过今生的说明书，或者是让我们去做什么的一系列规条。在我们的生命中知道神的声音是非常重要的，我们唯一能辨别神声音的方式就是透过阅读神的话语。任何健康关系的基础都是沟通。神的话语是祂向我们传达祂心中所想的方式。",
        "questions": [
            {"id": 1, "question": "圣经说这个世界是如何被建造的？", "references": ["彼后 3:5"]},
            {"id": 2, "question": "早期教会耶稣的跟随者致力于做什么？", "references": ["徒 2:42"]},
            {"id": 3, "question": "当神的道继续增长的时候会发生什么事？", "references": ["徒 6:7"]},
            {"id": 4, "question": "最初的圣经手稿是如何到达我们手上的？", "references": ["提后 3:16"]},
            {"id": 5, "question": "关于神的道约翰说了什么？", "references": ["约 1:1"]},
            {"id": 6, "question": "谁是道？", "references": ["约 1:14"]},
            {"id": 7, "question": "是什么让神的话语与其他的书区别？", "references": ["来 4:12"]},
            {"id": 8, "question": "下列章节关于神的道说了什么？", "references": ["诗 119:89"]},
            {"id": 9, "question": "神的话语的永恒性", "references": ["赛 40:8"]},
            {"id": 10, "question": "神对约书亚的命令是什么？如果约书亚遵守，神的应许是什么？", "references": ["书 1:8"]},
            {"id": 11, "question": "圣经手稿对什么有作用？", "references": ["提后 3:16-17"]},
            {"id": 12, "question": "描述一下反复思考神话语的人？", "references": ["诗 1:1-3"]},
            {"id": 13, "question": "耶稣是如何胜过试探打败魔鬼的？", "references": ["太 4:1-11"]},
            {"id": 14, "question": "大卫最强烈的渴望是什么？", "references": ["诗 119:81"]},
            {"id": 15, "question": "描述一下约伯对神话语的渴求。", "references": ["伯 23:12"]},
            {"id": 16, "question": "关于神的话语耶利米说了什么？", "references": ["耶 15:16"]},
        ],
        "application": "你阅读圣经会有什么困难吗？为什么？上帝的话语能帮助你做什么？",
    },
    {
        "id": "kids_L4_S2",
        "theme": "灵修",
        "lesson_num": 2,
        "title": "祷告",
        "prev": "kids_L4_S1.html", "prev_label": "← 第1课",
        "next": "kids_L5_S1.html", "next_label": "下一主题 →",
        "bible_readings": [
            "马可福音 1:35", "马太福音 6:5-13", "马太福音 7:7-11",
            "马太福音 21:22", "马可福音 11:24", "雅各书 4:3",
            "诗篇 66:18-19", "雅各书 1:6-8", "彼得前书 3:7",
            "腓立比书 4:6", "约翰福音 14:6",
            "约翰一书 5:14-15", "使徒行传 16:25-34",
        ],
        "teaching_text": "基督教就是一种神和人类的关系。所有的关系的建立都是通过沟通，我们和上帝之间的关系也没有什么不同。神通过很多种方式对我们说话，但是祂最主要对我们说话的方式是通过祂的话语：圣经。我们通过祷告和赞美来对祂说话。当我们阅读圣经的时候我们就是在听祂说话，当我们祷告和赞美的时候祂就在听我们说话。",
        "questions": [
            {"id": 1, "question": "耶稣在什么时间和地点祷告？", "references": ["可 1:35"]},
            {"id": 2, "question": "伪善者在什么地方祷告？", "references": ["太 6:5"]},
            {"id": 3, "question": "耶稣告诉祂的跟随者在什么地方祷告？", "references": ["太 6:6"]},
            {"id": 4, "question": "耶稣说我们应该对谁祷告？", "references": ["太 6:6,8-9"]},
            {"id": 5, "question": "我们应该为了什么而祷告？（主祷文）", "references": ["太 6:9-13"]},
            {"id": 6, "question": "对于那些祈求、寻找、叩门的人，神应许了什么？", "references": ["太 7:7-11"]},
            {"id": 7, "question": "如果我们祷告并且有信心我们可以得着什么？", "references": ["太 21:22"]},
            {"id": 8, "question": "耶稣说我们必须做什么使我们的祷告得蒙应允？", "references": ["可 11:24"]},
            {"id": 9, "question": "我们不能得着我们祈求的一个可能的原因是什么？", "references": ["雅 4:3"]},
            {"id": 10, "question": "什么会使我们的祷告成为阻碍？", "references": ["诗 66:18-19"]},
            {"id": 11, "question": "我们应该让谁知道我们的请求呢？", "references": ["腓 4:6"]},
            {"id": 12, "question": "我们怎样才能到达神那里？", "references": ["约 14:6"]},
            {"id": 13, "question": "我们对祷告有什么信心？", "references": ["约一 5:14-15"]},
            {"id": 14, "question": "当在监狱里面的时候保罗和西拉做了什么？", "references": ["徒 16:25"]},
            {"id": 15, "question": "对于他们祷告的结果是什么？", "references": ["徒 16:26-34"]},
        ],
        "application": "你有特定的时间留出来每日祷告吗？想想祷告在你的生活中扮演的角色？",
    },

    # ===== 圣灵 =====
    {
        "id": "kids_L5_S1",
        "theme": "圣灵",
        "lesson_num": 1,
        "title": "认识圣灵",
        "prev": "kids_L4_S2.html", "prev_label": "← 上一课",
        "next": "kids_L5_S2.html", "next_label": "第2课 →",
        "bible_readings": [
            "约翰福音 14:16-17", "马太福音 10:19-20", "约翰福音 14:26; 16:13-14",
            "使徒行传 1:8; 1:4-5", "罗马书 8:14-16,26-27", "提摩太后书 1:14",
            "马太福音 3:11", "使徒行传 2:1-6; 8:14-19; 9:17-19; 10:44-48; 19:1-6",
            "撒母耳记上 3:1-11", "路加福音 11:13",
        ],
        "teaching_text": "当耶稣复活的时候，对门徒来说这是一个好消息。由于祂即将回到天上的天父家，所以祂不能在地上呆太长时间。好消息是：耶稣告诉他们天父会赐下圣灵——神应许的礼物。离开了圣灵的力量和存在，人不可能过一个基督徒的生活。从我们重生的那刻开始，神的灵赋予我们能力，使我们在说话、思想、行事方面成为基督始终如一的见证。",
        "questions": [
            {"id": 1, "question": "圣灵是谁？", "references": ["约 14:16-17"]},
            {"id": 2, "question": "圣灵帮助我们的方法——在说话上", "references": ["太 10:19-20"]},
            {"id": 3, "question": "圣灵帮助我们的方法——在教导上", "references": ["约 14:26"]},
            {"id": 4, "question": "圣灵帮助我们的方法——在引导上", "references": ["约 16:13-14"]},
            {"id": 5, "question": "圣灵帮助我们的方法——在见证上", "references": ["徒 1:8"]},
            {"id": 6, "question": "耶稣告诉祂的门徒说当祂升到天上去之后，他们会做什么？", "references": ["徒 1:4-5"]},
            {"id": 7, "question": "施洗者约翰承诺说上帝会做什么？", "references": ["太 3:11"]},
            {"id": 8, "question": "描述五旬节圣灵降临的情形？", "references": ["徒 2:1-6"]},
            {"id": 9, "question": "天父把圣灵给了谁？", "references": ["路 11:13"]},
            {"id": 10, "question": "为什么撒母耳没有认出神的声音？", "references": ["撒上 3:1"]},
            {"id": 11, "question": "当以利告诉撒母耳那是神的呼召后，撒母耳的回应是什么？", "references": ["撒上 3:9-10"]},
        ],
        "application": "在我们的生命中为什么需要圣灵？今天圣灵在你的生命中可以帮助你做什么？",
    },
    {
        "id": "kids_L5_S2",
        "theme": "圣灵",
        "lesson_num": 2,
        "title": "圣灵的果子与恩赐",
        "prev": "kids_L5_S1.html", "prev_label": "← 第1课",
        "next": "kids_L6_S1.html", "next_label": "下一主题 →",
        "bible_readings": [
            "约翰福音 15:1-8", "加拉太书 5:22-23",
            "罗马书 12:6-8", "以弗所书 4:11-12",
            "哥林多前书 12:4-11; 13:1-2,13; 14:1-40",
            "哥林多前书 3:16", "使徒行传 1:8", "以弗所书 4:30",
        ],
        "teaching_text": "多结果子是圣经中一个重要主题。一颗多结果子的葡萄树是被细心的园丁树立在地上并且时常细心呵护的。认为枝子离开了葡萄树可以生长并且多结果子的想法是非常愚蠢的。圣灵的果子里面蕴藏了神的属性，而借着圣灵的恩赐把神的大能显明给世人。作为神在人间的代表，我们需要同时发展圣灵的果实和圣灵的恩赐。",
        "questions": [
            {"id": 1, "question": "那些不结果子的树枝会怎么样？", "references": ["约 15:2"]},
            {"id": 2, "question": "结果的树枝会怎么样？为什么父要修建多结果子的树枝？", "references": ["约 15:2"]},
            {"id": 3, "question": "我们可以靠着自己结果子吗？", "references": ["约 15:4"]},
            {"id": 4, "question": "为了结圣灵的果子我们必须做什么？", "references": ["约 15:4-5"]},
            {"id": 5, "question": "我们怎样可以给父带来荣耀？", "references": ["约 15:8"]},
            {"id": 6, "question": "要住在葡萄树上是什么意思？", "references": ["约 15:4-7"]},
            {"id": 7, "question": "列出圣灵所结的果子", "references": ["加 5:22-23"]},
            {"id": 8, "question": "最好的是什么？", "references": ["林前 13:13"]},
            {"id": 9, "question": "圣灵会居住在哪里？", "references": ["林前 3:16"]},
            {"id": 10, "question": "列出保罗在罗马书上提到的圣灵的恩赐。", "references": ["罗 12:6-8"]},
            {"id": 11, "question": "列出神赐予教会的领导恩赐。", "references": ["弗 4:11-12"]},
            {"id": 12, "question": "我们对待圣灵的恩赐应该持什么态度？", "references": ["林前 14:1"]},
            {"id": 13, "question": "我们渴望和使用属灵恩赐的动机应该是什么？", "references": ["林前 13:1-2"]},
            {"id": 14, "question": "神应许当圣灵降在门徒的身上时会发生什么？", "references": ["徒 1:8"]},
            {"id": 15, "question": "我们被警告不要做什么？", "references": ["弗 4:30"]},
        ],
        "application": "在你生命中看到圣灵所结果子的迹象了吗？想想在你生命中经历圣灵大能的某个时刻，发生了什么？",
    },

    # ===== 宣教与使命 =====
    {
        "id": "kids_L6_S1",
        "theme": "宣教与使命",
        "lesson_num": 1,
        "title": "分享福音",
        "prev": "kids_L5_S2.html", "prev_label": "← 上一课",
        "next": "kids_L6_S2.html", "next_label": "第2课 →",
        "bible_readings": [
            "哥林多后书 5:18-20", "约翰福音 13:35",
            "罗马书 1:14-16; 10:13-15",
            "使徒行传 10:24,44-48; 20:20-21",
            "箴言 29:25; 28:1",
            "使徒行传 4:29,31; 9:19-28",
            "以弗所书 6:19-20",
        ],
        "teaching_text": "圣灵降下并不是说仅仅让门徒过上好日子，而是因着一个使命。救赎的信息意味着它需要被分享给每个民族的每个公民。耶稣想要我们用我们的话语和行为来宣扬福音。好消息是：无论我们身在何处，神自己凭着圣灵的帮助，让我们作祂的代表。",
        "questions": [
            {"id": 1, "question": "耶稣给了每个信徒什么使命？", "references": ["林后 5:18-20"]},
            {"id": 2, "question": "别的人是怎么知道我们是耶稣的门徒的？", "references": ["约 13:35"]},
            {"id": 3, "question": "对于向未信主之人分享福音，保罗的态度是什么样子的？", "references": ["罗 1:14-16"]},
            {"id": 4, "question": "在人们求告主名之前必须发生什么？", "references": ["罗 10:13-15"]},
            {"id": 5, "question": "在哥尼流家里听彼得讲道的人身上发生了什么？", "references": ["徒 10:44-48"]},
            {"id": 6, "question": "保罗传讲了什么？", "references": ["徒 20:20-21"]},
            {"id": 7, "question": "箴言关于惧怕人的是怎么说的？", "references": ["箴 29:25"]},
            {"id": 8, "question": "描述下恶人和义人的区别是什么？", "references": ["箴 28:1"]},
            {"id": 9, "question": "在迫害的恐吓下，信徒为着什么来祷告？", "references": ["徒 4:29"]},
            {"id": 10, "question": "他们祷告的结果是什么？", "references": ["徒 4:31"]},
            {"id": 11, "question": "在扫罗转变信仰之后，他等了多久就去传讲福音了？", "references": ["徒 9:19-20"]},
            {"id": 12, "question": "尽管保罗的生命处于危险中，但保罗是如何讲道的？", "references": ["徒 9:22-28"]},
            {"id": 13, "question": "保罗为着他能以何种方式传扬福音寻求祷告？", "references": ["弗 6:19-20"]},
        ],
        "application": "写出三个你觉得上帝呼召你去给他们传讲福音的朋友或者亲人的名字。花点时间写下一个祷告，求神给你胆量，让你与别人分享救恩的信息。",
    },
    {
        "id": "kids_L6_S2",
        "theme": "宣教与使命",
        "lesson_num": 2,
        "title": "大使命",
        "prev": "kids_L6_S1.html", "prev_label": "← 第1课",
        "next": "kids_L7_S1.html", "next_label": "下一主题 →",
        "bible_readings": [
            "路加福音 4:18-21", "约翰一书 3:8", "以弗所书 6:12",
            "使徒行传 16:14", "哥林多后书 4:4", "歌罗西书 2:8",
            "使徒行传 8:6-8", "雅各书 5:14-15",
            "约翰福音 14:12-14", "使徒行传 3:6-7,16",
            "马太福音 28:18-20", "腓立比书 2:10-11",
            "使徒行传 1:8", "马太福音 9:35-38",
        ],
        "teaching_text": "耶稣叫我们传福音给贫穷的、被掳的、瞎眼的、受压制的人，祂也叫我们毁坏撒旦的工。当我们向迷失的人传福音的时候，我们在打一场属灵的仗。当我们宣讲真理的时候，耶稣基督会让那些被掳的得释放。我们所要做的就是放胆宣扬神救恩的好消息，并且祷告成就。当我们迈出了信心的这一步，神迹就会在人们的生活中发生。",
        "questions": [
            {"id": 1, "question": "耶稣来是要做什么？", "references": ["路 4:18-21"]},
            {"id": 2, "question": "为什么神的儿子要显现出来？", "references": ["约一 3:8"]},
            {"id": 3, "question": "我们在与什么争战？", "references": ["弗 6:12"]},
            {"id": 4, "question": "当保罗传道的时候发生了什么？", "references": ["徒 16:14"]},
            {"id": 5, "question": "在非信徒身上发生了什么？", "references": ["林后 4:4"]},
            {"id": 6, "question": "人是怎样被掳去的？", "references": ["西 2:8"]},
            {"id": 7, "question": "为什么撒玛利亚人都听腓利的话？", "references": ["徒 8:6-8"]},
            {"id": 8, "question": "雅各教导教会要为病人做什么呢？", "references": ["雅 5:14-15"]},
            {"id": 9, "question": "耶稣向信徒们承诺了什么？", "references": ["约 14:12"]},
            {"id": 10, "question": "美门的那个瘸子是怎样被治好的？", "references": ["徒 3:6-7,16"]},
            {"id": 11, "question": "耶稣基督之名有多大的权柄？", "references": ["太 28:18"]},
            {"id": 12, "question": "耶稣基督给祂的信徒最后的命令是什么？", "references": ["太 28:19"]},
            {"id": 13, "question": "耶稣承诺当圣灵降下的时候会发生什么？", "references": ["徒 1:8"]},
            {"id": 14, "question": "对于那些使万民做耶稣门徒的人，耶稣给了他们什么承诺？", "references": ["太 28:20"]},
            {"id": 15, "question": "世界上福音的状况是怎样的呢？", "references": ["太 9:35-37"]},
            {"id": 16, "question": "耶稣说我们要为了什么迫切地祷告呢？", "references": ["太 9:38"]},
        ],
        "application": "有没有哪个国家是上帝希望你为他们祷告的？上帝希望你在他对万民的救赎计划中做哪一部分的工作呢？",
    },

    # ===== 门徒与带领 =====
    {
        "id": "kids_L7_S1",
        "theme": "门徒与带领",
        "lesson_num": 1,
        "title": "作门徒",
        "prev": "kids_L6_S2.html", "prev_label": "← 上一课",
        "next": "kids_L7_S2.html", "next_label": "第2课 →",
        "bible_readings": [
            "马太福音 4:18-19", "使徒行传 2:42", "约翰福音 8:31",
            "路加福音 8:38-39", "希伯来书 10:24-25",
            "马太福音 28:18-20", "提摩太后书 2:2-6",
            "路加福音 6:48-49; 9:23; 14:27-33",
            "歌罗西书 2:13-15", "哥林多前书 1:18",
            "加拉太书 2:20",
        ],
        "teaching_text": "当耶稣在地上时，祂所做的不仅仅是吸引人群。耶稣邀请人们成为祂的门徒。成为门徒的起始点是跟随耶稣。我们通过服从祂的话语来跟随祂。门徒训练从跟随耶稣开始，但它不仅仅是为了跟随耶稣。作门徒也是为了帮助别人跟随耶稣。我们通过向朋友、同学、家人和亲戚讲述基督为我们所做的一切来做到这一点。",
        "questions": [
            {"id": 1, "question": "当耶稣看到加利利的渔夫时，祂告诉他们的第一件事情是什么？耶稣说渔夫跟随他之后将要做什么？", "references": ["太 4:18-19"]},
            {"id": 2, "question": "早期教会致力于什么？", "references": ["徒 2:42"]},
            {"id": 3, "question": "我们如何得知我们需要跟随或服从什么？", "references": ["约 8:31"]},
            {"id": 4, "question": "与其他信徒的团契是什么样子的？", "references": ["来 10:24-25"]},
            {"id": 5, "question": "耶稣呼召祂的跟随者做什么？", "references": ["太 28:19"]},
            {"id": 6, "question": "耶稣告诉我们在为新信徒施洗后必须做什么？", "references": ["太 28:20"]},
            {"id": 7, "question": "保罗吩咐提摩太用他所受的教训做什么？", "references": ["提后 2:2-6"]},
            {"id": 8, "question": "耶稣是如何描述那个听到祂的话就去行的人的呢？", "references": ["路 6:48"]},
            {"id": 9, "question": "耶稣如何描述听到他的话却不去做的人呢？", "references": ["路 6:49"]},
            {"id": 10, "question": "耶稣说他所有的门徒都必须做哪三件事才算跟随他？", "references": ["路 9:23"]},
            {"id": 11, "question": "耶稣还把作门徒比作什么？在开始盖楼之前，我们应该做什么？", "references": ["路 14:27-33"]},
            {"id": 12, "question": "在十字架上发生了什么？", "references": ["西 2:13-15"]},
            {"id": 13, "question": "十字架给迷失和垂死的人的信息是什么？对那些正在被拯救的人又是什么呢？", "references": ["林前 1:18"]},
            {"id": 14, "question": "你认为保罗说\"我已经与基督同钉十字架\"是什么意思？", "references": ["加 2:20"]},
        ],
        "application": "用你自己的话描述一下你认为作门徒的意义。你认为与基督同钉十字架对你意味着什么？",
    },
    {
        "id": "kids_L7_S2",
        "theme": "门徒与带领",
        "lesson_num": 2,
        "title": "基督徒品格",
        "prev": "kids_L7_S1.html", "prev_label": "← 第1课",
        "next": "kids_L8_S1.html", "next_label": "下一主题 →",
        "bible_readings": [
            "彼得后书 1:3-11", "罗马书 5:3-4", "雅各书 1:2-4",
            "马太福音 4:19-20", "马可福音 6:7", "马太福音 10:1",
            "马太福音 28:18-20",
        ],
        "teaching_text": "耶稣基督的门徒最重要的印记是敬虔的品格。圣灵的恩赐在宣扬和展示福音方面很重要，但圣灵的果实才是揭示我们作为耶稣的真正跟随者的身份。那些基督的门徒会在他们的思想、言语、行为和与他人相处的方式中表现出基督的品格来。虽然每个门徒都被赋予恩赐，但我们必须真实地在跟随耶稣中活出基督品格的印记。",
        "questions": [
            {"id": 1, "question": "神用祂的神能赐给我们什么？", "references": ["彼后 1:3"]},
            {"id": 2, "question": "我们如何能够分享神的性情呢？我们能够脱离什么呢？", "references": ["彼后 1:3-4"]},
            {"id": 3, "question": "我们要在信仰上增加什么，才能过上敬虔的生活？", "references": ["彼后 1:5-7"]},
            {"id": 4, "question": "在你的生活中，这些品质的成长有什么结果？", "references": ["彼后 1:8"]},
            {"id": 5, "question": "那些没有这些品格的人处于什么境况？", "references": ["彼后 1:9"]},
            {"id": 6, "question": "对于那些践行这些基督徒品质的人的应许是什么？", "references": ["彼后 1:10-11"]},
            {"id": 7, "question": "我们为什么要在苦难中欢喜？", "references": ["罗 5:3-4"]},
            {"id": 8, "question": "为什么雅各说我们可以把试炼当作全然的喜乐？", "references": ["雅 1:2-4"]},
            {"id": 9, "question": "耶稣告诉他的第一批门徒要做什么？第一批门徒是如何回应耶稣的命令和应许的？", "references": ["太 4:19-20"]},
            {"id": 10, "question": "耶稣给了门徒什么权柄，让他们去做什么？他们行使这种权柄做了什么？", "references": ["可 6:7"]},
            {"id": 11, "question": "耶稣在离世前对他的门徒小组说了什么？", "references": ["太 28:18-20"]},
        ],
        "application": "你的什么品格特质是你可能需要努力以体现敬虔的品格？你认为你能成为一个能产生影响的伟大领袖吗？为什么或为什么不？",
    },

    # ===== 属灵家庭和教会生活 =====
    {
        "id": "kids_L8_S1",
        "theme": "属灵家庭和教会生活",
        "lesson_num": 1,
        "title": "教会——基督的身体",
        "prev": "kids_L7_S2.html", "prev_label": "← 上一课",
        "next": "kids_L8_S2.html", "next_label": "第2课 →",
        "bible_readings": [
            "马太福音 16:18", "哥林多前书 10:4",
            "以弗所书 2:20; 5:25-28",
            "使徒行传 2:42-47; 4:32-37",
            "路加福音 21:1-4",
            "哥林多前书 12:14-27",
            "哥林多后书 8:1-5",
            "哥林多前书 12:18,21,22-24,25-26",
            "约翰福音 17:20-21", "以弗所书 4:3",
        ],
        "teaching_text": "在新约中彼得是向第一个教会传道的第一人，他告诉那些听道的人要悔改、受洗礼、领受圣灵，而那些听了就回应的人使信徒的数量大大加增——这些信徒就是我们现在所称的教会。我们并不是被拣选过孤独的基督徒生活，而是需要和别人一起跟随神。教会是神提升祂国度的器皿，祂没有B计划。",
        "questions": [
            {"id": 1, "question": "耶稣关于祂荣耀的教会说了些什么？", "references": ["太 16:18"]},
            {"id": 2, "question": "谁是磐石？", "references": ["林前 10:4"]},
            {"id": 3, "question": "谁是房角石？", "references": ["弗 2:20"]},
            {"id": 4, "question": "保罗把基督对教会的爱比作什么？", "references": ["弗 5:25-28"]},
            {"id": 5, "question": "初期教会的成员致力于什么？", "references": ["徒 2:42"]},
            {"id": 6, "question": "简略描绘初期的教会生活。", "references": ["徒 2:42-47"]},
            {"id": 7, "question": "关于早期教会的慷慨你知道些什么？", "references": ["徒 4:32-37"]},
            {"id": 8, "question": "通过耶稣的话，谁捐的是最多的？为什么？", "references": ["路 21:1-4"]},
            {"id": 9, "question": "关于基督每个肢体的重要性，保罗说了什么？", "references": ["林前 12:14-20"]},
            {"id": 10, "question": "谁决定身体的各个部分应该如何运作？", "references": ["林前 12:18"]},
            {"id": 11, "question": "对于那些认为不需要身体其他部位的人，保罗是怎么说的？", "references": ["林前 12:21"]},
            {"id": 12, "question": "对于那些看似软弱的肢体，保罗说了什么？", "references": ["林前 12:22-24"]},
            {"id": 13, "question": "身体的各个部位应该如何对待彼此？", "references": ["林前 12:25-26"]},
            {"id": 14, "question": "耶稣为祂的门徒的合一祷告了什么？", "references": ["约 17:20-21"]},
            {"id": 15, "question": "为了保持灵的合一我们应该做什么？", "references": ["弗 4:3"]},
        ],
        "application": "你认为神呼召你在祂的教会中扮演什么样的角色？祂是如何赋予你恩赐的？",
    },
    {
        "id": "kids_L8_S2",
        "theme": "属灵家庭和教会生活",
        "lesson_num": 2,
        "title": "教会带领与圣餐",
        "prev": "kids_L8_S1.html", "prev_label": "← 第1课",
        "next": "", "next_label": "",
        "bible_readings": [
            "以弗所书 4:11-16", "提多书 1:5",
            "约翰福音 21:15-17", "使徒行传 20:28",
            "以西结书 33:1-9; 34:2-5",
            "帖撒罗尼迦前书 5:12-13,25",
            "提摩太前书 5:17-19", "希伯来书 13:7,17",
            "以弗所书 4:15", "哥林多前书 3:10-11",
            "哥林多前书 11:26-32", "使徒行传 2:42",
        ],
        "teaching_text": "早期的教会不仅仅是一个组织，而是一个被神的灵掌管的活的有机体，这也是今天教会应该成为的样式。耶稣告诉门徒，为了纪念祂而吃喝。这个圣餐仪式代表了耶稣在十字架上的牺牲。这同时也是我们对自己新的生命、我们和耶稣新的关系的一个提醒。",
        "questions": [
            {"id": 1, "question": "神在教会中所担当的权柄和领导的五种角色是什么？", "references": ["弗 4:11-16"]},
            {"id": 2, "question": "提多为什么留在克里特岛？", "references": ["多 1:5"]},
            {"id": 3, "question": "牧师、长老、属灵领袖的一些职责是什么？", "references": ["约 21:15-17"]},
            {"id": 4, "question": "教会成员应该如何与他们的牧师、教会长老、属灵领袖建立关系？", "references": ["帖前 5:12-13"]},
            {"id": 5, "question": "谁是教会的头？", "references": ["弗 4:15"]},
            {"id": 6, "question": "谁是教会的基石？", "references": ["林前 3:10-11"]},
            {"id": 7, "question": "早期的门徒致力于做什么？", "references": ["徒 2:42"]},
            {"id": 8, "question": "当我们领圣餐时，宣告了什么？", "references": ["林前 11:26"]},
            {"id": 9, "question": "当我们不配得的时候，领受圣餐会发生什么？", "references": ["林前 11:27"]},
            {"id": 10, "question": "当我们领圣餐时，我们应该做什么？", "references": ["林前 11:28"]},
            {"id": 11, "question": "如果我们一直领受圣餐，却没有尊荣耶稣的身体和转离我们的罪，我们会发生什么？", "references": ["林前 11:29"]},
            {"id": 12, "question": "这对许多人造成了什么影响？", "references": ["林前 11:30"]},
            {"id": 13, "question": "我们如何避免被审判？", "references": ["林前 11:31"]},
            {"id": 14, "question": "当神审判管教祂的儿女时，祂的动机是什么？", "references": ["林前 11:32"]},
        ],
        "application": "谁是一个在教会里受你尊敬的领袖？为什么？纪念耶稣的死与复活有什么重要意义？",
    },
]


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(ANSWERS_DIR, exist_ok=True)

    for lesson in COURSE_DATA:
        lesson_id = lesson["id"]
        html = generate_lesson_html(lesson)
        filepath = os.path.join(OUTPUT_DIR, f"{lesson_id}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Generated: {lesson_id}.html")

    # Save course data as JSON
    course_json_path = os.path.join(DATA_DIR, "kids_course.json")
    with open(course_json_path, "w", encoding="utf-8") as f:
        json.dump(COURSE_DATA, f, ensure_ascii=False, indent=2)
    print(f"\nSaved course data: {course_json_path}")
    print(f"\nTotal: {len(COURSE_DATA)} lessons generated")


if __name__ == "__main__":
    main()
