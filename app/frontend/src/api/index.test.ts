import { describe, it, expect, vi, beforeEach } from 'vitest';
import { api, fetchApi } from './index';

// Mock fetch function
const mockFetch = vi.fn();

beforeEach(() => {
  vi.clearAllMocks();
  global.fetch = mockFetch;
});


describe('fetchApi', () => {
  it('should successfully fetch data and parse JSON', async () => {
    const mockData = { message: 'Hello from mock server' };
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockData),
      headers: new Headers({ 'Content-Type': 'application/json' }),
    });

    const result = await fetchApi('/test');
    expect(result).toEqual(mockData);
    expect(mockFetch).toHaveBeenCalledWith('/api/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
  });

  it('should handle HTTP error responses', async () => {
    const errorData = { detail: 'Not Found' };
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      json: () => Promise.resolve(errorData),
      headers: new Headers({ 'Content-Type': 'application/json' }),
    });

    await expect(fetchApi('/test')).rejects.toThrow('Not Found');
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  it('should re-throw network errors', async () => {
    const networkError = new Error('Network Down');
    mockFetch.mockRejectedValueOnce(networkError);

    await expect(fetchApi('/test')).rejects.toThrow('Network Down');
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  it('should correctly handle FormData request body', async () => {
    const formData = new FormData();
    formData.append('file', new File(['content'], 'test.txt'));
    formData.append('data', 'some_data');

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true }),
      headers: new Headers({ 'Content-Type': 'application/json' }),
    });

    await fetchApi('/upload', 'POST', formData);

    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toBe('/api/upload');
    expect(options.method).toBe('POST');
    expect(options.body).toBeInstanceOf(FormData);
    expect(options.headers['Content-Type']).toBeUndefined(); // Content-Type should be undefined for FormData
  });

  it('should correctly handle file download response (application/x-yaml)', async () => {
    const mockBlob = new Blob(['yaml content'], { type: 'application/x-yaml' });
    Object.defineProperty(mockBlob, 'text', {
      value: () => Promise.resolve('yaml content'),
      writable: true,
      configurable: true,
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      blob: () => Promise.resolve(mockBlob),
      text: () => Promise.resolve('yaml content'),
      headers: new Headers({ 'Content-Type': 'application/x-yaml' }),
    });

    const result = await fetchApi<Blob>('/export', 'POST', { id: '123' });
        expect(result).toBeInstanceOf(Blob);
        expect(result.type).toBe('application/x-yaml');
        const textContent = await result.text();
        expect(textContent).toBe('yaml content');
      });

  it('should correctly handle file download response (application/json with content-disposition)', async () => {
    const mockBlob = new Blob(['{"key": "value"}'], { type: 'application/json' });
    Object.defineProperty(mockBlob, 'text', {
      value: () => Promise.resolve('{"key": "value"}'),
      writable: true,
      configurable: true,
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      blob: () => Promise.resolve(mockBlob),
      text: () => Promise.resolve('{"key": "value"}'), // Add this line
      headers: new Headers({ 'Content-Type': 'application/json', 'Content-Disposition': 'attachment; filename="data.json"' }),
    });

    const result = await fetchApi<Blob>('/download', 'POST', { id: '456' });
    expect(result).toBeInstanceOf(Blob);
    expect(result.type).toBe('application/json');
    const textContent = await result.text();
    expect(textContent).toBe('{"key": "value"}');
  });
});
describe('api.hello', () => {
  it('should call fetchApi with correct parameters for hello endpoint', async () => {
    const mockResponse = { message: 'Hello from mock server' };
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse),
      headers: new Headers({ 'Content-Type': 'application/json' }),
    });

    const requestBody = { message: 'test' };
    const result = await api.hello(requestBody);

    expect(result).toEqual(mockResponse);
    expect(mockFetch).toHaveBeenCalledWith('/api/hello', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
    });
  });

  it('should handle errors for hello endpoint', async () => {
    const errorData = { detail: 'Bad Request' };
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      statusText: 'Bad Request',
      json: () => Promise.resolve(errorData),
      headers: new Headers({ 'Content-Type': 'application/json' }),
    });

    await expect(api.hello({ message: 'invalid' })).rejects.toThrow('Bad Request');
  });
});

describe('api.getModels', () => {
  it('should call fetchApi with correct parameters for getModels endpoint', async () => {
    const mockResponse = [{ name: 'model1' }, { name: 'model2' }];
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse),
      headers: new Headers({ 'Content-Type': 'application/json' }),
    });

    const result = await api.getModels();

    expect(result).toEqual(mockResponse);
    expect(mockFetch).toHaveBeenCalledWith('/api/models', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
  });
});