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
}

export interface Command {
  name: string
  content: string
}

export interface Role {
  name: string
  content: string
}

export interface SelectedConfig {
  model: Model | null
  rules: Rule[]
  roles: Role[]
  commands: Command[]
  hooks: {
    before: string
    after: string
  }
}

export interface ApiResponse<T> {
  data: T
  status: string
}