import React from 'react';
import { render, screen, act } from '@testing-library/react';
import { ThemeProvider, useTheme } from './ThemeContext';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Test component that uses the theme context
const TestComponent: React.FC = () => {
  const { themeType, currentTheme, setThemeType } = useTheme();

  return (
    <div>
      <div data-testid="theme-type">{themeType}</div>
      <div data-testid="theme-algorithm">{currentTheme.algorithm?.toString()}</div>
      <button onClick={() => setThemeType('nightRain' as any)}>
        Change to Night Rain
      </button>
    </div>
  );
};

describe('ThemeContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset document.body.className
    document.body.className = '';
  });

  it('should provide default theme when no localStorage value', () => {
    localStorageMock.getItem.mockReturnValue(null);

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId('theme-type')).toHaveTextContent('deepSeaMoon');
  });

  it('should load theme from localStorage', () => {
    localStorageMock.getItem.mockReturnValue('nightRain');

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId('theme-type')).toHaveTextContent('nightRain');
  });

  it('should fall back to first theme if saved theme does not exist', () => {
    localStorageMock.getItem.mockReturnValue('nonexistent-theme');

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    // Should fall back to first available theme
    const themeType = screen.getByTestId('theme-type').textContent;
    expect(themeType).toBeTruthy();
  });

  it('should change theme when setThemeType is called', () => {
    localStorageMock.getItem.mockReturnValue('deepSeaMoon');

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId('theme-type')).toHaveTextContent('deepSeaMoon');

    act(() => {
      screen.getByText('Change to Night Rain').click();
    });

    expect(screen.getByTestId('theme-type')).toHaveTextContent('nightRain');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('theme-type', 'nightRain');
  });

  it('should update document body className based on theme', () => {
    localStorageMock.getItem.mockReturnValue('deepSeaMoon');

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(document.body.className).toContain('dark-theme');
    expect(document.body.className).toContain('theme-deepSeaMoon');
  });

  it('should apply light theme class for light themes', () => {
    localStorageMock.getItem.mockReturnValue('springBreeze');

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(document.body.className).toContain('light-theme');
    // The theme should be applied correctly
    expect(document.body.className).toMatch(/theme-\w+/);
  });

  it('should throw error when useTheme is used outside provider', () => {
    const TestComponentWithoutProvider: React.FC = () => {
      useTheme();
      return <div>Test</div>;
    };

    // Suppress console.error for this test
    const originalError = console.error;
    console.error = jest.fn();

    expect(() => {
      render(<TestComponentWithoutProvider />);
    }).toThrow('useTheme must be used within a ThemeProvider');

    console.error = originalError;
  });

  it('should provide theme configuration object', () => {
    localStorageMock.getItem.mockReturnValue('deepSeaMoon');

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    // Should have algorithm property (indicates it's a proper theme config)
    expect(screen.getByTestId('theme-algorithm')).not.toBeEmptyDOMElement();
  });
});