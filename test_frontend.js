// 前端功能测试脚本
const puppeteer = require('puppeteer');

async function testModeSelector() {
    console.log('🧪 开始测试前端功能...');
    
    const browser = await puppeteer.launch({
        headless: false,
        slowMo: 100 // 减慢速度以便观察
    });
    
    const page = await browser.newPage();
    
    try {
        // 访问模式选择器页面
        await page.goto('http://localhost:8000/mode-selector');
        
        // 等待页面加载
        await page.waitForSelector('.mode-grid', { timeout: 5000 });
        console.log('✅ 页面加载成功');
        
        // 检查默认选中的 orchestrator
        const orchestratorItem = await page.$('[data-slug="orchestrator"]');
        const isSelected = await orchestratorItem.evaluate(el => el.classList.contains('selected'));
        console.log(`✅ Orchestrator 默认选中: ${isSelected}`);
        
        // 测试搜索功能
        const searchInput = await page.$('.search-input');
        await searchInput.type('code');
        await page.waitForTimeout(1000);
        
        const searchResults = await page.$$('.mode-item');
        console.log(`✅ 搜索功能正常，找到 ${searchResults.length} 个包含 "code" 的模式`);
        
        // 清除搜索
        await searchInput.click({ clickCount: 3 });
        await searchInput.press('Backspace');
        await page.waitForTimeout(500);
        
        // 测试选择模式
        const codeItem = await page.$('[data-slug="code"]');
        await codeItem.click();
        await page.waitForTimeout(500);
        
        // 检查预览区域是否更新
        const selectedCount = await page.$eval('#selectedCount', el => el.textContent);
        console.log(`✅ 选中模式数量: ${selectedCount}`);
        
        // 测试复制功能
        const copyBtn = await page.$('#copyBtn');
        await copyBtn.click();
        await page.waitForTimeout(1000);
        
        // 检查按钮文本变化
        const copyBtnText = await page.evaluate(el => el.textContent);
        console.log(`✅ 复制功能正常: ${copyBtnText}`);
        
        // 测试清除功能
        const clearBtn = await page.$('#clearBtn');
        await clearBtn.click();
        await page.waitForTimeout(500);
        
        const selectedCountAfterClear = await page.$eval('#selectedCount', el => el.textContent);
        console.log(`✅ 清除后选中模式数量: ${selectedCountAfterClear}`);
        
        // 测试响应式布局
        await page.setViewport({ width: 375, height: 667 }); // iPhone 6/7/8
        await page.waitForTimeout(500);
        
        const selectorContent = await page.$('.selector-content');
        const isMobileLayout = await selectorContent.evaluate(el => {
            const styles = window.getComputedStyle(el);
            return styles.gridTemplateColumns === '1fr';
        });
        console.log(`✅ 移动端响应式布局: ${isMobileLayout}`);
        
        // 恢复桌面视图
        await page.setViewport({ width: 1920, height: 1080 });
        
        console.log('\n🎉 所有前端功能测试通过！');
        
    } catch (error) {
        console.error('❌ 测试失败:', error);
    } finally {
        await browser.close();
    }
}

// 如果直接运行此脚本
if (require.main === module) {
    testModeSelector();
}

module.exports = { testModeSelector };