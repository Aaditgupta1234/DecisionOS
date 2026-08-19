export type DependencyType = 'HARD_BLOCKER' | 'SOFT_BLOCKER' | 'EXTERNAL';

export interface InitiativeDependency {
  id: string;
  code: string;
  title: string;
  type: DependencyType;
  isResolved: boolean;
  owner: string;
  resolutionRequirement: string;
}

export interface DependencyGuardResult {
  allowed: boolean;
  hasHardBlockers: boolean;
  hasSoftBlockers: boolean;
  hasExternalRisks: boolean;
  hardBlockers: InitiativeDependency[];
  softBlockers: InitiativeDependency[];
  externalRisks: InitiativeDependency[];
  message: string;
}

export class InitiativeDependencyGuard {
  /**
   * Validates whether an initiative can transition to a target status
   */
  public static validateTransition(
    targetStatus: string,
    dependencies: InitiativeDependency[],
    hasBaselineSnapshot: boolean = true
  ): DependencyGuardResult {
    // If moving to NOT_STARTED or DISMISSED, always allow
    if (targetStatus === 'NOT_STARTED' || targetStatus === 'DISMISSED') {
      return {
        allowed: true,
        hasHardBlockers: false,
        hasSoftBlockers: false,
        hasExternalRisks: false,
        hardBlockers: [],
        softBlockers: [],
        externalRisks: [],
        message: 'State transition permitted without restrictions.',
      };
    }

    const unresolved = dependencies.filter((d) => !d.isResolved);
    const hardBlockers = unresolved.filter((d) => d.type === 'HARD_BLOCKER');
    const softBlockers = unresolved.filter((d) => d.type === 'SOFT_BLOCKER');
    const externalRisks = unresolved.filter((d) => d.type === 'EXTERNAL');

    // Rule 1: Moving to IN_PROGRESS with HARD_BLOCKERS is strictly prohibited
    if (targetStatus === 'IN_PROGRESS' && hardBlockers.length > 0) {
      return {
        allowed: false,
        hasHardBlockers: true,
        hasSoftBlockers: softBlockers.length > 0,
        hasExternalRisks: externalRisks.length > 0,
        hardBlockers,
        softBlockers,
        externalRisks,
        message: `Cannot start initiative: ${hardBlockers.length} unresolved hard blocker(s) detected (${hardBlockers.map((b) => b.code).join(', ')}).`,
      };
    }

    // Rule 2: Moving to COMPLETED requires baseline snapshot and no hard blockers
    if (targetStatus === 'COMPLETED') {
      if (!hasBaselineSnapshot) {
        return {
          allowed: false,
          hasHardBlockers: true,
          hasSoftBlockers: false,
          hasExternalRisks: false,
          hardBlockers: [],
          softBlockers: [],
          externalRisks: [],
          message: 'Cannot mark as completed: Immutable KPI baseline snapshot has not been frozen.',
        };
      }

      if (hardBlockers.length > 0) {
        return {
          allowed: false,
          hasHardBlockers: true,
          hasSoftBlockers: softBlockers.length > 0,
          hasExternalRisks: externalRisks.length > 0,
          hardBlockers,
          softBlockers,
          externalRisks,
          message: `Cannot mark as completed: ${hardBlockers.length} hard blocker(s) remaining (${hardBlockers.map((b) => b.code).join(', ')}).`,
        };
      }
    }

    // Allowed with warnings if soft blockers or external risks exist
    if (softBlockers.length > 0 || externalRisks.length > 0) {
      return {
        allowed: true,
        hasHardBlockers: false,
        hasSoftBlockers: softBlockers.length > 0,
        hasExternalRisks: externalRisks.length > 0,
        hardBlockers: [],
        softBlockers,
        externalRisks,
        message: softBlockers.length > 0
          ? `Permitted with warning: ${softBlockers.length} soft blocker(s) pending.`
          : `Permitted with risk flag: ${externalRisks.length} external dependency vector(s) active.`,
      };
    }

    return {
      allowed: true,
      hasHardBlockers: false,
      hasSoftBlockers: false,
      hasExternalRisks: false,
      hardBlockers: [],
      softBlockers: [],
      externalRisks: [],
      message: 'Transition verified. All prerequisite dependencies are satisfied.',
    };
  }
}
