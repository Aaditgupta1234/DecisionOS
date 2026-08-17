import React from 'react';
import { ExecutiveNav } from '../../components/home/ExecutiveNav';
import { HeroCommandStage } from '../../components/home/HeroCommandStage';
import { WhyDashboardsFailSection } from '../../components/home/WhyDashboardsFailSection';
import { IntelligencePipelineSection } from '../../components/home/IntelligencePipelineSection';
import { ThreeImperativesSection } from '../../components/home/ThreeImperativesSection';
import { ExecutiveCommandCenterPreview } from '../../components/home/ExecutiveCommandCenterPreview';
import { DexInteractiveTerminal } from '../../components/home/DexInteractiveTerminal';
import { EnterpriseSystemScaleSection } from '../../components/home/EnterpriseSystemScaleSection';
import { ExecutiveCtaFooter } from '../../components/home/ExecutiveCtaFooter';
import '../../styles/home.css';

export const HomeView: React.FC = () => {
  return (
    <div className="home-container">
      {/* Background Matrix Grid */}
      <div className="home-bg-grid" />

      {/* 1. Executive Navigation */}
      <ExecutiveNav />

      {/* 2. Hero Command Stage (DEX on 3D Pedestal with 4 Telemetry Pods) */}
      <HeroCommandStage />

      {/* 3. Why Traditional Dashboards Fail */}
      <WhyDashboardsFailSection />

      {/* 4. The Intelligence Pipeline DAG */}
      <IntelligencePipelineSection />

      {/* 5. Three Executive Imperatives (Know, Understand, Decide) */}
      <ThreeImperativesSection />

      {/* 6. Executive Command Center Preview */}
      <ExecutiveCommandCenterPreview />

      {/* 7. DEX Scenario Sandbox */}
      <DexInteractiveTerminal />

      {/* 8. Enterprise System Scale (Recruiter Gold) */}
      <EnterpriseSystemScaleSection />

      {/* 9. Executive CTA & Footer */}
      <ExecutiveCtaFooter />
    </div>
  );
};

export default HomeView;
