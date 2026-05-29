/**
 * 圣经版本管理器
 * 仅负责更新页面上的经文内容
 */
class BibleVersionManager {
    constructor() {
        // 从 localStorage 加载选中的版本，默认为 ['cunps']
        const saved = localStorage.getItem('bibleVersions');
        this.selectedVersions = saved ? JSON.parse(saved) : ['cunps'];
        if (!Array.isArray(this.selectedVersions) || this.selectedVersions.length === 0) {
            this.selectedVersions = ['cunps'];
        }
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
            
            // 4. 立即更新页面以匹配选中的版本
            this.updatePageVerses();
            
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
        
        // 添加提示文本
        const hint = document.createElement('div');
        hint.className = 'version-selector-hint';
        hint.textContent = '选择版本 (可多选):';
        selectorContainer.appendChild(hint);
        
        Object.values(this.versions).forEach(ver => {
            const label = document.createElement('label');
            label.className = 'version-checkbox-label';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = ver.id;
            checkbox.checked = this.selectedVersions.includes(ver.id);
            
            checkbox.addEventListener('change', (e) => {
                this.handleVersionChange(e.target);
            });

            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(ver.abbreviation));
            selectorContainer.appendChild(label);
        });

        header.appendChild(selectorContainer);
    }

    handleVersionChange(checkbox) {
        const verId = checkbox.value;
        
        if (checkbox.checked) {
            // 添加版本
            if (this.selectedVersions.length >= 3) {
                alert('最多只能同时显示3个版本');
                checkbox.checked = false;
                return;
            }
            if (!this.selectedVersions.includes(verId)) {
                this.selectedVersions.push(verId);
            }
        } else {
            // 移除版本
            if (this.selectedVersions.length <= 1) {
                alert('至少需要显示一个版本');
                checkbox.checked = true;
                return;
            }
            this.selectedVersions = this.selectedVersions.filter(id => id !== verId);
        }

        // 保存并更新
        // 保持版本顺序：cunps, csb, esv
        const order = ['cunps', 'csb', 'esv']; 
        this.selectedVersions.sort((a, b) => order.indexOf(a) - order.indexOf(b));
        
        localStorage.setItem('bibleVersions', JSON.stringify(this.selectedVersions));
        this.updatePageVerses();
    }

    updatePageVerses() {
        const scriptureDivs = document.querySelectorAll('.scripture-container');
        
        scriptureDivs.forEach(div => {
            const id = div.getAttribute('data-id');
            const data = this.verseData[id];
            
            if (data && data.versions) {
                // 清空当前内容
                div.innerHTML = '';

                this.selectedVersions.forEach(verId => {
                    const content = data.versions[verId];
                    const verInfo = this.versions[verId];
                    
                    if (content) {
                        const block = document.createElement('div');
                        block.className = 'version-block';
                        
                        // 如果显示多个版本，添加版本标签
                        if (this.selectedVersions.length > 1) {
                            const label = document.createElement('div');
                            label.className = 'version-label';
                            label.textContent = verInfo.name;
                            block.appendChild(label);
                        }

                        const textDiv = document.createElement('div');
                        textDiv.className = 'scripture-text';
                        textDiv.textContent = content;
                        block.appendChild(textDiv);

                        const refDiv = document.createElement('div');
                        refDiv.className = 'scripture-ref';
                        
                        // 处理引用格式
                        let refText = data.ref;
                        refText = refText.replace(/\s*和合本\s*/, '');
                        // 如果只有一个版本，显示在引用里；如果有多个版本，引用里就不需要重复版本名了，因为上面有label
                        // 但为了清晰，还是保持引用纯净，版本名在label或引用后
                        if (this.selectedVersions.length === 1) {
                             refDiv.textContent = `(${refText} ${verInfo.name})`;
                        } else {
                             refDiv.textContent = `(${refText})`;
                        }
                        
                        block.appendChild(refDiv);
                        div.appendChild(block);
                    }
                });
            }
        });
    }
}

window.bibleManager = new BibleVersionManager();
