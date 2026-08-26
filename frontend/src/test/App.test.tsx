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
    const branding = await screen.findAllByText(/DecisionOS/i);
    expect(branding.length).toBeGreaterThan(0);
  });
});
