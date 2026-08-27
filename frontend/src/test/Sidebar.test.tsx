import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import { Sidebar } from '../components/layout/Sidebar';

describe('Sidebar Component', () => {
  it('renders all key executive navigation links', () => {
    render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>
    );

    expect(screen.getByText('Enterprise Command')).toBeInTheDocument();
    expect(screen.getByText('Executive Boardroom')).toBeInTheDocument();
    expect(screen.getByText('AI Business Analyst')).toBeInTheDocument();
    expect(screen.getByText('AI Decision Copilot')).toBeInTheDocument();
    expect(screen.getByText('Data & Intelligence')).toBeInTheDocument();
    expect(screen.getByText('Strategy & Execution')).toBeInTheDocument();
    expect(screen.getByText('Governance & Risk')).toBeInTheDocument();
    expect(screen.getByText('Enterprise Portfolio')).toBeInTheDocument();
    expect(screen.getByText('Platform Admin')).toBeInTheDocument();
  });
});
