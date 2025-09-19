import { renderHook } from '@testing-library/react';
import { useDocumentTitle, setDocumentTitle } from './useDocumentTitle';

describe('useDocumentTitle', () => {
  const originalTitle = document.title;

  beforeEach(() => {
    // Reset document title before each test
    document.title = 'Original Title';
  });

  afterAll(() => {
    // Restore original title after all tests
    document.title = originalTitle;
  });

  it('should set document title with default suffix', () => {
    renderHook(() => useDocumentTitle('Test Page'));

    expect(document.title).toBe('Test Page - LazyAI Studio');
  });

  it('should set document title with custom suffix', () => {
    renderHook(() => useDocumentTitle('Test Page', 'Custom App'));

    expect(document.title).toBe('Test Page - Custom App');
  });

  it('should set only suffix when title is empty', () => {
    renderHook(() => useDocumentTitle(''));

    expect(document.title).toBe('LazyAI Studio');
  });

  it('should set only custom suffix when title is empty', () => {
    renderHook(() => useDocumentTitle('', 'Custom App'));

    expect(document.title).toBe('Custom App');
  });

  it('should update title when title changes', () => {
    const { rerender } = renderHook(
      ({ title }) => useDocumentTitle(title),
      { initialProps: { title: 'First Title' } }
    );

    expect(document.title).toBe('First Title - LazyAI Studio');

    rerender({ title: 'Second Title' });

    expect(document.title).toBe('Second Title - LazyAI Studio');
  });

  it('should update title when suffix changes', () => {
    const { rerender } = renderHook(
      ({ suffix }) => useDocumentTitle('Test Page', suffix),
      { initialProps: { suffix: 'App 1' } }
    );

    expect(document.title).toBe('Test Page - App 1');

    rerender({ suffix: 'App 2' });

    expect(document.title).toBe('Test Page - App 2');
  });

  it('should restore previous title on unmount', () => {
    const initialTitle = 'Initial Title';
    document.title = initialTitle;

    const { unmount } = renderHook(() => useDocumentTitle('Test Page'));

    expect(document.title).toBe('Test Page - LazyAI Studio');

    unmount();

    expect(document.title).toBe(initialTitle);
  });

  it('should handle multiple hook instances correctly', () => {
    const { unmount: unmount1 } = renderHook(() => useDocumentTitle('Page 1'));
    expect(document.title).toBe('Page 1 - LazyAI Studio');

    const { unmount: unmount2 } = renderHook(() => useDocumentTitle('Page 2'));
    expect(document.title).toBe('Page 2 - LazyAI Studio');

    unmount2();
    // After unmounting the second hook, title should remain as Page 2
    expect(document.title).toBe('Page 1 - LazyAI Studio');

    unmount1();
    // After unmounting all hooks, should restore to original
    expect(document.title).toBe('Original Title');
  });
});

describe('setDocumentTitle', () => {
  const originalTitle = document.title;

  beforeEach(() => {
    document.title = 'Original Title';
  });

  afterAll(() => {
    document.title = originalTitle;
  });

  it('should set document title with default suffix', () => {
    setDocumentTitle('Function Test');

    expect(document.title).toBe('Function Test - LazyAI Studio');
  });

  it('should set document title with custom suffix', () => {
    setDocumentTitle('Function Test', 'Custom App');

    expect(document.title).toBe('Function Test - Custom App');
  });

  it('should set only suffix when title is empty', () => {
    setDocumentTitle('');

    expect(document.title).toBe('LazyAI Studio');
  });

  it('should set only custom suffix when title is empty', () => {
    setDocumentTitle('', 'Custom App');

    expect(document.title).toBe('Custom App');
  });

  it('should handle undefined title', () => {
    setDocumentTitle(undefined as any);

    expect(document.title).toBe('LazyAI Studio');
  });

  it('should handle null title', () => {
    setDocumentTitle(null as any);

    expect(document.title).toBe('LazyAI Studio');
  });
});