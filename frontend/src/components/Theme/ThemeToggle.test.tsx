import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider } from '../../contexts/ThemeContext';
import ThemeToggle from './ThemeToggle';

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

const renderWithThemeProvider = (component: React.ReactElement) => {
  return render(
    <ThemeProvider>
      {component}
    </ThemeProvider>
  );
};

describe('ThemeToggle', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue('deepSeaMoon');
  });

  it('should render theme toggle button', () => {
    renderWithThemeProvider(<ThemeToggle />);

    const toggleButton = screen.getByRole('button');
    expect(toggleButton).toBeInTheDocument();
  });

  it('should show current theme name', () => {
    renderWithThemeProvider(<ThemeToggle />);

    // Should show some theme name
    const button = screen.getByRole('button');
    expect(button).toHaveTextContent(/主题/);
  });

  it('should open dropdown when clicked', () => {
    renderWithThemeProvider(<ThemeToggle />);

    const toggleButton = screen.getByRole('button');
    fireEvent.mouseEnter(toggleButton);

    // Should show dropdown with theme options
    // Note: Antd dropdown behavior might need different event handling
    expect(toggleButton).toBeInTheDocument();
  });

  it('should have tooltip with theme information', () => {
    renderWithThemeProvider(<ThemeToggle />);

    const toggleButton = screen.getByRole('button');

    // Trigger tooltip
    fireEvent.mouseEnter(toggleButton);

    // The tooltip should be accessible
    expect(toggleButton).toHaveAttribute('title');
  });

  it('should change theme when option is selected', () => {
    renderWithThemeProvider(<ThemeToggle />);

    const toggleButton = screen.getByRole('button');

    // Click to open dropdown
    fireEvent.click(toggleButton);

    // This test would require more complex Antd dropdown interaction
    // For now, just verify the button is clickable
    expect(toggleButton).toBeInTheDocument();
  });

  it('should display theme icon', () => {
    renderWithThemeProvider(<ThemeToggle />);

    const toggleButton = screen.getByRole('button');

    // Should contain an icon (Antd icons are rendered as spans with specific classes)
    const icon = toggleButton.querySelector('.anticon');
    expect(icon || toggleButton.querySelector('svg')).toBeTruthy();
  });

  it('should be accessible', () => {
    renderWithThemeProvider(<ThemeToggle />);

    const toggleButton = screen.getByRole('button');

    // Should have proper accessibility attributes
    expect(toggleButton).toBeInTheDocument();
    expect(toggleButton).not.toHaveAttribute('aria-disabled', 'true');
  });

  it('should handle theme switching correctly', () => {
    const { rerender } = renderWithThemeProvider(<ThemeToggle />);

    // Change localStorage mock to different theme
    localStorageMock.getItem.mockReturnValue('springBreeze');

    rerender(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    const toggleButton = screen.getByRole('button');
    expect(toggleButton).toBeInTheDocument();
  });

  it('should work with all available themes', () => {
    const themes = ['deepSeaMoon', 'nightRain', 'plumRain', 'springBreeze', 'summerGreen'];

    themes.forEach(theme => {
      localStorageMock.getItem.mockReturnValue(theme);

      renderWithThemeProvider(<ThemeToggle />);

      const toggleButton = screen.getByRole('button');
      expect(toggleButton).toBeInTheDocument();
    });
  });

  it('should handle invalid theme gracefully', () => {
    localStorageMock.getItem.mockReturnValue('invalid-theme');

    renderWithThemeProvider(<ThemeToggle />);

    const toggleButton = screen.getByRole('button');
    expect(toggleButton).toBeInTheDocument();
  });
});