# 静态图片资源

此目录用于存放应用中使用的静态图片资源。

## 目录结构

```
src/assets/images/
├── icons/          # 图标文件
│   ├── logo.svg    # 应用logo
│   ├── favicon.ico # 网站图标
│   └── ...         # 其他图标
├── avatars/        # 头像图片
├── backgrounds/    # 背景图片
├── illustrations/  # 插图和示意图
└── screenshots/    # 截图
```

## 图片优化建议

1. **使用现代格式**：优先使用 WebP、AVIF 等现代图片格式
2. **响应式图片**：使用 `srcset` 和 `sizes` 属性提供不同尺寸的图片
3. **懒加载**：对非首屏图片使用懒加载
4. **压缩优化**：使用工具压缩图片大小
5. **CDN加速**：考虑使用CDN分发图片资源

## 使用示例

```tsx
import React from 'react';
import logo from '@/assets/images/icons/logo.svg';

const Logo = () => {
  return (
    <img 
      src={logo} 
      alt="应用Logo" 
      className="logo"
      loading="lazy"
    />
  );
};