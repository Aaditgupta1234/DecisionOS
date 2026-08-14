import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { Dataset } from '../types';
import { DecisionApi } from '../api';

interface DatasetContextType {
  datasets: Dataset[];
  activeDataset: Dataset | null;
  setActiveDataset: (dataset: Dataset) => void;
  loading: boolean;
  error: string | null;
  refreshDatasets: (organizationId?: string) => Promise<void>;
}

const DatasetContext = createContext<DatasetContextType | undefined>(undefined);

export const DatasetProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [activeDataset, setActiveDatasetState] = useState<Dataset | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const refreshDatasets = async (organizationId?: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await DecisionApi.listDatasets(organizationId);
      const list = Array.isArray(data) ? data : [];
      setDatasets(list);

      let savedId: string | null = null;
      try {
        if (typeof window !== 'undefined' && window.localStorage) {
          savedId = window.localStorage.getItem('decisionos_active_dataset_id');
        }
      } catch {
        // Safe fallback
      }

      const matched = list.find((d) => d.id === savedId);

      if (matched) {
        setActiveDatasetState(matched);
      } else if (list.length > 0) {
        setActiveDatasetState(list[0]);
        try {
          if (typeof window !== 'undefined' && window.localStorage) {
            window.localStorage.setItem('decisionos_active_dataset_id', list[0].id);
          }
        } catch {}
      } else {
        setActiveDatasetState(null);
      }
    } catch (err: any) {
      console.error('Failed to load datasets:', err);
      setError(err?.message || 'Unable to connect to backend datasets API.');
    } finally {
      setLoading(false);
    }
  };

  const setActiveDataset = (dataset: Dataset) => {
    setActiveDatasetState(dataset);
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.setItem('decisionos_active_dataset_id', dataset.id);
      }
    } catch {}
  };

  useEffect(() => {
    refreshDatasets();
  }, []);

  return (
    <DatasetContext.Provider
      value={{
        datasets,
        activeDataset,
        setActiveDataset,
        loading,
        error,
        refreshDatasets,
      }}
    >
      {children}
    </DatasetContext.Provider>
  );
};

export const useDataset = () => {
  const context = useContext(DatasetContext);
  if (!context) {
    throw new Error('useDataset must be used within a DatasetProvider');
  }
  return context;
};
