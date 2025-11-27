(function() {
    // State
    const state = {
        theme: localStorage.getItem('reader_theme') || 'light',
        fontSize: parseInt(localStorage.getItem('reader_fontSize')) || 19,
        fontFamily: localStorage.getItem('reader_fontFamily') || 'serif',
        layout: localStorage.getItem('reader_layout') || 'scroll',
        sidebarOpen: false,
        settingsOpen: false
    };

    // Ensure FontAwesome
    if (!document.querySelector('link[href*="font-awesome"]')) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css';
        document.head.appendChild(link);
    }

    function injectUI() {
        const body = document.body;

        // Toolbar
        const toolbar = document.createElement('div');
        toolbar.className = 'reader-toolbar';
        toolbar.innerHTML = `
            <div class="reader-btn" id="btn-toc" title="目录"><i class="fas fa-list"></i></div>
            <div class="reader-btn" id="btn-settings" title="设置"><i class="fas fa-font"></i></div>
            <div class="reader-btn" id="btn-mode" title="模式"><i class="fas fa-columns"></i></div>
            <div class="reader-btn" id="btn-home" title="返回主页" onclick="window.location.href='../index.html'"><i class="fas fa-home"></i></div>
        `;
        body.appendChild(toolbar);

        // Sidebar
        const sidebar = document.createElement('div');
        sidebar.className = 'reader-sidebar';
        sidebar.innerHTML = `
            <div class="sidebar-header">
                <h3>目录</h3>
                <div style="cursor:pointer" id="btn-close-sidebar"><i class="fas fa-times"></i></div>
            </div>
            <div class="sidebar-tabs">
                <div class="sidebar-tab active" data-tab="toc">目录</div>
                <div class="sidebar-tab" data-tab="search">搜索</div>
            </div>
            <div class="search-box" style="display:none">
                <input type="text" class="search-input" placeholder="搜索全书内容...">
            </div>
            <div class="sidebar-content" id="sidebar-content">
                <!-- Content goes here -->
            </div>
        `;
        body.appendChild(sidebar);

        // Settings Modal
        const modal = document.createElement('div');
        modal.className = 'settings-modal';
        modal.innerHTML = `
            <div class="setting-group">
                <span class="setting-label">主题</span>
                <div class="theme-options">
                    <div class="theme-btn light" data-theme="light">浅色</div>
                    <div class="theme-btn dark" data-theme="dark">深色</div>
                </div>
            </div>
            <div class="setting-group">
                <span class="setting-label">字号</span>
                <div class="font-size-controls">
                    <button class="font-btn" id="font-decrease"><i class="fas fa-minus"></i></button>
                    <span id="font-size-display">${state.fontSize}</span>
                    <button class="font-btn" id="font-increase"><i class="fas fa-plus"></i></button>
                </div>
            </div>
            <div class="setting-group">
                <span class="setting-label">字体</span>
                <select id="font-family-select" style="width:100%; padding:5px;">
                    <option value="serif">宋体 / Serif</option>
                    <option value="sans">黑体 / Sans</option>
                </select>
            </div>
        `;
        body.appendChild(modal);

        // Overlay
        const overlay = document.createElement('div');
        overlay.className = 'reader-overlay';
        body.appendChild(overlay);
    }

    function applyState() {
        const body = document.body;
        const content = document.querySelector('.content-wrapper');
        
        // Theme
        if (state.theme === 'dark') {
            body.classList.add('dark-mode');
        } else {
            body.classList.remove('dark-mode');
        }
        document.querySelectorAll('.theme-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.theme === state.theme);
        });

        // Font Size
        document.documentElement.style.setProperty('--base-font-size', `${state.fontSize}px`);
        document.getElementById('font-size-display').textContent = state.fontSize;

        // Font Family
        if (state.fontFamily === 'sans') {
            body.style.fontFamily = 'var(--font-sans)';
        } else {
            body.style.fontFamily = 'var(--font-serif)';
        }
        document.getElementById('font-family-select').value = state.fontFamily;

        // Layout
        if (state.layout === 'columns' && window.innerWidth > 768) {
            body.classList.add('column-mode');
        } else {
            body.classList.remove('column-mode');
        }
        
        // Update Mode Icon
        const modeIcon = document.querySelector('#btn-mode i');
        if (modeIcon) {
            modeIcon.className = state.layout === 'columns' ? 'fas fa-scroll' : 'fas fa-columns';
        }
    }

    function renderTOC() {
        const container = document.getElementById('sidebar-content');
        if (!readerData || !readerData.toc) return;

        const currentFile = window.location.pathname.split('/').pop();
        
        let html = '<ul class="reader-toc-list">';
        readerData.toc.forEach(item => {
            const isActive = item.link === currentFile ? 'active' : '';
            html += `<li><a href="${item.link}" class="${isActive}">${item.title}</a></li>`;
        });
        html += '</ul>';
        container.innerHTML = html;
    }

    function performSearch(query) {
        const container = document.getElementById('sidebar-content');
        if (!query.trim()) {
            container.innerHTML = '<div style="padding:20px;text-align:center;color:#999">请输入关键词搜索</div>';
            return;
        }

        const results = readerData.searchIndex.filter(item => 
            item.content.includes(query) || item.title.includes(query)
        );

        if (results.length === 0) {
            container.innerHTML = '<div style="padding:20px;text-align:center;color:#999">未找到相关内容</div>';
            return;
        }

        let html = '<div class="search-results">';
        results.forEach(item => {
            // Create snippet
            const idx = item.content.indexOf(query);
            let snippet = '';
            if (idx !== -1) {
                const start = Math.max(0, idx - 20);
                const end = Math.min(item.content.length, idx + query.length + 40);
                snippet = item.content.substring(start, end);
                snippet = snippet.replace(query, `<span class="highlight">${query}</span>`);
            } else {
                snippet = item.content.substring(0, 60);
            }

            html += `
                <div class="search-item" onclick="window.location.href='${item.link}?q=${encodeURIComponent(query)}'">
                    <div class="search-title">${item.title}</div>
                    <div class="search-snippet">...${snippet}...</div>
                </div>
            `;
        });
        html += '</div>';
        container.innerHTML = html;
    }

    function handleHighlight() {
        const params = new URLSearchParams(window.location.search);
        const query = params.get('q');
        if (query) {
            // Simple highlight implementation
            // Note: This is destructive to HTML structure if not careful. 
            // Ideally use a library like Mark.js, but for now simple replacement in text nodes.
            
            const content = document.querySelector('.content-wrapper');
            if (!content) return;

            // Remove existing highlights if any (though page reload clears them)
            
            // We need to be careful not to break HTML tags.
            // A safe way is to use TreeWalker
            
            const walker = document.createTreeWalker(content, NodeFilter.SHOW_TEXT, null, false);
            const nodes = [];
            while(walker.nextNode()) nodes.push(walker.currentNode);
            
            let found = false;
            for (const node of nodes) {
                if (node.nodeValue.includes(query)) {
                    const span = document.createElement('span');
                    span.innerHTML = node.nodeValue.replace(
                        new RegExp(query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), 
                        `<span class="highlight-match" style="background:yellow;color:black">${query}</span>`
                    );
                    node.parentNode.replaceChild(span, node);
                    found = true;
                }
            }
            
            if (found) {
                setTimeout(() => {
                    const firstMatch = document.querySelector('.highlight-match');
                    if (firstMatch) {
                        firstMatch.scrollIntoView({behavior: 'smooth', block: 'center'});
                    }
                }, 500);
            }
        }
    }

    function initEvents() {
        // Toolbar Buttons
        document.getElementById('btn-toc').addEventListener('click', () => {
            state.sidebarOpen = true;
            document.querySelector('.reader-sidebar').classList.add('active');
            document.querySelector('.reader-overlay').classList.add('active');
            // Reset to TOC tab
            document.querySelector('.sidebar-tab[data-tab="toc"]').click();
        });

        document.getElementById('btn-settings').addEventListener('click', () => {
            state.settingsOpen = !state.settingsOpen;
            document.querySelector('.settings-modal').classList.toggle('active');
            document.querySelector('.reader-overlay').classList.toggle('active', state.settingsOpen);
        });

        document.getElementById('btn-mode').addEventListener('click', () => {
            state.layout = state.layout === 'scroll' ? 'columns' : 'scroll';
            localStorage.setItem('reader_layout', state.layout);
            applyState();
        });

        // Sidebar Close
        document.getElementById('btn-close-sidebar').addEventListener('click', () => {
            state.sidebarOpen = false;
            document.querySelector('.reader-sidebar').classList.remove('active');
            document.querySelector('.reader-overlay').classList.remove('active');
        });

        // Overlay Click
        document.querySelector('.reader-overlay').addEventListener('click', () => {
            state.sidebarOpen = false;
            state.settingsOpen = false;
            document.querySelector('.reader-sidebar').classList.remove('active');
            document.querySelector('.settings-modal').classList.remove('active');
            document.querySelector('.reader-overlay').classList.remove('active');
        });

        // Tabs
        document.querySelectorAll('.sidebar-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                document.querySelectorAll('.sidebar-tab').forEach(t => t.classList.remove('active'));
                e.target.classList.add('active');
                
                const tabName = e.target.dataset.tab;
                const searchBox = document.querySelector('.search-box');
                
                if (tabName === 'search') {
                    searchBox.style.display = 'block';
                    document.getElementById('sidebar-content').innerHTML = '';
                    document.querySelector('.search-input').focus();
                } else {
                    searchBox.style.display = 'none';
                    renderTOC();
                }
            });
        });

        // Search Input
        document.querySelector('.search-input').addEventListener('input', (e) => {
            performSearch(e.target.value);
        });

        // Settings Controls
        document.querySelectorAll('.theme-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                state.theme = e.target.dataset.theme;
                localStorage.setItem('reader_theme', state.theme);
                applyState();
            });
        });

        document.getElementById('font-increase').addEventListener('click', () => {
            if (state.fontSize < 32) {
                state.fontSize += 1;
                localStorage.setItem('reader_fontSize', state.fontSize);
                applyState();
            }
        });

        document.getElementById('font-decrease').addEventListener('click', () => {
            if (state.fontSize > 12) {
                state.fontSize -= 1;
                localStorage.setItem('reader_fontSize', state.fontSize);
                applyState();
            }
        });

        document.getElementById('font-family-select').addEventListener('change', (e) => {
            state.fontFamily = e.target.value;
            localStorage.setItem('reader_fontFamily', state.fontFamily);
            applyState();
        });
    }

    // Initialize
    document.addEventListener('DOMContentLoaded', () => {
        injectUI();
        initEvents();
        applyState();
        renderTOC();
        handleHighlight();
    });

})();
