/**
 * Utility functions tests for LazyAI Studio Frontend
 */

// Mock utility functions for testing
export const formatDate = (date: Date | string): string => {
  const d = new Date(date);
  return d.toLocaleDateString('zh-CN');
};

export const formatFileSize = (bytes: number): string => {
  const sizes = ['B', 'KB', 'MB', 'GB'];
  if (bytes === 0) return '0 B';
  
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + ' ' + sizes[i];
};

export const validateSlug = (slug: string): boolean => {
  const slugRegex = /^[a-z0-9-]+$/;
  return slugRegex.test(slug) && slug.length >= 2 && slug.length <= 50;
};

describe('Utility Functions', () => {
  describe('formatDate', () => {
    test('formats date object correctly', () => {
      const date = new Date('2024-01-15');
      const formatted = formatDate(date);
      expect(formatted).toBe('2024/1/15');
    });

    test('formats date string correctly', () => {
      const formatted = formatDate('2024-01-15');
      expect(formatted).toBe('2024/1/15');
    });

    test('handles invalid date', () => {
      const formatted = formatDate('invalid-date');
      expect(formatted).toBe('Invalid Date');
    });
  });

  describe('formatFileSize', () => {
    test('formats bytes correctly', () => {
      expect(formatFileSize(0)).toBe('0 B');
      expect(formatFileSize(512)).toBe('512 B');
      expect(formatFileSize(1024)).toBe('1 KB');
      expect(formatFileSize(1536)).toBe('1.5 KB');
      expect(formatFileSize(1048576)).toBe('1 MB');
      expect(formatFileSize(1073741824)).toBe('1 GB');
    });

    test('handles large file sizes', () => {
      const result = formatFileSize(1234567890);
      expect(result).toMatch(/^\d+(\.\d+)? GB$/);
    });
  });

  describe('validateSlug', () => {
    test('validates correct slugs', () => {
      expect(validateSlug('test-model')).toBe(true);
      expect(validateSlug('code-python')).toBe(true);
      expect(validateSlug('my-model-123')).toBe(true);
      expect(validateSlug('ab')).toBe(true);
    });

    test('rejects invalid slugs', () => {
      expect(validateSlug('')).toBe(false);
      expect(validateSlug('a')).toBe(false); // too short
      expect(validateSlug('Test-Model')).toBe(false); // uppercase
      expect(validateSlug('test_model')).toBe(false); // underscore
      expect(validateSlug('test model')).toBe(false); // space
      expect(validateSlug('test@model')).toBe(false); // special character
    });

    test('rejects too long slugs', () => {
      const longSlug = 'a'.repeat(51);
      expect(validateSlug(longSlug)).toBe(false);
    });
  });
});