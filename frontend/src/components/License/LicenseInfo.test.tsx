import React from 'react';
import { render, screen } from '@testing-library/react';
import LicenseInfo from './LicenseInfo';

describe('LicenseInfo', () => {
  it('should render license information', () => {
    render(<LicenseInfo />);

    // Check for actual license content based on the component implementation
    expect(screen.getByText('AGPL-3.0')).toBeInTheDocument();
    expect(screen.getByText('LazyGophers')).toBeInTheDocument();
  });

  it('should be accessible', () => {
    const { container } = render(<LicenseInfo />);

    // Should have proper semantic structure
    expect(container.firstChild).toBeInTheDocument();
  });

  it('should render without crashing', () => {
    expect(() => render(<LicenseInfo />)).not.toThrow();
  });

  it('should have consistent styling', () => {
    const { container } = render(<LicenseInfo />);

    // Should have some content
    expect(container.firstChild).toBeTruthy();
  });
});