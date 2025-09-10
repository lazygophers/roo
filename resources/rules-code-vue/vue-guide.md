---
name: vue-guide
title: Vue.js官方风格指南
description: "Vue.js官方风格指南完整版，提供优先级分类的规范和最佳实践，涵盖必要规则、强烈推荐、推荐使用和谨慎使用等多个级别"
category: language-guide
language: vue
priority: high
tags: [Vue.js, 风格指南, 官方规范, 最佳实践]
sections:
  - "优先级A（必要）：组件命名、data函数、v-for的key、避免v-if/v-for同用、scoped样式"
  - "优先级B（强烈推荐）：组件文件、单文件组件命名、Prop定义、属性分行"
  - "优先级C（推荐）：选项顺序、attribute顺序、组件和v-for的key"
  - "优先级D（谨慎使用）：v-html、scoped元素选择器、隐式父子通信"
priority_levels:
  - "A：必要（避免错误）"
  - "B：强烈推荐（提高可读性）"
  - "C：推荐（保持一致）"
  - "D：谨慎使用（潜在风险）"
references:
  - "Vue.js官方风格指南"
---

# Vue.js 官方风格指南

## 🔧 技术栈
- Vue 3.x, Vite, TypeScript, Pinia
- UI: Element Plus, Tailwind CSS
- 工具: ESLint, Prettier, Vue DevTools

## 📝 命名规范

| 元素 | 命名法 | 示例 |
|------|--------|------|
| 组件名 | `PascalCase` (多单词) | `UserProfile.vue` |
| 组件文件 | `PascalCase/kebab-case` | `UserList.vue` |
| Props | `camelCase` | `userName`, `isVisible` |
| 事件名 | `kebab-case` | `@user-updated` |
| 变量/方法 | `camelCase` | `handleClick`, `userData` |
| 常量 | `SCREAMING_SNAKE_CASE` | `API_BASE_URL` |

## 🏷️ 类型/接口定义

```vue
<template>
  <div class="user-card">
    <h3>{{ user.name }}</h3>
    <button @click="handleUpdate">Update</button>
    <ul>
      <li v-for="item in items" :key="item.id">
        {{ item.title }}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
interface User {
  id: number;
  name: string;
  email: string;
}

const props = defineProps<{
  user: User;
  items: Array<{ id: number; title: string }>;
}>();

const emit = defineEmits<{
  userUpdated: [user: User];
}>();
</script>

<style scoped>
.user-card {
  padding: 1rem;
  border: 1px solid #ddd;
}
</style>
```

## 🧪 测试规范

```javascript
// UserComponent.spec.js
import { mount } from '@vue/test-utils';
import UserComponent from '@/components/UserComponent.vue';

describe('UserComponent', () => {
  it('renders user data correctly', () => {
    const user = { id: 1, name: 'John' };
    const wrapper = mount(UserComponent, {
      props: { user }
    });
    
    expect(wrapper.text()).toContain('John');
    expect(wrapper.find('.user-card').exists()).toBe(true);
  });
});
```

## ✅ 核心要求
- 组件名必须是多单词（除App外）
- `data`必须是函数，返回对象
- `v-for`必须配合`:key`使用
- 避免`v-if`和`v-for`同时使用
- 样式使用`scoped`或CSS Modules
- Props定义要详细，包含类型和验证
- 遵循"props down, events up"原则
- 避免使用`v-html`和直接DOM操作
