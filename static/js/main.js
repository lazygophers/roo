// 全局变量
let allModels = [];
let searchTerm = '';
let selectedModels = new Set();

// 获取所有模式
async function fetchAllModels() {
    try {
        const response = await fetch('/api/models');
        if (!response.ok) {
            throw new Error('Failed to fetch models');
        }
        const data = await response.json();
        allModels = data.models || [];
        return data;
    } catch (error) {
        console.error('Error fetching models:', error);
        return { models: [] };
    }
}

// 获取所有语言
async function fetchLanguages() {
    try {
        const response = await fetch('/api/languages');
        if (!response.ok) {
            throw new Error('Failed to fetch languages');
        }
        const data = await response.json();
        return data.languages || [];
    } catch (error) {
        console.error('Error fetching languages:', error);
        return [];
    }
}

// 加载语言选项
async function loadLanguageOptions() {
    const languageSelect = document.getElementById('languageSelect');
    languageSelect.innerHTML = '<option value="">加载中...</option>';
    
    try {
        const languages = await fetchLanguages();
        languageSelect.innerHTML = '';
        
        // 获取当前语言，用于确定使用哪种本地化名称
        const currentLang = new URLSearchParams(window.location.search).get('lang') || 'zh-CN';
        
        // 获取当前语言的语言文件，以访问language_switcher部分
        let currentLangNames = {};
        try {
            const response = await fetch(`/static/locales/${currentLang}.json`);
            if (response.ok) {
                const langData = await response.json();
                currentLangNames = langData.language_switcher || {};
            }
        } catch (e) {
            console.warn('Failed to load current language file:', e);
        }
        
        // 语言代码到本地化名称的映射
        const langNames = {
            'zh-CN': currentLangNames.chinese || '中文',
            'en': currentLangNames.english || 'English',
            'ja': currentLangNames.japanese || '日本語',
            'fr': currentLangNames.french || 'Français',
            'ar': currentLangNames.arabic || 'العربية',
            'ru': currentLangNames.russian || 'Русский',
            'es': currentLangNames.spanish || 'Español',
            'zh-TW': currentLangNames.traditional_chinese || '繁體中文'
        };
        
        languages.forEach(lang => {
            const option = document.createElement('option');
            option.value = lang.code;
            // 使用本地化语言名称
            option.textContent = langNames[lang.code] || lang.name;
            languageSelect.appendChild(option);
        });
        
        // 设置当前语言
        languageSelect.value = currentLang;
        
    } catch (error) {
        console.error('Error loading language options:', error);
        languageSelect.innerHTML = '<option value="">加载失败</option>';
    }
}

// 渲染模式卡片
function renderModeCards() {
    const container = document.getElementById('modeCheckboxes');
    container.innerHTML = '';
    
    // 过滤模式
    const filteredModels = allModels.filter(mode => {
        if (!searchTerm) return true;
        const term = searchTerm.toLowerCase();
        return mode.name.toLowerCase().includes(term) ||
               mode.slug.toLowerCase().includes(term);
    });
    
    // 添加动画延迟
    filteredModels.forEach((model, index) => {
        const div = document.createElement('div');
        div.className = `mode-checkbox ${model.required ? 'required' : ''}`;
        div.style.animationDelay = `${index * 0.05}s`;
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `mode-${model.slug}`;
        checkbox.value = model.slug;
        checkbox.checked = model.required || selectedModels.has(model.slug);
        checkbox.disabled = model.required;
        
        const label = document.createElement('label');
        label.htmlFor = `mode-${model.slug}`;
        label.innerHTML = `
            <div class="mode-name">${model.name}</div>
            <div class="mode-slug">${model.slug}</div>
        `;
        
        div.appendChild(checkbox);
        div.appendChild(label);
        
        // 为整个卡片添加点击事件
        div.addEventListener('click', (e) => {
            // 如果点击的是复选框，不处理，让原生事件处理
            if (e.target.type === 'checkbox') {
                return;
            }
            
            // 对于必需模式且已选中，不允许取消
            if (model.required && checkbox.checked) {
                return;
            }
            
            // 阻止事件冒泡，避免触发复选框的默认行为
            e.preventDefault();
            e.stopPropagation();
            
            // 切换复选框状态
            const newState = !checkbox.checked;
            checkbox.checked = newState;
            
            // 触发 change 事件，确保状态同步
            const changeEvent = new Event('change', { bubbles: true });
            checkbox.dispatchEvent(changeEvent);
        });
        
        // 为复选框添加 change 事件（统一处理状态变化）
        checkbox.addEventListener('change', (e) => {
            // 如果是必需模式且试图取消选中，阻止
            if (model.required && !e.target.checked) {
                e.target.checked = true;
                e.stopPropagation();
                return;
            }
            
            // 更新选中状态集合
            if (e.target.checked) {
                selectedModels.add(model.slug);
            } else {
                selectedModels.delete(model.slug);
            }
            
            // 更新样式类
            if (e.target.checked) {
                div.classList.add('selected');
            } else {
                div.classList.remove('selected');
            }
            
            // 更新右侧详情展示
            updateModeDetails();
        });
        
        // 阻止标签点击事件冒泡到卡片
        label.addEventListener('click', (e) => {
            e.stopPropagation();
        });
        
        container.appendChild(div);
    });
}

