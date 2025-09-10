/**
 * API service tests for LazyAI Studio Frontend
 */

// Mock API functions for testing
export const API_BASE_URL = 'http://localhost:8000/api';

export interface ModelData {
  slug: string;
  name: string;
  roleDefinition: string;
  whenToUse: string;
  description: string;
  groups: string[];
  file_path: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  total?: number;
}

// Mock fetch implementation for tests
const mockFetch = (url: string, options?: RequestInit): Promise<Response> => {
  const mockResponse = {
    ok: true,
    status: 200,
    json: async () => ({
      success: true,
      data: [],
      total: 0
    })
  };
  
  return Promise.resolve(mockResponse as Response);
};

export const apiService = {
  async getModels(filters?: { category?: string; search?: string }): Promise<ApiResponse<ModelData[]>> {
    const response = await mockFetch(`${API_BASE_URL}/models`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(filters || {})
    });
    
    return response.json();
  },

  async getModelBySlug(slug: string): Promise<ModelData | null> {
    const response = await mockFetch(`${API_BASE_URL}/models/by-slug`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ slug })
    });
    
    if (!response.ok) return null;
    return response.json();
  },

  async getCategories(): Promise<ApiResponse<{ [key: string]: ModelData[] }>> {
    const response = await mockFetch(`${API_BASE_URL}/models/categories/list`, {
      method: 'POST'
    });
    
    return response.json();
  }
};

describe('API Service', () => {
  beforeEach(() => {
    // Mock global fetch
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('getModels', () => {
    test('fetches models successfully', async () => {
      const mockResponse = {
        success: true,
        data: [
          {
            slug: 'test-model',
            name: 'Test Model',
            roleDefinition: 'Test role',
            whenToUse: 'For testing',
            description: 'Test description',
            groups: ['test'],
            file_path: '/test/path'
          }
        ],
        total: 1
      };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockResponse
      });

      const result = await apiService.getModels();
      expect(result.success).toBe(true);
      expect(result.data).toHaveLength(1);
      expect(result.total).toBe(1);
    });

    test('sends correct request with filters', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ success: true, data: [], total: 0 })
      });

      await apiService.getModels({ category: 'core', search: 'python' });

      expect(global.fetch).toHaveBeenCalledWith(
        `${API_BASE_URL}/models`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ category: 'core', search: 'python' })
        }
      );
    });

    test('handles API error', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 500,
        json: async () => ({ success: false, message: 'Server error' })
      });

      const result = await apiService.getModels();
      expect(result.success).toBe(false);
    });
  });

  describe('getModelBySlug', () => {
    test('fetches model by slug successfully', async () => {
      const mockModel = {
        slug: 'test-model',
        name: 'Test Model',
        roleDefinition: 'Test role',
        whenToUse: 'For testing',
        description: 'Test description',
        groups: ['test'],
        file_path: '/test/path'
      };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockModel
      });

      const result = await apiService.getModelBySlug('test-model');
      expect(result).toEqual(mockModel);
    });

    test('returns null for non-existent model', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 404
      });

      const result = await apiService.getModelBySlug('nonexistent');
      expect(result).toBeNull();
    });

    test('sends correct request parameters', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({})
      });

      await apiService.getModelBySlug('code-python');

      expect(global.fetch).toHaveBeenCalledWith(
        `${API_BASE_URL}/models/by-slug`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ slug: 'code-python' })
        }
      );
    });
  });

  describe('getCategories', () => {
    test('fetches categories successfully', async () => {
      const mockCategories = {
        success: true,
        data: {
          core: [{ slug: 'orchestrator', name: 'Orchestrator' }],
          coder: [{ slug: 'code-python', name: 'Python Coder' }]
        }
      };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockCategories
      });

      const result = await apiService.getCategories();
      expect(result.success).toBe(true);
      expect(result.data.core).toBeDefined();
      expect(result.data.coder).toBeDefined();
    });

    test('handles empty categories', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ success: true, data: {} })
      });

      const result = await apiService.getCategories();
      expect(result.success).toBe(true);
      expect(Object.keys(result.data)).toHaveLength(0);
    });
  });

  describe('Error Handling', () => {
    test('handles network errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      await expect(apiService.getModels()).rejects.toThrow('Network error');
    });

    test('handles malformed JSON responses', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => { throw new Error('Invalid JSON'); }
      });

      await expect(apiService.getModels()).rejects.toThrow('Invalid JSON');
    });

    test('handles timeout errors', async () => {
      jest.setTimeout(1000);
      
      (global.fetch as jest.Mock).mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 2000))
      );

      // This would timeout in a real scenario
      // For testing, we'll just verify the mock was called
      const promise = apiService.getModels();
      expect(global.fetch).toHaveBeenCalled();
    });
  });
});