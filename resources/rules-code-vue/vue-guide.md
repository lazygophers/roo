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

本指南旨在提供一套统一的 Vue.js 代码风格规范，以提高代码的可读性、可维护性和团队协作效率。

[TOC]

## 优先级 A：必要 (Essential)

这些规则有助于避免错误，因此请务必学习并遵守。

### A.1 组件名为多个单词

**我自定义的组件名应始终为多个单词，根组件 `App` 除外。**

这可以避免与未来的 HTML 元素产生命名冲突，因为所有的 HTML 元素名称都是单个单词。

```vue
<!-- 不推荐 -->
<script>
export default {
  name: "Item",
  // ...
};
</script>

<!-- 推荐 -->
<script>
export default {
  name: "TodoItem",
  // ...
};
</script>
```

### A.2 组件 data 必须是函数

**在组件中，`data` 选项必须是一个函数。**

当在一个组件中使用 `data` 属性时 (除了 `new Vue` 创建的根实例)，它的值必须是返回一个对象的函数。这可以防止多个组件实例共享同一个数据对象，从而避免状态污染。

```vue
<!-- 不推荐 -->
<script>
export default {
  data: {
    message: "Hello",
  },
};
</script>

<!-- 推荐 -->
<script>
export default {
  data() {
    return {
      message: "Hello",
    };
  },
};
</script>
```

### A.3 `v-for` 必须有 `key`

**总是用 `key` 搭配 `v-for`。**

`key` 属性可以帮助 Vue 跟踪每个节点的身份，从而高效地重用和重新排序元素。这对于维护组件或元素的状态至关重要。

```vue
<template>
  <div>
    <!-- 不推荐 -->
    <ul>
      <li v-for="todo in todos">
        {{ todo.text }}
      </li>
    </ul>

    <!-- 推荐 -->
    <ul>
      <li v-for="todo in todos" :key="todo.id">
        {{ todo.text }}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      todos: [
        { id: 1, text: "Learn Vue" },
        { id: 2, text: "Build something awesome" },
      ],
    };
  },
};
</script>
```

### A.4 避免 `v-if` 和 `v-for` 一起使用

**永远不要在同一个元素上同时使用 `v-if` 和 `v-for`。**

`v-for` 的优先级高于 `v-if`，这意味着 `v-if` 将分别重复运行于每个循环中。这会带来不必要的性能开销。

```vue
<!-- 不推荐 -->
<ul>
  <li
    v-for="user in users"
    v-if="user.isActive"
    :key="user.id"
  >
    {{ user.name }}
  </li>
</ul>

<!-- 推荐 -->
<template>
  <ul v-if="activeUsers.length">
    <li v-for="user in activeUsers" :key="user.id">
      {{ user.name }}
    </li>
  </ul>
</template>

<script>
export default {
  data() {
    return {
      users: [
        { id: 1, name: "Alice", isActive: true },
        { id: 2, name: "Bob", isActive: false },
        { id: 3, name: "Charlie", isActive: true },
      ],
    };
  },
  computed: {
    activeUsers() {
      return this.users.filter((user) => user.isActive);
    },
  },
};
</script>
```

### A.5 组件样式应设为局部

**对于应用，顶级 `App` 组件和布局组件中的样式可以是全局的，但所有其他组件都应该有自己的作用域。**

这可以防止样式泄露到其他组件，确保组件样式的独立性和可维护性。

```vue
<!-- 不推荐：全局样式 -->
<style>
.btn-danger {
  background-color: red;
}
</style>

<!-- 推荐：局部样式 -->
<style scoped>
.btn-primary {
  background-color: blue;
}
</style>
```

---

## 优先级 B：强烈推荐 (Strongly Recommended)

这些规则可以极大地提高代码的可读性和可维护性。

### B.1 组件文件

**只要有能够拼接文件的构建系统，就把每个组件单独分成文件。**

这能帮助你更快速地找到一个组件的定义。

```js
// 不推荐: 在一个文件中定义多个组件
Vue.component('TodoList', {
  // ...
})

Vue.component('TodoItem', {
  // ...
})

// 推荐: 每个组件一个文件
// file: components/TodoList.vue
export default {
  name: 'TodoList',
  // ...
}

// file: components/TodoItem.vue
export default {
  name: 'TodoItem',
  // ...
}
```

### B.2 单文件组件文件的大小写

**单文件组件的文件名应该要么始终是单词大写开头 (PascalCase)，要么始终是横线连接 (kebab-case)。**

单词大写开头 (PascalCase) 的文件名在代码编辑器中更容易识别。

```
// 不推荐
components/
|- my-component.vue
|- myComponent.vue

// 推荐
components/
|- MyComponent.vue
// or
components/
|- my-component.vue
```

### B.3 Prop 定义应尽量详细

**Prop 定义应尽量详细，至少需要指定其类型。**

这使得组件的 API 更加清晰，并在开发过程中提供有用的警告信息。

```javascript
// 不推荐
props: ['status']

// 推荐
props: {
  status: String
}

// 强烈推荐
props: {
  status: {
    type: String,
    required: true,
    validator: function (value) {
      return [
        'syncing',
        'synced',
        'version-conflict',
        'error'
      ].indexOf(value) !== -1
    }
  }
}
```

