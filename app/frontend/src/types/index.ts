export interface Model {
  slug: string
  name: string
  description?: string
  category?: string
  tags?: string[]
  _path: string
}

export interface Rule {
  name: string
  content: string
  metadata?: {
    title?: string
    description?: string
    category?: string
    priority?: string
    tags?: string[]
  }
}

export interface Command {
  name: string
  content: string
  metadata?: {
    title?: string
    description?: string
    category?: string
    usage?: string
    examples?: string[]
  }
}

export interface Role {
  name: string
  content: string
  metadata?: {
    title?: string
    description?: string
    traits?: string[]
    features?: string[]
  }
}

export interface SelectedConfig {
  model: Model | null
  rules: Rule[]
  roles: Role[]
  commands: Command[]
  hooks: {
    before: string
    after: string
    beforeMetadata?: any
    afterMetadata?: any
  }
}

// 元数据接口
export interface Metadata {
  title?: string
  description?: string
  category?: string
  priority?: string
  tags?: string[]
  traits?: string[]
  features?: string[]
  usage?: string
  examples?: string[]
}

export interface ApiResponse<T> {
  data: T
  status: string
}