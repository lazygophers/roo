---
name: react-guide
title: React开发规范指南
description: "React开发规范和最佳实践"
category: 语言指南
language: react
priority: high
tags: [React, TypeScript, JSX]
---

# React 开发规范

## 🔧 技术栈
- **框架**: React 18+, Next.js
- **语言**: TypeScript
- **状态**: Redux Toolkit, Zustand
- **样式**: Tailwind CSS, styled-components

## 📝 命名规范
| 类型 | 规范 | 示例 |
|------|------|------|
| 组件文件 | PascalCase + .tsx | `UserCard.tsx` |
| 组件名 | PascalCase | `UserCard` |
| Props接口 | PascalCase + Props | `UserCardProps` |
| Hooks | use + camelCase | `useUserData` |

## 📁 文件结构
```
/components
└── /UserCard
    ├── UserCard.tsx
    ├── UserCard.module.css
    └── UserCard.test.tsx
```

## 🏷️ TypeScript接口定义
```tsx
interface UserCardProps {
    user: User;
    onEdit?: () => void;
    isLoading?: boolean;
    className?: string;
}

const UserCard: React.FC<UserCardProps> = ({ 
    user, 
    onEdit, 
    isLoading = false,
    className 
}) => {
    return <div className={className}>...</div>;
};
```

## 🔄 Hooks使用
```tsx
// 自定义Hook
const useUserData = (userId: string) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        fetchUser(userId).then(setUser).finally(() => setLoading(false));
    }, [userId]);
    
    return { user, loading };
};
```

## 🧪 测试规范
```tsx
import { render, screen } from '@testing-library/react';
import UserCard from './UserCard';

test('renders user name', () => {
    const user = { name: '张三', email: 'zhang@example.com' };
    render(<UserCard user={user} />);
    expect(screen.getByText('张三')).toBeInTheDocument();
});
```

## ✅ 核心要求
- 使用TypeScript定义Props接口
- 组件命名与文件名一致
- 每个文件只导出一个组件
- 自定义Hook以use开头
- 编写对应测试文件
