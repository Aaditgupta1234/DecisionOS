import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from '../App';

// Mock global fetch for testing dataset loading
globalThis.fetch = vi.fn(() =>
  Promise.resolve({
    ok: true,
    text: () => Promise.resolve(JSON.stringify({ success: true, data: [] })),
  } as Response)
);

describe('App Component', () => {
  it('renders application shell and branding', async () => {
    render(<App />);
    expect(screen.getByText('Decision')).toBeInTheDocument();
    expect(screen.getByText('OS')).toBeInTheDocument();
    expect(screen.getByText('Decision Intelligence')).toBeInTheDocument();
  });
});
