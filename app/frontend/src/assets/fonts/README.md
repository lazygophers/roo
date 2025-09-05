# 静态字体资源

此目录用于存放应用中使用的字体文件。

## 目录结构

```
src/assets/fonts/
├── icons/          # 图标字体文件
├── web/            # Web字体文件
│   ├── regular/    # 常规字体
│   ├── bold/        # 粗体字体
│   ├── italic/      # 斜体字体
│   └── bolditalic/  # 粗斜体字体
└── variable/       # 可变字体文件
    ├── wght/       # 字重变化
    ├── wdth/       # 字宽变化
    └── slnt/       # 字体倾斜度
```

## 字体格式推荐

1. **WOFF/WOFF2** - 现代Web字体格式，压缩效果好
2. **TTF/OTF** - TrueType/OpenType字体格式
3. **EOT** - 嵌入OpenType字体（旧版IE支持）

## 字体加载优化

```css
/* 在CSS中预加载关键字体 */
@font-face {
  font-family: 'MainFont';
  src: url('@/assets/fonts/web/regular/main-regular.woff2') format('woff2'),
       url('@/assets/fonts/web/regular/main-regular.woff') format('woff');
  font-weight: 400;
  font-style: normal;
  font-display: swap; /* 优化字体加载性能 */
}

/* 定义字体变量 */
:root {
  --font-primary: 'MainFont', sans-serif;
  --font-secondary: 'SecondaryFont', sans-serif;
}
```

## 使用示例

```tsx
import '@/assets/fonts/web/regular/main-regular.woff2';

// 在CSS中使用
body {
  font-family: var(--font-primary);
}

// 在组件中使用
const Title = ({ children }) => (
  <h1 style={{ fontFamily: 'var(--font-primary)' }}>
    {children}
  </h1>
);
```

## 性能优化建议

1. **字体子集化**：只包含需要的字符集
2. **预加载关键字体**：提升首屏渲染速度
3. **使用font-display: swap**：优化字体加载策略
4. **考虑使用系统字体**：减少网络请求
5. **使用CDN分发**：加速字体文件加载