// 更新模式详情展示
function updateModeDetails() {
    const detailsContainer = document.getElementById('modeDetails');
    detailsContainer.innerHTML = '';
    
    // 获取所有选中的模式（包括必需模式）
    const selectedModeData = allModels.filter(model =>
        model.required || selectedModels.has(model.slug)
    );
    
    if (selectedModeData.length === 0) {
        detailsContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📋</div>
                <p>请选择至少一个模式查看详情</p>
                <p class="empty-subtitle">点击左侧模式卡片开始探索</p>
            </div>
        `;
        return;
    }
    
    // 为每个选中的模式创建详情卡片
    selectedModeData.forEach((model, index) => {
        const detailCard = document.createElement('div');
        detailCard.className = 'mode-detail-card';
        detailCard.style.animationDelay = `${index * 0.1}s`;
        
        // 获取模式图标
        const modeIcon = getModelIcon(model.slug);
        
        detailCard.innerHTML = `
            <div class="detail-header">
                <div class="detail-title">
                    <span class="mode-icon">${modeIcon}</span>
                    <h3>${model.name}</h3>
                    ${model.required ? '<span class="required-badge">必需</span>' : ''}
                </div>
                <div class="mode-slug-detail">${model.slug}</div>
            </div>
            <div class="detail-content">
                <div class="detail-section">
                    <h4>🎭 角色定义</h4>
                    <p>${model.roleDefinition || '暂无角色定义'}</p>
                </div>
                <div class="detail-section">
                    <h4>📝 描述</h4>
                    <p>${model.description || '暂无描述'}</p>
                </div>
                <div class="detail-section">
                    <h4>⏰ 使用时机</h4>
                    <p>${model.whenToUse || '暂无使用时机说明'}</p>
                </div>
                <div class="detail-section">
                    <h4>🎯 核心职责</h4>
                    <ul>
                        ${(model.core_responsibilities || ['暂无职责信息']).map(resp =>
                            `<li>${resp}</li>`
                        ).join('')}
                    </ul>
                </div>
                <div class="detail-section">
                    <h4>🛠️ 工具权限</h4>
                    <div class="tool-permissions">
                        ${model.tool_permissions && model.tool_permissions.length > 0
                            ? model.tool_permissions.map(tool => `
                                <span class="tool-tag">${tool}</span>
                            `).join('')
                            : '<span class="no-tools">无特殊工具权限</span>'
                        }
                    </div>
                </div>
                ${model.groups && model.groups.length > 0 ? `
                <div class="detail-section">
                    <h4>🏷️ 分组标签</h4>
                    <div class="tool-permissions">
                        ${model.groups.map(group => `
                            <span class="tool-tag">${group}</span>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
            </div>
        `;
        
        detailsContainer.appendChild(detailCard);
    });
}

// 获取模式图标
function getModelIcon(slug) {
    const iconMap = {
        'orchestrator': '🧠',
        'architect': '🏗️',
        'code': '🪄',
        'ask': '📚',
        'debug': '🔬',
        'doc-writer': '✍️',
        'giter': '⚙️',
        'researcher': '📚',
        'project-research': '🔍',
        'mode-writer': '✍️',
        'memory': '🧠'
    };
    return iconMap[slug] || '🎯';
}

// 搜索功能
document.getElementById('searchInput')?.addEventListener('input', (e) => {
    searchTerm = e.target.value;
    renderModeCards();
});

// 语言切换
function changeLanguage(lang) {
    console.log('Language changed to:', lang);
    // 跳转到对应语言的页面
    const url = new URL(window.location);
    url.searchParams.set('lang', lang);
    window.location.href = url.toString();
}

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
    // 加载语言选项
    await loadLanguageOptions();
    
    // 加载模式列表
    const response = await fetchAllModels();
    
    // 初始化选中状态（必需模式默认选中）
    allModels.forEach(model => {
        if (model.required) {
            selectedModels.add(model.slug);
        }
    });
    
    renderModeCards();
    updateModeDetails();
    
    // 绑定事件
    const languageSelect = document.getElementById('languageSelect');
    if (languageSelect) {
        languageSelect.addEventListener('change', (e) => {
            changeLanguage(e.target.value);
        });
    }
    
    // 初始化选中状态的样式
    document.querySelectorAll('.mode-checkbox input[type="checkbox"]:checked').forEach(checkbox => {
        checkbox.closest('.mode-checkbox').classList.add('selected');
    });
});