/**
 * 圣经版本管理器
 * 仅负责更新页面上的经文内容
 */
class BibleVersionManager {
    constructor() {
        this.currentVersion = localStorage.getItem('bibleVersion') || 'cuv';
        this.versions = {};
        this.verseData = {};
    }

    async init(pageId) {
        // 1. 加载版本配置
        try {
            const vResponse = await fetch('data/bible-versions.json');
            const vData = await vResponse.json();
            this.versions = vData.versions;
            
            // 2. 加载当前页面的经文数据
            if (pageId) {
                try {
                    const dResponse = await fetch(`data/${pageId}_verses.json`);
                    if (dResponse.ok) {
                        this.verseData = await dResponse.json();
                    } else {
                        console.log(`No verse data found for ${pageId}`);
                    }
                } catch (e) {
                    console.warn('Could not load verse data:', e);
                }
            }

            // 3. 初始化UI
            this.createVersionSelector();
            
            // 4. 如果不是默认版本，立即更新页面
            if (this.currentVersion !== 'cuv') {
                this.updatePageVerses();
            }
        } catch (error) {
            console.error('Failed to init bible manager:', error);
        }
    }

    createVersionSelector() {
        const header = document.querySelector('header');
        if (!header) return;

        // 检查是否已存在
        if (document.querySelector('.version-selector')) return;

        const selectorContainer = document.createElement('div');
        selectorContainer.className = 'version-selector';
        
        const select = document.createElement('select');
        select.className = 'version-select';
        
        Object.values(this.versions).forEach(ver => {
            const option = document.createElement('option');
            option.value = ver.id;
            option.textContent = `${ver.name} (${ver.abbreviation})`;
            if (ver.id === this.currentVersion) {
                option.selected = true;
            }
            select.appendChild(option);
        });

        select.addEventListener('change', (e) => {
            this.changeVersion(e.target.value);
        });

        selectorContainer.appendChild(select);
        header.appendChild(selectorContainer);
    }

    changeVersion(versionId) {
        this.currentVersion = versionId;
        localStorage.setItem('bibleVersion', versionId);
        this.updatePageVerses();
    }

    updatePageVerses() {
        const scriptureDivs = document.querySelectorAll('.scripture-container');
        
        scriptureDivs.forEach(div => {
            const id = div.getAttribute('data-id');
            const data = this.verseData[id];
            
            if (data && data.versions) {
                const content = data.versions[this.currentVersion] || data.versions['cuv'];
                const verInfo = this.versions[this.currentVersion];
                
                // 更新经文文本
                const textDiv = div.querySelector('.scripture-text');
                if (textDiv) textDiv.textContent = content;
                
                // 更新引用
                const refDiv = div.querySelector('.scripture-ref');
                if (refDiv) {
                    // 保持引用格式 (书卷章节 版本)
                    // 简单的替换策略：如果引用里有"和合本"，替换为当前版本名
                    // 或者直接重构引用字符串
                    let refText = data.ref;
                    // 移除旧的版本标记（如果有）
                    refText = refText.replace(/\s*和合本\s*/, ''); 
                    refDiv.textContent = `(${refText} ${verInfo.name})`;
                }
            }
        });
    }
}

window.bibleManager = new BibleVersionManager();
