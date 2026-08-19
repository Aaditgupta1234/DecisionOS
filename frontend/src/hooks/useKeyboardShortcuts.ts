import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

export const useKeyboardShortcuts = (onOpenSearch?: () => void) => {
  const navigate = useNavigate();
  const [gPressed, setGPressed] = useState(false);

  useEffect(() => {
    let timeout: any = null;

    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore in input or textarea
      if (
        document.activeElement?.tagName === 'INPUT' ||
        document.activeElement?.tagName === 'TEXTAREA'
      ) {
        return;
      }

      // Command + K or Ctrl + K
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        onOpenSearch?.();
        return;
      }

      // Sequence: G followed by letter
      if (e.key.toLowerCase() === 'g' && !e.metaKey && !e.ctrlKey) {
        setGPressed(true);
        clearTimeout(timeout);
        timeout = setTimeout(() => setGPressed(false), 1000);
        return;
      }

      if (gPressed) {
        const key = e.key.toLowerCase();
        setGPressed(false);

        switch (key) {
          case 'p':
            navigate('/portfolio-rollup');
            break;
          case 'c':
            navigate('/capital-allocation');
            break;
          case 'd':
            navigate('/diagnostics');
            break;
          case 'k':
            navigate('/kpi-dictionary');
            break;
          case 'r':
            navigate('/reports');
            break;
          case 'm':
            navigate('/monitoring');
            break;
          case 's':
            navigate('/strategy-execution');
            break;
          case 'a':
            navigate('/agents');
            break;
          default:
            break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      clearTimeout(timeout);
    };
  }, [gPressed, navigate, onOpenSearch]);

  return { gPressed };
};
