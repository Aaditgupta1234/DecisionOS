import React from 'react';
import { useDataset } from '../../context/DatasetContext';
import { Database } from 'lucide-react';
import { EmptyState } from '../../components/feedback/EmptyState';
import { ExecutiveDashboard } from '../../features/dashboard/ExecutiveDashboard';

export const DashboardView: React.FC = () => {
  const { activeDataset } = useDataset();

  if (!activeDataset) {
    return (
      <div className="page-container">
        <EmptyState
          title="No Active Dataset Selected"
          description="Upload a CSV dataset or select an existing dataset from the top navigation to view the executive decision intelligence dashboard."
          icon={Database}
        />
      </div>
    );
  }

  return <ExecutiveDashboard datasetId={activeDataset.id} />;
};
export default DashboardView;
