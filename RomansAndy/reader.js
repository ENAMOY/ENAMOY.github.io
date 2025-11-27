
(function() {
    // State
    const state = {
        theme: localStorage.getItem('reader_theme') || 'light',
        fontSize: parseInt(localStorage.getItem('reader_fontSize')) || 19,
        layout: localStorage.getItem('reader_layout') || 'scroll',
        sidebarOpen: false,
        settingsOpen: false,
        searchQuery: ''
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
            <div class="reader-btn" id="btn-home" title="首页" onclick="window.location.href='index.html'"><i class="fas fa-home"></i></div>
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
        body.style.fontSize = `${state.fontSize}px`;
        const display = document.getElementById('font-size-display');
        if(display) display.textContent = state.fontSize;

        // Layout
        if (state.layout === 'columns') {
            body.classList.add('two-column-mode');
        } else {
            body.classList.remove('two-column-mode');
        }
    }

    function bindEvents() {
        // Toolbar
        document.getElementById('btn-toc').onclick = () => toggleSidebar(true);
        document.getElementById('btn-settings').onclick = () => toggleSettings();
        document.getElementById('btn-mode').onclick = () => toggleLayout();
        
        // Sidebar
        document.getElementById('btn-close-sidebar').onclick = () => toggleSidebar(false);
        document.querySelector('.reader-overlay').onclick = () => {
            toggleSidebar(false);
            toggleSettings(false);
        };

        // Tabs
        document.querySelectorAll('.sidebar-tab').forEach(tab => {
            tab.onclick = (e) => {
                document.querySelectorAll('.sidebar-tab').forEach(t => t.classList.remove('active'));
                e.target.classList.add('active');
                const mode = e.target.dataset.tab;
                if (mode === 'toc') {
                    document.querySelector('.search-box').style.display = 'none';
                    renderTOC();
                } else {
                    document.querySelector('.search-box').style.display = 'block';
                    document.querySelector('.search-input').focus();
                    renderSearchResults(); // Render empty or previous results
                }
            };
        });

        // Search
        const searchInput = document.querySelector('.search-input');
        let debounceTimer;
        searchInput.oninput = (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                state.searchQuery = e.target.value;
                renderSearchResults();
            }, 300);
        };

        // Settings
        document.querySelectorAll('.theme-btn').forEach(btn => {
            btn.onclick = () => {
                state.theme = btn.dataset.theme;
                localStorage.setItem('reader_theme', state.theme);
                applyState();
            };
        });

        document.getElementById('font-increase').onclick = () => {
            state.fontSize = Math.min(state.fontSize + 2, 32);
            localStorage.setItem('reader_fontSize', state.fontSize);
            applyState();
        };

        document.getElementById('font-decrease').onclick = () => {
            state.fontSize = Math.max(state.fontSize - 2, 12);
            localStorage.setItem('reader_fontSize', state.fontSize);
            applyState();
        };
        
        document.getElementById('font-family-select').onchange = (e) => {
            const val = e.target.value;
            if(val === 'sans') {
                document.body.style.fontFamily = 'var(--font-sans)';
            } else {
                document.body.style.fontFamily = 'var(--font-serif)';
            }
        };
    }

    function toggleSidebar(show) {
        state.sidebarOpen = show !== undefined ? show : !state.sidebarOpen;
        document.querySelector('.reader-sidebar').classList.toggle('active', state.sidebarOpen);
        document.querySelector('.reader-overlay').classList.toggle('active', state.sidebarOpen);
        if (state.sidebarOpen) {
            toggleSettings(false);
            if (!document.getElementById('sidebar-content').hasChildNodes()) {
                renderTOC();
            }
        }
    }

    function toggleSettings(show) {
        state.settingsOpen = show !== undefined ? show : !state.settingsOpen;
        document.querySelector('.settings-modal').classList.toggle('active', state.settingsOpen);
        if (state.settingsOpen) {
            // toggleSidebar(false); // Optional: close sidebar when settings open
        }
    }

    function toggleLayout() {
        state.layout = state.layout === 'scroll' ? 'columns' : 'scroll';
        localStorage.setItem('reader_layout', state.layout);
        applyState();
    }

    function loadData() {
        // Check if BOOK_DATA is loaded
        if (window.BOOK_DATA) {
            // Data already loaded via script tag
            return;
        }
        // If not, maybe fetch it? But we are using script tag injection.
        // Just in case, we can try to fetch reader_data.js
    }

    function renderTOC() {
        const container = document.getElementById('sidebar-content');
        container.innerHTML = '';
        if (!window.BOOK_DATA || !window.BOOK_DATA.toc) return;

        const currentPath = window.location.pathname.split('/').pop();

        window.BOOK_DATA.toc.forEach(item => {
            const a = document.createElement('a');
            a.className = 'toc-item';
            a.href = item.url;
            a.textContent = item.title;
            if (item.url === currentPath) {
                a.classList.add('active');
            }
            container.appendChild(a);
        });
    }

    function renderSearchResults() {
        const container = document.getElementById('sidebar-content');
        container.innerHTML = '';
        const query = state.searchQuery.toLowerCase();
        
        if (!query) {
            container.innerHTML = '<div style="padding:20px;color:#999;text-align:center">输入关键词搜索</div>';
            return;
        }

        if (!window.BOOK_DATA || !window.BOOK_DATA.search_index) return;

        const results = window.BOOK_DATA.search_index.filter(item => {
            return item.title.toLowerCase().includes(query) || item.content.toLowerCase().includes(query);
        });

        if (results.length === 0) {
            container.innerHTML = '<div style="padding:20px;color:#999;text-align:center">未找到相关内容</div>';
            return;
        }

        results.forEach(item => {
            const div = document.createElement('div');
            div.className = 'search-result';
            div.onclick = () => window.location.href = item.url;
            
            // Create snippet
            let snippet = '';
            const contentLower = item.content.toLowerCase();
            const idx = contentLower.indexOf(query);
            if (idx > -1) {
                const start = Math.max(0, idx - 20);
                const end = Math.min(item.content.length, idx + 40);
                snippet = '...' + item.content.substring(start, end) + '...';
            } else {
                snippet = item.content.substring(0, 60) + '...';
            }

            div.innerHTML = `
                <div class="result-title">${item.title}</div>
                <div class="result-snippet">${snippet}</div>
            `;
            container.appendChild(div);
        });
    }

    // Initialize
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