### B.4 元素/组件的多个属性应分行

**拥有多个属性的元素，应每个属性占据一行，以提高可读性。**

```vue
<!-- 不推荐 -->
<img src="https://vuejs.org/images/logo.png" alt="Vue Logo">

<MyComponent
  foo="1" bar="2"
  baz="3">
</MyComponent>

<!-- 推荐 -->
<img
  src="https://vuejs.org/images/logo.png"
  alt="Vue Logo"
>

<MyComponent
  :foo="1"
  :bar="2"
  :baz="3"
/>
```

---

## 优先级 C：推荐 (Recommended)

这些规则旨在确保样式和模式的一致性，使得代码更易于维护。

### C.1 组件/实例的选项的顺序

**组件/实例的选项应该有统一的顺序。**

这是我们推荐的默认顺序：

1.  **副作用** (Side Effects), e.g. `el`
2.  **全局感知** (Global Awareness), e.g. `name`, `parent`
3.  **组件类型** (Component Type), e.g. `functional`
4.  **模板修改器** (Template Modifiers), e.g. `delimiters`, `comments`
5.  **模板依赖** (Template Dependencies), e.g. `components`, `directives`, `filters`
6.  **组合** (Composition), e.g. `extends`, `mixins`
7.  **接口** (Interface), e.g. `inheritAttrs`, `model`, `props`/`propsData`
8.  **本地状态** (Local State), e.g. `data`, `computed`
9.  **事件** (Events), e.g. `watch`, Lifecycle Events
10. **非响应式属性** (Non-Reactive Properties), e.g. `methods`
11. **渲染** (Rendering), e.g. `template`/`render`, `renderError`

### C.2 元素 attribute 的顺序

**HTML attribute 的顺序应保持一致。**

推荐的顺序是：

1.  **定义** (e.g. `is`)
2.  **列表渲染** (e.g. `v-for`)
3.  **条件渲染** (e.g. `v-if`, `v-else-if`, `v-else`, `v-show`, `v-cloak`)
4.  **渲染方式** (e.g. `v-pre`, `v-once`)
5.  **全局感知** (e.g. `id`)
6.  **唯一性** (e.g. `ref`, `key`)
7.  **双向绑定** (e.g. `v-model`)
8.  **其它 Attribute** (所有未列出的 attribute)
9.  **事件** (e.g. `@click`)
10. **内容** (e.g. `v-html`, `v-text`)

### C.3 组件和 `v-for` 的 `key`

**在组件上使用 `v-for` 时，总是应该带上 `key`。**

这与在普通元素上使用 `key` 的原因相同，可以维护状态，提高渲染效率。

```vue
<!-- 不推荐 -->
<MyComponent v-for="item in items" />

<!-- 推荐 -->
<MyComponent v-for="item in items" :key="item.id" />
```

---

## 优先级 D：谨慎使用 (Use with Caution)

这些特性存在潜在风险，只应在少数特殊情况下使用。

### D.1 `v-html`

**应避免使用 `v-html`，因为它可能导致 XSS 攻击。**

只在可信内容上使用 `v-html`，绝不要将其用于我提交的内容。

### D.2 避免在 `scoped` 中使用元素选择器

**在 `scoped` 样式中，应优先使用类选择器，而不是元素选择器。**

为了实现局部作用域，Vue 会为组件的元素添加一个唯一的 `data` 属性（如 `data-v-f3f3eg9`）。然后，样式选择器会被修改，以确保它们只作用于带有这个特定属性的元素。相比类选择器（如 `.btn-close[data-v-f3f3eg9]`），大量的元素属性选择器（如 `button[data-v-f3f3eg9]`）会慢得多。

```vue
&lt;!-- 不推荐 --&gt; &lt;template&gt; &lt;button&gt;×&lt;/button&gt;
&lt;/template&gt; &lt;style scoped&gt; button { background-color: red; }
&lt;/style&gt; &lt;!-- 推荐 --&gt; &lt;template&gt; &lt;button class="btn
btn-close"&gt;×&lt;/button&gt; &lt;/template&gt; &lt;style scoped&gt; .btn-close
{ background-color: red; } &lt;/style&gt;
```

### D.3 避免隐式的父子组件通信

**应优先使用 `props` 和 `events` 进行父子组件通信，而不是 `this.$parent` 或直接修改 prop。**

一个理想的 Vue 应用遵循“props down, events up” (属性向下传递，事件向上传递) 的单向数据流原则。这使得组件的状态流更易于理解和维护。虽然在某些深度耦合的组件场景下，`this.$parent` 或修改 prop 可能带来一时的便利，但这通常是以牺牲代码清晰度为代价的。

```javascript
// 不推荐
// child-component.js
export default {
  props: {
    user: {
      type: Object,
      required: true
    }
  },
  methods: {
    updateUserName() {
      // 直接修改 prop，违反了单向数据流
      this.user.name = 'New Name';
    }
  }
}

// 推荐
// child-component.js
export default {
  props: {
    user: {
      type: Object,
      required: true
    }
  },
  methods: {
    updateUserName() {
      // 发送事件，让父组件来处理状态变更
      this.$emit('update:userName', 'New Name');
    }
  }
}
```
