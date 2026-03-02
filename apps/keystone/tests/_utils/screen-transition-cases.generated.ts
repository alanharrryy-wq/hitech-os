import type {
  ScreenDeterminismEvaluation,
  ScreenDeterminismInput,
  PitchFlowState
} from "./screen-transition-determinism";

export interface ScreenTransitionCase {
  readonly id: string;
  readonly input: ScreenDeterminismInput;
  readonly expected: ScreenDeterminismEvaluation;
  readonly expectedTransitions: {
    readonly draftRunScreen05: PitchFlowState;
    readonly draftRunScreen06: PitchFlowState;
    readonly approvalState: PitchFlowState;
    readonly approvalLock: string | null;
    readonly runScreen06Lock: string | null;
    readonly rejectionState: PitchFlowState;
    readonly resetState: PitchFlowState;
  };
}

export const SCREEN_TRANSITION_CASES: readonly ScreenTransitionCase[] = [
  {
    id: "case_0001",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 25,
        penaltyScore: 12,
        finalScore: 13,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 20,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0002",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 28,
        penaltyScore: 0,
        finalScore: 28,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 32,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0003",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 30,
        penaltyScore: 0,
        finalScore: 30,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 36,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0004",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 32,
        penaltyScore: 0,
        finalScore: 32,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 40,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0005",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 34,
        penaltyScore: 0,
        finalScore: 34,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 43,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0006",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 29,
        penaltyScore: 19,
        finalScore: 10,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 18,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0007",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 32,
        penaltyScore: 7,
        finalScore: 25,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 30,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0008",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 34,
        penaltyScore: 7,
        finalScore: 27,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 34,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0009",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 37,
        penaltyScore: 7,
        finalScore: 30,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 38,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0010",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 38,
        penaltyScore: 7,
        finalScore: 31,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 41,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0011",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 33,
        penaltyScore: 26,
        finalScore: 7,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 16,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0012",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 36,
        penaltyScore: 14,
        finalScore: 22,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 28,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0013",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 39,
        penaltyScore: 14,
        finalScore: 25,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 33,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0014",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 41,
        penaltyScore: 14,
        finalScore: 27,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 37,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0015",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 42,
        penaltyScore: 14,
        finalScore: 28,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 39,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0016",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 38,
        penaltyScore: 33,
        finalScore: 5,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 15,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0017",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 41,
        penaltyScore: 21,
        finalScore: 20,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 27,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0018",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 43,
        penaltyScore: 21,
        finalScore: 22,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 31,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0019",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 45,
        penaltyScore: 21,
        finalScore: 24,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 35,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0020",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 47,
        penaltyScore: 21,
        finalScore: 26,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 38,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0021",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 42,
        penaltyScore: 40,
        finalScore: 2,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 13,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0022",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 45,
        penaltyScore: 28,
        finalScore: 17,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 25,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0023",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 47,
        penaltyScore: 28,
        finalScore: 19,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 29,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0024",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 50,
        penaltyScore: 28,
        finalScore: 22,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 34,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0025",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 51,
        penaltyScore: 28,
        finalScore: 23,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 36,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0026",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 34,
        penaltyScore: 12,
        finalScore: 22,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 32,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0027",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 37,
        penaltyScore: 0,
        finalScore: 37,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 44,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0028",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 39,
        penaltyScore: 0,
        finalScore: 39,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 48,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0029",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 41,
        penaltyScore: 0,
        finalScore: 41,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 52,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0030",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 43,
        penaltyScore: 0,
        finalScore: 43,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 55,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0031",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 38,
        penaltyScore: 19,
        finalScore: 19,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 30,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0032",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 41,
        penaltyScore: 7,
        finalScore: 34,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 43,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0033",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 44,
        penaltyScore: 7,
        finalScore: 37,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 47,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0034",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 46,
        penaltyScore: 7,
        finalScore: 39,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 51,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0035",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 47,
        penaltyScore: 7,
        finalScore: 40,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 53,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0036",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 43,
        penaltyScore: 26,
        finalScore: 17,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 29,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0037",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 46,
        penaltyScore: 14,
        finalScore: 32,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 41,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0038",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 48,
        penaltyScore: 14,
        finalScore: 34,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 45,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0039",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 50,
        penaltyScore: 14,
        finalScore: 36,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 49,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0040",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 52,
        penaltyScore: 14,
        finalScore: 38,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 52,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0041",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 47,
        penaltyScore: 33,
        finalScore: 14,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 27,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0042",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 50,
        penaltyScore: 21,
        finalScore: 29,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 40,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0043",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 52,
        penaltyScore: 21,
        finalScore: 31,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 43,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0044",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 55,
        penaltyScore: 21,
        finalScore: 34,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 48,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0045",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 56,
        penaltyScore: 21,
        finalScore: 35,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 50,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0046",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 52,
        penaltyScore: 40,
        finalScore: 12,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 26,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0047",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 55,
        penaltyScore: 28,
        finalScore: 27,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 38,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0048",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 57,
        penaltyScore: 28,
        finalScore: 29,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 42,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0049",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 59,
        penaltyScore: 28,
        finalScore: 31,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 46,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0050",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 61,
        penaltyScore: 28,
        finalScore: 33,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 49,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0051",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 40,
        penaltyScore: 12,
        finalScore: 28,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 40,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0052",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 43,
        penaltyScore: 0,
        finalScore: 43,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 53,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0053",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 45,
        penaltyScore: 0,
        finalScore: 45,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 56,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0054",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 48,
        penaltyScore: 0,
        finalScore: 48,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 61,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0055",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 49,
        penaltyScore: 0,
        finalScore: 49,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 63,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0056",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 45,
        penaltyScore: 19,
        finalScore: 26,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 39,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0057",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 48,
        penaltyScore: 7,
        finalScore: 41,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 51,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0058",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 50,
        penaltyScore: 7,
        finalScore: 43,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 55,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0059",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 52,
        penaltyScore: 7,
        finalScore: 45,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 59,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0060",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 54,
        penaltyScore: 7,
        finalScore: 47,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 62,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0061",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 49,
        penaltyScore: 26,
        finalScore: 23,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 37,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0062",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 52,
        penaltyScore: 14,
        finalScore: 38,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 50,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0063",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 54,
        penaltyScore: 14,
        finalScore: 40,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 54,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0064",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 56,
        penaltyScore: 14,
        finalScore: 42,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 57,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0065",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 58,
        penaltyScore: 14,
        finalScore: 44,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 60,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0066",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 53,
        penaltyScore: 33,
        finalScore: 20,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 36,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0067",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 56,
        penaltyScore: 21,
        finalScore: 35,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 48,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0068",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 59,
        penaltyScore: 21,
        finalScore: 38,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 52,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0069",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 61,
        penaltyScore: 21,
        finalScore: 40,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 56,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0070",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 62,
        penaltyScore: 21,
        finalScore: 41,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 59,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0071",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 58,
        penaltyScore: 40,
        finalScore: 18,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 34,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0072",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 61,
        penaltyScore: 28,
        finalScore: 33,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 47,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0073",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 63,
        penaltyScore: 28,
        finalScore: 35,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 51,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0074",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 65,
        penaltyScore: 28,
        finalScore: 37,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 54,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0075",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 28,
        finalScore: 39,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 57,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0076",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 46,
        penaltyScore: 12,
        finalScore: 34,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 49,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0077",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 49,
        penaltyScore: 0,
        finalScore: 49,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 61,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0078",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 52,
        penaltyScore: 0,
        finalScore: 52,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 65,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0079",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 54,
        penaltyScore: 0,
        finalScore: 54,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 69,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0080",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 55,
        penaltyScore: 0,
        finalScore: 55,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 72,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0081",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 51,
        penaltyScore: 19,
        finalScore: 32,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 47,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0082",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 54,
        penaltyScore: 7,
        finalScore: 47,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 60,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0083",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 56,
        penaltyScore: 7,
        finalScore: 49,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 64,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0084",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 58,
        penaltyScore: 7,
        finalScore: 51,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 67,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0085",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 60,
        penaltyScore: 7,
        finalScore: 53,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 70,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0086",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 55,
        penaltyScore: 26,
        finalScore: 29,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 46,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0087",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 58,
        penaltyScore: 14,
        finalScore: 44,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 58,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0088",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 60,
        penaltyScore: 14,
        finalScore: 46,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 62,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0089",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 63,
        penaltyScore: 14,
        finalScore: 49,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 66,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0090",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 64,
        penaltyScore: 14,
        finalScore: 50,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 69,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0091",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 60,
        penaltyScore: 33,
        finalScore: 27,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 44,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0092",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 63,
        penaltyScore: 21,
        finalScore: 42,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 57,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0093",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 65,
        penaltyScore: 21,
        finalScore: 44,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 61,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0094",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 21,
        finalScore: 46,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 64,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0095",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 69,
        penaltyScore: 21,
        finalScore: 48,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 67,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0096",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 64,
        penaltyScore: 40,
        finalScore: 24,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 43,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0097",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 28,
        finalScore: 39,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 55,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0098",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 69,
        penaltyScore: 28,
        finalScore: 41,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 59,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0099",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 71,
        penaltyScore: 28,
        finalScore: 43,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 63,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0100",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 73,
        penaltyScore: 28,
        finalScore: 45,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 66,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0101",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 49,
        penaltyScore: 12,
        finalScore: 37,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 53,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0102",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 52,
        penaltyScore: 0,
        finalScore: 52,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 65,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0103",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 55,
        penaltyScore: 0,
        finalScore: 55,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 69,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0104",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 57,
        penaltyScore: 0,
        finalScore: 57,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 73,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0105",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 58,
        penaltyScore: 0,
        finalScore: 58,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 76,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0106",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 54,
        penaltyScore: 19,
        finalScore: 35,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 52,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0107",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 57,
        penaltyScore: 7,
        finalScore: 50,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 64,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0108",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 59,
        penaltyScore: 7,
        finalScore: 52,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 68,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0109",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 61,
        penaltyScore: 7,
        finalScore: 54,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 72,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0110",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 63,
        penaltyScore: 7,
        finalScore: 56,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 74,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0111",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 58,
        penaltyScore: 26,
        finalScore: 32,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 50,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0112",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 61,
        penaltyScore: 14,
        finalScore: 47,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 62,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0113",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 63,
        penaltyScore: 14,
        finalScore: 49,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 66,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0114",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 66,
        penaltyScore: 14,
        finalScore: 52,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 70,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0115",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 14,
        finalScore: 53,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 73,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0116",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 63,
        penaltyScore: 33,
        finalScore: 30,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 49,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0117",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 66,
        penaltyScore: 21,
        finalScore: 45,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 61,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0118",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 68,
        penaltyScore: 21,
        finalScore: 47,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 65,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0119",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 70,
        penaltyScore: 21,
        finalScore: 49,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 69,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0120",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 72,
        penaltyScore: 21,
        finalScore: 51,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 72,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0121",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 40,
        finalScore: 27,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 47,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0122",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 70,
        penaltyScore: 28,
        finalScore: 42,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 59,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0123",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 72,
        penaltyScore: 28,
        finalScore: 44,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 63,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0124",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 75,
        penaltyScore: 28,
        finalScore: 47,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 67,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0125",
    input: {
      industrialReliability: 25,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 76,
        penaltyScore: 28,
        finalScore: 48,
        reasons: ["screen05:final-score-below-70", "screen05:industrial-reliability-below-45", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 70,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0126",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 31,
        penaltyScore: 12,
        finalScore: 19,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 23,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0127",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 34,
        penaltyScore: 0,
        finalScore: 34,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 35,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0128",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 36,
        penaltyScore: 0,
        finalScore: 36,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 39,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0129",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 39,
        penaltyScore: 0,
        finalScore: 39,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 44,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0130",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 40,
        penaltyScore: 0,
        finalScore: 40,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 46,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0131",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 35,
        penaltyScore: 19,
        finalScore: 16,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 21,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0132",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 38,
        penaltyScore: 7,
        finalScore: 31,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 34,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0133",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 41,
        penaltyScore: 7,
        finalScore: 34,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 38,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0134",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 43,
        penaltyScore: 7,
        finalScore: 36,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 42,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0135",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 44,
        penaltyScore: 7,
        finalScore: 37,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 44,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0136",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 40,
        penaltyScore: 26,
        finalScore: 14,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 20,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0137",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 43,
        penaltyScore: 14,
        finalScore: 29,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 32,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0138",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 45,
        penaltyScore: 14,
        finalScore: 31,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 36,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0139",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 47,
        penaltyScore: 14,
        finalScore: 33,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 40,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0140",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 49,
        penaltyScore: 14,
        finalScore: 35,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 43,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0141",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 44,
        penaltyScore: 33,
        finalScore: 11,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 18,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0142",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 47,
        penaltyScore: 21,
        finalScore: 26,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 31,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0143",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 49,
        penaltyScore: 21,
        finalScore: 28,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 35,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0144",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 52,
        penaltyScore: 21,
        finalScore: 31,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 39,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0145",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 53,
        penaltyScore: 21,
        finalScore: 32,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 41,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0146",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 49,
        penaltyScore: 40,
        finalScore: 9,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 17,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0147",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 52,
        penaltyScore: 28,
        finalScore: 24,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 30,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0148",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 54,
        penaltyScore: 28,
        finalScore: 26,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 33,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0149",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 56,
        penaltyScore: 28,
        finalScore: 28,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 37,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0150",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 58,
        penaltyScore: 28,
        finalScore: 30,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 40,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0151",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 40,
        penaltyScore: 12,
        finalScore: 28,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 35,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0152",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 43,
        penaltyScore: 0,
        finalScore: 43,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 48,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0153",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 46,
        penaltyScore: 0,
        finalScore: 46,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 52,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0154",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 48,
        penaltyScore: 0,
        finalScore: 48,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 56,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0155",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 49,
        penaltyScore: 0,
        finalScore: 49,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 58,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0156",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 45,
        penaltyScore: 19,
        finalScore: 26,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 34,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0157",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 48,
        penaltyScore: 7,
        finalScore: 41,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 47,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0158",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 50,
        penaltyScore: 7,
        finalScore: 43,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 50,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0159",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 52,
        penaltyScore: 7,
        finalScore: 45,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 54,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0160",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 54,
        penaltyScore: 7,
        finalScore: 47,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 57,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0161",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 49,
        penaltyScore: 26,
        finalScore: 23,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 33,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0162",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 52,
        penaltyScore: 14,
        finalScore: 38,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 45,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0163",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 54,
        penaltyScore: 14,
        finalScore: 40,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 49,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0164",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 57,
        penaltyScore: 14,
        finalScore: 43,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 53,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0165",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 58,
        penaltyScore: 14,
        finalScore: 44,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 56,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0166",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 54,
        penaltyScore: 33,
        finalScore: 21,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 31,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0167",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 57,
        penaltyScore: 21,
        finalScore: 36,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 44,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0168",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 59,
        penaltyScore: 21,
        finalScore: 38,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 48,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0169",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 61,
        penaltyScore: 21,
        finalScore: 40,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 51,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0170",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 63,
        penaltyScore: 21,
        finalScore: 42,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 54,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0171",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 58,
        penaltyScore: 40,
        finalScore: 18,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 30,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0172",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 61,
        penaltyScore: 28,
        finalScore: 33,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 42,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0173",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 63,
        penaltyScore: 28,
        finalScore: 35,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 46,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0174",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 65,
        penaltyScore: 28,
        finalScore: 37,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 50,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0175",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 28,
        finalScore: 39,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 53,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0176",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 47,
        penaltyScore: 12,
        finalScore: 35,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 44,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0177",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 50,
        penaltyScore: 0,
        finalScore: 50,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 57,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0178",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 52,
        penaltyScore: 0,
        finalScore: 52,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 60,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0179",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 54,
        penaltyScore: 0,
        finalScore: 54,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 64,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0180",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 56,
        penaltyScore: 0,
        finalScore: 56,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 67,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0181",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 51,
        penaltyScore: 19,
        finalScore: 32,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 43,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0182",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 54,
        penaltyScore: 7,
        finalScore: 47,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 55,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0183",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 56,
        penaltyScore: 7,
        finalScore: 49,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 59,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0184",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 58,
        penaltyScore: 7,
        finalScore: 51,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 63,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0185",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 60,
        penaltyScore: 7,
        finalScore: 53,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 66,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0186",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 55,
        penaltyScore: 26,
        finalScore: 29,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 41,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0187",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 58,
        penaltyScore: 14,
        finalScore: 44,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 53,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0188",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 61,
        penaltyScore: 14,
        finalScore: 47,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 58,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0189",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 63,
        penaltyScore: 14,
        finalScore: 49,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 61,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0190",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 64,
        penaltyScore: 14,
        finalScore: 50,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 64,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0191",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 60,
        penaltyScore: 33,
        finalScore: 27,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 40,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0192",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 63,
        penaltyScore: 21,
        finalScore: 42,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 52,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0193",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 65,
        penaltyScore: 21,
        finalScore: 44,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 56,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0194",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 21,
        finalScore: 46,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 60,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0195",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 69,
        penaltyScore: 21,
        finalScore: 48,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 63,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0196",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 64,
        penaltyScore: 40,
        finalScore: 24,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 38,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0197",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 28,
        finalScore: 39,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 50,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0198",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 69,
        penaltyScore: 28,
        finalScore: 41,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 54,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0199",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 72,
        penaltyScore: 28,
        finalScore: 44,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 59,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0200",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 73,
        penaltyScore: 28,
        finalScore: 45,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 61,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0201",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 53,
        penaltyScore: 12,
        finalScore: 41,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 53,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0202",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 56,
        penaltyScore: 0,
        finalScore: 56,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 65,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0203",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 58,
        penaltyScore: 0,
        finalScore: 58,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 69,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0204",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 60,
        penaltyScore: 0,
        finalScore: 60,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 73,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0205",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 62,
        penaltyScore: 0,
        finalScore: 62,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 76,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0206",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 57,
        penaltyScore: 19,
        finalScore: 38,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 51,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0207",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 60,
        penaltyScore: 7,
        finalScore: 53,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 63,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0208",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 62,
        penaltyScore: 7,
        finalScore: 55,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 67,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0209",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 65,
        penaltyScore: 7,
        finalScore: 58,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 71,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0210",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 66,
        penaltyScore: 7,
        finalScore: 59,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 74,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0211",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 62,
        penaltyScore: 26,
        finalScore: 36,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 50,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0212",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 65,
        penaltyScore: 14,
        finalScore: 51,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 62,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0213",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 14,
        finalScore: 53,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 66,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0214",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 69,
        penaltyScore: 14,
        finalScore: 55,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 70,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0215",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 71,
        penaltyScore: 14,
        finalScore: 57,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 73,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0216",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 66,
        penaltyScore: 33,
        finalScore: 33,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 48,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0217",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 69,
        penaltyScore: 21,
        finalScore: 48,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 60,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0218",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 71,
        penaltyScore: 21,
        finalScore: 50,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 64,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0219",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 73,
        penaltyScore: 21,
        finalScore: 52,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 68,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0220",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 75,
        penaltyScore: 21,
        finalScore: 54,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 71,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0221",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 70,
        penaltyScore: 40,
        finalScore: 30,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 46,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0222",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 73,
        penaltyScore: 28,
        finalScore: 45,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 58,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0223",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 76,
        penaltyScore: 28,
        finalScore: 48,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 63,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0224",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 78,
        penaltyScore: 28,
        finalScore: 50,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 67,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0225",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 79,
        penaltyScore: 28,
        finalScore: 51,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 69,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0226",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 56,
        penaltyScore: 12,
        finalScore: 44,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 57,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0227",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 59,
        penaltyScore: 0,
        finalScore: 59,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 69,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0228",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 61,
        penaltyScore: 0,
        finalScore: 61,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 73,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0229",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 63,
        penaltyScore: 0,
        finalScore: 63,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 77,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0230",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 65,
        penaltyScore: 0,
        finalScore: 65,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 80,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0231",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 60,
        penaltyScore: 19,
        finalScore: 41,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 55,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0232",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 63,
        penaltyScore: 7,
        finalScore: 56,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 67,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0233",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 65,
        penaltyScore: 7,
        finalScore: 58,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 71,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0234",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 68,
        penaltyScore: 7,
        finalScore: 61,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 76,
        reasons: ["screen06:blocked-by-screen05"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0235",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 69,
        penaltyScore: 7,
        finalScore: 62,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 78,
        reasons: ["screen06:blocked-by-screen05"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0236",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 65,
        penaltyScore: 26,
        finalScore: 39,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 54,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0237",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 68,
        penaltyScore: 14,
        finalScore: 54,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 66,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0238",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 70,
        penaltyScore: 14,
        finalScore: 56,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 70,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0239",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 72,
        penaltyScore: 14,
        finalScore: 58,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 74,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0240",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 74,
        penaltyScore: 14,
        finalScore: 60,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 77,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0241",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 69,
        penaltyScore: 33,
        finalScore: 36,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 52,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0242",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 72,
        penaltyScore: 21,
        finalScore: 51,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 64,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0243",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 74,
        penaltyScore: 21,
        finalScore: 53,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 68,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0244",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 77,
        penaltyScore: 21,
        finalScore: 56,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 73,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0245",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 78,
        penaltyScore: 21,
        finalScore: 57,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 75,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0246",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 73,
        penaltyScore: 40,
        finalScore: 33,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 50,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0247",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 76,
        penaltyScore: 28,
        finalScore: 48,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 63,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0248",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 79,
        penaltyScore: 28,
        finalScore: 51,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 67,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0249",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 81,
        penaltyScore: 28,
        finalScore: 53,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 71,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0250",
    input: {
      industrialReliability: 45,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 82,
        penaltyScore: 28,
        finalScore: 54,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 73,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0251",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 37,
        penaltyScore: 12,
        finalScore: 25,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 26,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0252",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 40,
        penaltyScore: 0,
        finalScore: 40,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 39,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0253",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 43,
        penaltyScore: 0,
        finalScore: 43,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 43,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0254",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 45,
        penaltyScore: 0,
        finalScore: 45,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 47,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0255",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 46,
        penaltyScore: 0,
        finalScore: 46,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 49,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0256",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 42,
        penaltyScore: 19,
        finalScore: 23,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 25,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0257",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 45,
        penaltyScore: 7,
        finalScore: 38,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 38,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0258",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 47,
        penaltyScore: 7,
        finalScore: 40,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 42,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0259",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 49,
        penaltyScore: 7,
        finalScore: 42,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 45,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0260",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 51,
        penaltyScore: 7,
        finalScore: 44,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 48,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0261",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 46,
        penaltyScore: 26,
        finalScore: 20,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 24,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0262",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 49,
        penaltyScore: 14,
        finalScore: 35,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 36,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0263",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 51,
        penaltyScore: 14,
        finalScore: 37,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 40,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0264",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 54,
        penaltyScore: 14,
        finalScore: 40,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 44,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0265",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 55,
        penaltyScore: 14,
        finalScore: 41,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 47,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0266",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 51,
        penaltyScore: 33,
        finalScore: 18,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 22,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0267",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 54,
        penaltyScore: 21,
        finalScore: 33,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 35,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0268",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 56,
        penaltyScore: 21,
        finalScore: 35,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 39,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0269",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 58,
        penaltyScore: 21,
        finalScore: 37,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 42,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0270",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 60,
        penaltyScore: 21,
        finalScore: 39,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 45,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0271",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 55,
        penaltyScore: 40,
        finalScore: 15,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 21,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0272",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 58,
        penaltyScore: 28,
        finalScore: 30,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 33,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0273",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 60,
        penaltyScore: 28,
        finalScore: 32,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 37,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0274",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 63,
        penaltyScore: 28,
        finalScore: 35,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 41,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0275",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 64,
        penaltyScore: 28,
        finalScore: 36,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 44,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0276",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 47,
        penaltyScore: 12,
        finalScore: 35,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 40,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0277",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 50,
        penaltyScore: 0,
        finalScore: 50,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 52,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0278",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 52,
        penaltyScore: 0,
        finalScore: 52,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 56,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0279",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 54,
        penaltyScore: 0,
        finalScore: 54,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 60,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0280",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 56,
        penaltyScore: 0,
        finalScore: 56,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 62,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0281",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 51,
        penaltyScore: 19,
        finalScore: 32,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 38,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0282",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 54,
        penaltyScore: 7,
        finalScore: 47,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 50,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0283",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 56,
        penaltyScore: 7,
        finalScore: 49,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 54,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0284",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 59,
        penaltyScore: 7,
        finalScore: 52,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 58,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0285",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 60,
        penaltyScore: 7,
        finalScore: 53,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 61,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0286",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 56,
        penaltyScore: 26,
        finalScore: 30,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 37,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0287",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 59,
        penaltyScore: 14,
        finalScore: 45,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 49,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0288",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 61,
        penaltyScore: 14,
        finalScore: 47,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 53,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0289",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 63,
        penaltyScore: 14,
        finalScore: 49,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 57,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0290",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 65,
        penaltyScore: 14,
        finalScore: 51,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 60,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0291",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 60,
        penaltyScore: 33,
        finalScore: 27,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 35,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0292",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 63,
        penaltyScore: 21,
        finalScore: 42,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 47,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0293",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 65,
        penaltyScore: 21,
        finalScore: 44,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 51,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0294",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 21,
        finalScore: 46,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 55,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0295",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 69,
        penaltyScore: 21,
        finalScore: 48,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 58,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0296",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 64,
        penaltyScore: 40,
        finalScore: 24,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 33,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0297",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 28,
        finalScore: 39,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 45,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0298",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 70,
        penaltyScore: 28,
        finalScore: 42,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 50,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0299",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 72,
        penaltyScore: 28,
        finalScore: 44,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 54,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0300",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 73,
        penaltyScore: 28,
        finalScore: 45,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 56,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0301",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 53,
        penaltyScore: 12,
        finalScore: 41,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 48,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0302",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 56,
        penaltyScore: 0,
        finalScore: 56,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 60,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0303",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 58,
        penaltyScore: 0,
        finalScore: 58,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 64,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0304",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 60,
        penaltyScore: 0,
        finalScore: 60,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 68,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0305",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 62,
        penaltyScore: 0,
        finalScore: 62,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 71,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0306",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 57,
        penaltyScore: 19,
        finalScore: 38,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 46,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0307",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 60,
        penaltyScore: 7,
        finalScore: 53,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 58,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0308",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 63,
        penaltyScore: 7,
        finalScore: 56,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 63,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0309",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 65,
        penaltyScore: 7,
        finalScore: 58,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 67,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0310",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 66,
        penaltyScore: 7,
        finalScore: 59,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 69,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0311",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 62,
        penaltyScore: 26,
        finalScore: 36,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 45,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0312",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 65,
        penaltyScore: 14,
        finalScore: 51,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 57,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0313",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 14,
        finalScore: 53,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 61,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0314",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 69,
        penaltyScore: 14,
        finalScore: 55,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 65,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0315",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 71,
        penaltyScore: 14,
        finalScore: 57,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 68,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0316",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 66,
        penaltyScore: 33,
        finalScore: 33,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 43,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0317",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 69,
        penaltyScore: 21,
        finalScore: 48,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 55,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0318",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 71,
        penaltyScore: 21,
        finalScore: 50,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 59,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0319",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 74,
        penaltyScore: 21,
        finalScore: 53,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 64,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0320",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 75,
        penaltyScore: 21,
        finalScore: 54,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 66,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0321",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 71,
        penaltyScore: 40,
        finalScore: 31,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 42,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0322",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 74,
        penaltyScore: 28,
        finalScore: 46,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 54,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0323",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 76,
        penaltyScore: 28,
        finalScore: 48,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 58,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0324",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 78,
        penaltyScore: 28,
        finalScore: 50,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 62,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0325",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 80,
        penaltyScore: 28,
        finalScore: 52,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 65,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0326",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 59,
        penaltyScore: 12,
        finalScore: 47,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 56,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0327",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 62,
        penaltyScore: 0,
        finalScore: 62,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 68,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0328",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 64,
        penaltyScore: 0,
        finalScore: 64,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 72,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0329",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 0,
        finalScore: 67,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 77,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0330",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 68,
        penaltyScore: 0,
        finalScore: 68,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 79,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0331",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 64,
        penaltyScore: 19,
        finalScore: 45,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 55,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0332",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 7,
        finalScore: 60,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 67,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0333",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 69,
        penaltyScore: 7,
        finalScore: 62,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 71,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0334",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 71,
        penaltyScore: 7,
        finalScore: 64,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 75,
        reasons: ["screen06:blocked-by-screen05"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0335",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 73,
        penaltyScore: 7,
        finalScore: 66,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 78,
        reasons: ["screen06:blocked-by-screen05"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0336",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 68,
        penaltyScore: 26,
        finalScore: 42,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 53,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0337",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 71,
        penaltyScore: 14,
        finalScore: 57,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 65,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0338",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 73,
        penaltyScore: 14,
        finalScore: 59,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 69,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0339",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 75,
        penaltyScore: 14,
        finalScore: 61,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 73,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0340",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 77,
        penaltyScore: 14,
        finalScore: 63,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 76,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0341",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 72,
        penaltyScore: 33,
        finalScore: 39,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 51,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0342",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 75,
        penaltyScore: 21,
        finalScore: 54,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 64,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0343",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 78,
        penaltyScore: 21,
        finalScore: 57,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 68,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0344",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 80,
        penaltyScore: 21,
        finalScore: 59,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 72,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0345",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 81,
        penaltyScore: 21,
        finalScore: 60,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 74,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0346",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 77,
        penaltyScore: 40,
        finalScore: 37,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 50,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0347",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 80,
        penaltyScore: 28,
        finalScore: 52,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 63,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0348",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 82,
        penaltyScore: 28,
        finalScore: 54,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 66,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0349",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 84,
        penaltyScore: 28,
        finalScore: 56,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 70,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0350",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 86,
        penaltyScore: 28,
        finalScore: 58,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 73,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0351",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 62,
        penaltyScore: 12,
        finalScore: 50,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 60,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0352",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 65,
        penaltyScore: 0,
        finalScore: 65,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 73,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0353",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 0,
        finalScore: 67,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 76,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0354",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 70,
        penaltyScore: 0,
        finalScore: 70,
        reasons: ["screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 81,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0355",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 71,
        penaltyScore: 0,
        finalScore: 71,
        reasons: ["screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 83,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0356",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 19,
        finalScore: 48,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 59,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0357",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 70,
        penaltyScore: 7,
        finalScore: 63,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 71,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0358",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 72,
        penaltyScore: 7,
        finalScore: 65,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 75,
        reasons: ["screen06:blocked-by-screen05"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0359",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 74,
        penaltyScore: 7,
        finalScore: 67,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 79,
        reasons: ["screen06:blocked-by-screen05"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0360",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 76,
        penaltyScore: 7,
        finalScore: 69,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 82,
        reasons: ["screen06:blocked-by-screen05"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0361",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 71,
        penaltyScore: 26,
        finalScore: 45,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 57,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0362",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 74,
        penaltyScore: 14,
        finalScore: 60,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 70,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0363",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 76,
        penaltyScore: 14,
        finalScore: 62,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 73,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0364",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 79,
        penaltyScore: 14,
        finalScore: 65,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 78,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0365",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 80,
        penaltyScore: 14,
        finalScore: 66,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 80,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0366",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 75,
        penaltyScore: 33,
        finalScore: 42,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 56,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0367",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 78,
        penaltyScore: 21,
        finalScore: 57,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 68,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0368",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 81,
        penaltyScore: 21,
        finalScore: 60,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 72,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0369",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 83,
        penaltyScore: 21,
        finalScore: 62,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 76,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0370",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 84,
        penaltyScore: 21,
        finalScore: 63,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 79,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0371",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 80,
        penaltyScore: 40,
        finalScore: 40,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 54,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0372",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 83,
        penaltyScore: 28,
        finalScore: 55,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 67,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0373",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 85,
        penaltyScore: 28,
        finalScore: 57,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 71,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0374",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 87,
        penaltyScore: 28,
        finalScore: 59,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 74,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0375",
    input: {
      industrialReliability: 65,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 89,
        penaltyScore: 28,
        finalScore: 61,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 77,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0376",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 44,
        penaltyScore: 12,
        finalScore: 32,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 31,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0377",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 47,
        penaltyScore: 0,
        finalScore: 47,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 43,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0378",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 49,
        penaltyScore: 0,
        finalScore: 49,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 47,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0379",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 51,
        penaltyScore: 0,
        finalScore: 51,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 51,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0380",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 53,
        penaltyScore: 0,
        finalScore: 53,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 54,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0381",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 48,
        penaltyScore: 19,
        finalScore: 29,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 29,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0382",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 51,
        penaltyScore: 7,
        finalScore: 44,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 41,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0383",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 53,
        penaltyScore: 7,
        finalScore: 46,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 45,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0384",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 56,
        penaltyScore: 7,
        finalScore: 49,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 49,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0385",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 57,
        penaltyScore: 7,
        finalScore: 50,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 52,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0386",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 53,
        penaltyScore: 26,
        finalScore: 27,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 28,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0387",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 56,
        penaltyScore: 14,
        finalScore: 42,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 40,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0388",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 58,
        penaltyScore: 14,
        finalScore: 44,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 44,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0389",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 60,
        penaltyScore: 14,
        finalScore: 46,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 48,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0390",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 62,
        penaltyScore: 14,
        finalScore: 48,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 51,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0391",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 57,
        penaltyScore: 33,
        finalScore: 24,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 26,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0392",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 60,
        penaltyScore: 21,
        finalScore: 39,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 38,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0393",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 62,
        penaltyScore: 21,
        finalScore: 41,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 42,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0394",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 65,
        penaltyScore: 21,
        finalScore: 44,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 47,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0395",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 66,
        penaltyScore: 21,
        finalScore: 45,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 49,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0396",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 61,
        penaltyScore: 40,
        finalScore: 21,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 24,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0397",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 64,
        penaltyScore: 28,
        finalScore: 36,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 36,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0398",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 28,
        finalScore: 39,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 41,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0399",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 69,
        penaltyScore: 28,
        finalScore: 41,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 45,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0400",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 70,
        penaltyScore: 28,
        finalScore: 42,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 47,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0401",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 53,
        penaltyScore: 12,
        finalScore: 41,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 43,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0402",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 56,
        penaltyScore: 0,
        finalScore: 56,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 55,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0403",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 58,
        penaltyScore: 0,
        finalScore: 58,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 59,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0404",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 61,
        penaltyScore: 0,
        finalScore: 61,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 64,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0405",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 62,
        penaltyScore: 0,
        finalScore: 62,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 66,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0406",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 58,
        penaltyScore: 19,
        finalScore: 39,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 42,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0407",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 61,
        penaltyScore: 7,
        finalScore: 54,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 54,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0408",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 63,
        penaltyScore: 7,
        finalScore: 56,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 58,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0409",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 65,
        penaltyScore: 7,
        finalScore: 58,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 62,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0410",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 7,
        finalScore: 60,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 65,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0411",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 62,
        penaltyScore: 26,
        finalScore: 36,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 40,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0412",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 65,
        penaltyScore: 14,
        finalScore: 51,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 52,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0413",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 14,
        finalScore: 53,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 56,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0414",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 69,
        penaltyScore: 14,
        finalScore: 55,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 60,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0415",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 71,
        penaltyScore: 14,
        finalScore: 57,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 63,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0416",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 66,
        penaltyScore: 33,
        finalScore: 33,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 38,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0417",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 69,
        penaltyScore: 21,
        finalScore: 48,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 51,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0418",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 72,
        penaltyScore: 21,
        finalScore: 51,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 55,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0419",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 74,
        penaltyScore: 21,
        finalScore: 53,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 59,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0420",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 75,
        penaltyScore: 21,
        finalScore: 54,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 61,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0421",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 71,
        penaltyScore: 40,
        finalScore: 31,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 37,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0422",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 74,
        penaltyScore: 28,
        finalScore: 46,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 49,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0423",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 76,
        penaltyScore: 28,
        finalScore: 48,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 53,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0424",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 78,
        penaltyScore: 28,
        finalScore: 50,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 57,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0425",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 80,
        penaltyScore: 28,
        finalScore: 52,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 60,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0426",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 59,
        penaltyScore: 12,
        finalScore: 47,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 51,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0427",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 62,
        penaltyScore: 0,
        finalScore: 62,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 64,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0428",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 65,
        penaltyScore: 0,
        finalScore: 65,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 68,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0429",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 0,
        finalScore: 67,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 72,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0430",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 68,
        penaltyScore: 0,
        finalScore: 68,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 74,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0431",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 64,
        penaltyScore: 19,
        finalScore: 45,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 50,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0432",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 7,
        finalScore: 60,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 62,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0433",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 69,
        penaltyScore: 7,
        finalScore: 62,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 66,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0434",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 71,
        penaltyScore: 7,
        finalScore: 64,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 70,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0435",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 73,
        penaltyScore: 7,
        finalScore: 66,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 73,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0436",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 68,
        penaltyScore: 26,
        finalScore: 42,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 48,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0437",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 71,
        penaltyScore: 14,
        finalScore: 57,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 61,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0438",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 73,
        penaltyScore: 14,
        finalScore: 59,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 65,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0439",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 76,
        penaltyScore: 14,
        finalScore: 62,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 69,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0440",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 77,
        penaltyScore: 14,
        finalScore: 63,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 71,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0441",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 73,
        penaltyScore: 33,
        finalScore: 40,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 47,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0442",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 76,
        penaltyScore: 21,
        finalScore: 55,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 60,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0443",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 78,
        penaltyScore: 21,
        finalScore: 57,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 63,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0444",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 80,
        penaltyScore: 21,
        finalScore: 59,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 67,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0445",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 82,
        penaltyScore: 21,
        finalScore: 61,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 70,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0446",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 77,
        penaltyScore: 40,
        finalScore: 37,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 45,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0447",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 80,
        penaltyScore: 28,
        finalScore: 52,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 58,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0448",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 82,
        penaltyScore: 28,
        finalScore: 54,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 62,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0449",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 84,
        penaltyScore: 28,
        finalScore: 56,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 65,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0450",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 86,
        penaltyScore: 28,
        finalScore: 58,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 68,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0451",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 66,
        penaltyScore: 12,
        finalScore: 54,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 60,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0452",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 69,
        penaltyScore: 0,
        finalScore: 69,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 72,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0453",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 71,
        penaltyScore: 0,
        finalScore: 71,
        reasons: ["screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 76,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0454",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 73,
        penaltyScore: 0,
        finalScore: 73,
        reasons: ["screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 80,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0455",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 75,
        penaltyScore: 0,
        finalScore: 75,
        reasons: ["screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 83,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0456",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 70,
        penaltyScore: 19,
        finalScore: 51,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 58,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0457",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 73,
        penaltyScore: 7,
        finalScore: 66,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 71,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0458",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 75,
        penaltyScore: 7,
        finalScore: 68,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 75,
        reasons: ["screen06:blocked-by-screen05"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0459",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 77,
        penaltyScore: 7,
        finalScore: 70,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 78,
        reasons: ["screen06:blocked-by-screen05"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0460",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 79,
        penaltyScore: 7,
        finalScore: 72,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 81,
        reasons: ["screen06:blocked-by-screen05"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0461",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 74,
        penaltyScore: 26,
        finalScore: 48,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 57,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0462",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 77,
        penaltyScore: 14,
        finalScore: 63,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 69,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0463",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 80,
        penaltyScore: 14,
        finalScore: 66,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 73,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0464",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 82,
        penaltyScore: 14,
        finalScore: 68,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 77,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0465",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 83,
        penaltyScore: 14,
        finalScore: 69,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 80,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0466",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 79,
        penaltyScore: 33,
        finalScore: 46,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 55,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0467",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 82,
        penaltyScore: 21,
        finalScore: 61,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 68,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0468",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 84,
        penaltyScore: 21,
        finalScore: 63,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 72,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0469",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 86,
        penaltyScore: 21,
        finalScore: 65,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 76,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0470",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 88,
        penaltyScore: 21,
        finalScore: 67,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 78,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0471",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 83,
        penaltyScore: 40,
        finalScore: 43,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 54,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0472",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 86,
        penaltyScore: 28,
        finalScore: 58,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 66,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0473",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 88,
        penaltyScore: 28,
        finalScore: 60,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 70,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0474",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 91,
        penaltyScore: 28,
        finalScore: 63,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 74,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0475",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 92,
        penaltyScore: 28,
        finalScore: 64,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 77,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0476",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 69,
        penaltyScore: 12,
        finalScore: 57,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 64,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0477",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 72,
        penaltyScore: 0,
        finalScore: 72,
        reasons: ["screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 77,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0478",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 74,
        penaltyScore: 0,
        finalScore: 74,
        reasons: ["screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 80,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0479",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 76,
        penaltyScore: 0,
        finalScore: 76,
        reasons: ["screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 84,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0480",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 78,
        penaltyScore: 0,
        finalScore: 78,
        reasons: ["screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 87,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0481",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 73,
        penaltyScore: 19,
        finalScore: 54,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 63,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0482",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 76,
        penaltyScore: 7,
        finalScore: 69,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 75,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0483",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 78,
        penaltyScore: 7,
        finalScore: 71,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 79,
        reasons: ["screen06:blocked-by-screen05"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0484",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 81,
        penaltyScore: 7,
        finalScore: 74,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 83,
        reasons: ["screen06:blocked-by-screen05"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0485",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 82,
        penaltyScore: 7,
        finalScore: 75,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 86,
        reasons: ["screen06:blocked-by-screen05"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0486",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 77,
        penaltyScore: 26,
        finalScore: 51,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 61,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0487",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 80,
        penaltyScore: 14,
        finalScore: 66,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 73,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0488",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 83,
        penaltyScore: 14,
        finalScore: 69,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 78,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0489",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 85,
        penaltyScore: 14,
        finalScore: 71,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 81,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0490",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 86,
        penaltyScore: 14,
        finalScore: 72,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 84,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0491",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 82,
        penaltyScore: 33,
        finalScore: 49,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 60,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0492",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 85,
        penaltyScore: 21,
        finalScore: 64,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 72,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0493",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 87,
        penaltyScore: 21,
        finalScore: 66,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 76,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0494",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 89,
        penaltyScore: 21,
        finalScore: 68,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 80,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0495",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 91,
        penaltyScore: 21,
        finalScore: 70,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 83,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0496",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 86,
        penaltyScore: 40,
        finalScore: 46,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 58,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0497",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 89,
        penaltyScore: 28,
        finalScore: 61,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 70,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0498",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 91,
        penaltyScore: 28,
        finalScore: 63,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 74,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0499",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 94,
        penaltyScore: 28,
        finalScore: 66,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 78,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0500",
    input: {
      industrialReliability: 85,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 95,
        penaltyScore: 28,
        finalScore: 67,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 81,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0501",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 49,
        penaltyScore: 12,
        finalScore: 37,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 33,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0502",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 52,
        penaltyScore: 0,
        finalScore: 52,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 46,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0503",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 54,
        penaltyScore: 0,
        finalScore: 54,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 50,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0504",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 56,
        penaltyScore: 0,
        finalScore: 56,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 53,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0505",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 58,
        penaltyScore: 0,
        finalScore: 58,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 56,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0506",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 53,
        penaltyScore: 19,
        finalScore: 34,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 32,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0507",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 56,
        penaltyScore: 7,
        finalScore: 49,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 44,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0508",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 58,
        penaltyScore: 7,
        finalScore: 51,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 48,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0509",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 61,
        penaltyScore: 7,
        finalScore: 54,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 52,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0510",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 62,
        penaltyScore: 7,
        finalScore: 55,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 55,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0511",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 57,
        penaltyScore: 26,
        finalScore: 31,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 30,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0512",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 60,
        penaltyScore: 14,
        finalScore: 46,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 42,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0513",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 63,
        penaltyScore: 14,
        finalScore: 49,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 47,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0514",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 65,
        penaltyScore: 14,
        finalScore: 51,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 51,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0515",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 66,
        penaltyScore: 14,
        finalScore: 52,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 53,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0516",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 62,
        penaltyScore: 33,
        finalScore: 29,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 29,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0517",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 65,
        penaltyScore: 21,
        finalScore: 44,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 41,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0518",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 21,
        finalScore: 46,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 45,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0519",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 69,
        penaltyScore: 21,
        finalScore: 48,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 49,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0520",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 71,
        penaltyScore: 21,
        finalScore: 50,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 52,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0521",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 66,
        penaltyScore: 40,
        finalScore: 26,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 27,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0522",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 69,
        penaltyScore: 28,
        finalScore: 41,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 39,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0523",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 71,
        penaltyScore: 28,
        finalScore: 43,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 43,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0524",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 74,
        penaltyScore: 28,
        finalScore: 46,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 48,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0525",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 20,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 75,
        penaltyScore: 28,
        finalScore: 47,
        reasons: ["screen05:final-score-below-70", "screen05:software-completeness-below-50", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 50,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0526",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 58,
        penaltyScore: 12,
        finalScore: 46,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 46,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0527",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 61,
        penaltyScore: 0,
        finalScore: 61,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 58,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0528",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 63,
        penaltyScore: 0,
        finalScore: 63,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 62,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0529",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 65,
        penaltyScore: 0,
        finalScore: 65,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 66,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0530",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 0,
        finalScore: 67,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 69,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0531",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 62,
        penaltyScore: 19,
        finalScore: 43,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 44,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0532",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 65,
        penaltyScore: 7,
        finalScore: 58,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 56,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0533",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 68,
        penaltyScore: 7,
        finalScore: 61,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 61,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0534",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 70,
        penaltyScore: 7,
        finalScore: 63,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 65,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0535",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 71,
        penaltyScore: 7,
        finalScore: 64,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 67,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0536",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 26,
        finalScore: 41,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 43,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0537",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 70,
        penaltyScore: 14,
        finalScore: 56,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 55,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0538",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 72,
        penaltyScore: 14,
        finalScore: 58,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 59,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0539",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 74,
        penaltyScore: 14,
        finalScore: 60,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 63,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0540",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 76,
        penaltyScore: 14,
        finalScore: 62,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 66,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0541",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 71,
        penaltyScore: 33,
        finalScore: 38,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 41,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0542",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 74,
        penaltyScore: 21,
        finalScore: 53,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 54,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0543",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 76,
        penaltyScore: 21,
        finalScore: 55,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 57,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0544",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 79,
        penaltyScore: 21,
        finalScore: 58,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 62,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0545",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 80,
        penaltyScore: 21,
        finalScore: 59,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 64,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0546",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 76,
        penaltyScore: 40,
        finalScore: 36,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 40,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0547",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 79,
        penaltyScore: 28,
        finalScore: 51,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 52,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0548",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 81,
        penaltyScore: 28,
        finalScore: 53,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 56,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0549",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 83,
        penaltyScore: 28,
        finalScore: 55,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 60,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0550",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 50,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 85,
        penaltyScore: 28,
        finalScore: 57,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 63,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0551",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 64,
        penaltyScore: 12,
        finalScore: 52,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 54,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0552",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 67,
        penaltyScore: 0,
        finalScore: 67,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 66,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0553",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 69,
        penaltyScore: 0,
        finalScore: 69,
        reasons: ["screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 70,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0554",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 72,
        penaltyScore: 0,
        finalScore: 72,
        reasons: ["screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 75,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0555",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 73,
        penaltyScore: 0,
        finalScore: 73,
        reasons: ["screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 77,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0556",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 69,
        penaltyScore: 19,
        finalScore: 50,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 53,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0557",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 72,
        penaltyScore: 7,
        finalScore: 65,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 65,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0558",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 74,
        penaltyScore: 7,
        finalScore: 67,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 69,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0559",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 76,
        penaltyScore: 7,
        finalScore: 69,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 73,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0560",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 78,
        penaltyScore: 7,
        finalScore: 71,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 76,
        reasons: ["screen06:blocked-by-screen05"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0561",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 73,
        penaltyScore: 26,
        finalScore: 47,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 51,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0562",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 76,
        penaltyScore: 14,
        finalScore: 62,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 64,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0563",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 78,
        penaltyScore: 14,
        finalScore: 64,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 67,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0564",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 80,
        penaltyScore: 14,
        finalScore: 66,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 71,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0565",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 82,
        penaltyScore: 14,
        finalScore: 68,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 74,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0566",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 77,
        penaltyScore: 33,
        finalScore: 44,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 50,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0567",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 80,
        penaltyScore: 21,
        finalScore: 59,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 62,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0568",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 83,
        penaltyScore: 21,
        finalScore: 62,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 66,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0569",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 85,
        penaltyScore: 21,
        finalScore: 64,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 70,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0570",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 86,
        penaltyScore: 21,
        finalScore: 65,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 73,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0571",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 82,
        penaltyScore: 40,
        finalScore: 42,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 48,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0572",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 85,
        penaltyScore: 28,
        finalScore: 57,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 61,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0573",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 87,
        penaltyScore: 28,
        finalScore: 59,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 65,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0574",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 89,
        penaltyScore: 28,
        finalScore: 61,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 68,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0575",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 70,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 91,
        penaltyScore: 28,
        finalScore: 63,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 71,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0576",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 70,
        penaltyScore: 12,
        finalScore: 58,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 62,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0577",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 73,
        penaltyScore: 0,
        finalScore: 73,
        reasons: ["screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 75,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0578",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 76,
        penaltyScore: 0,
        finalScore: 76,
        reasons: ["screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 79,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0579",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 78,
        penaltyScore: 0,
        finalScore: 78,
        reasons: ["screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 83,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0580",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 79,
        penaltyScore: 0,
        finalScore: 79,
        reasons: ["screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 85,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0581",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 75,
        penaltyScore: 19,
        finalScore: 56,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 61,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0582",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 78,
        penaltyScore: 7,
        finalScore: 71,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 74,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0583",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 80,
        penaltyScore: 7,
        finalScore: 73,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 77,
        reasons: ["screen06:blocked-by-screen05"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0584",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 82,
        penaltyScore: 7,
        finalScore: 75,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 81,
        reasons: ["screen06:blocked-by-screen05"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0585",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 84,
        penaltyScore: 7,
        finalScore: 77,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 84,
        reasons: ["screen06:blocked-by-screen05"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0586",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 79,
        penaltyScore: 26,
        finalScore: 53,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 60,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0587",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 82,
        penaltyScore: 14,
        finalScore: 68,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 72,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0588",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 84,
        penaltyScore: 14,
        finalScore: 70,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 76,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0589",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 87,
        penaltyScore: 14,
        finalScore: 73,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 80,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0590",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 88,
        penaltyScore: 14,
        finalScore: 74,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 83,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0591",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 84,
        penaltyScore: 33,
        finalScore: 51,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 58,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0592",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 87,
        penaltyScore: 21,
        finalScore: 66,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 71,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0593",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 89,
        penaltyScore: 21,
        finalScore: 68,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 75,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0594",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 91,
        penaltyScore: 21,
        finalScore: 70,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 78,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0595",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 93,
        penaltyScore: 21,
        finalScore: 72,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 81,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0596",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 88,
        penaltyScore: 40,
        finalScore: 48,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 57,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0597",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 91,
        penaltyScore: 28,
        finalScore: 63,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 69,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0598",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 93,
        penaltyScore: 28,
        finalScore: 65,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 73,
        reasons: ["screen06:blocked-by-screen05", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0599",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 95,
        penaltyScore: 28,
        finalScore: 67,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 77,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0600",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 90,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 97,
        penaltyScore: 28,
        finalScore: 69,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 80,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0601",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 73,
        penaltyScore: 12,
        finalScore: 61,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 67,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0602",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 76,
        penaltyScore: 0,
        finalScore: 76,
        reasons: ["screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 79,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0603",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 79,
        penaltyScore: 0,
        finalScore: 79,
        reasons: ["screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 83,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0604",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 81,
        penaltyScore: 0,
        finalScore: 81,
        reasons: ["screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 87,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0605",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 20,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 0
    },
    expected: {
      screen05: {
        weightedScore: 82,
        penaltyScore: 0,
        finalScore: 82,
        reasons: ["screen05:traction-strength-below-40"],
        decision: "hold"
      },
      screen06: {
        executionScore: 90,
        reasons: ["screen06:blocked-by-screen05"],
        band: "watch"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0606",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 78,
        penaltyScore: 19,
        finalScore: 59,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 65,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0607",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 81,
        penaltyScore: 7,
        finalScore: 74,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 78,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0608",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 83,
        penaltyScore: 7,
        finalScore: 76,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 82,
        reasons: ["screen06:blocked-by-screen05"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0609",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 85,
        penaltyScore: 7,
        finalScore: 78,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 85,
        reasons: ["screen06:blocked-by-screen05"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0610",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 40,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 1
    },
    expected: {
      screen05: {
        weightedScore: 87,
        penaltyScore: 7,
        finalScore: 80,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 88,
        reasons: ["screen06:blocked-by-screen05"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0611",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 82,
        penaltyScore: 26,
        finalScore: 56,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 64,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0612",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 85,
        penaltyScore: 14,
        finalScore: 71,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 76,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0613",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 87,
        penaltyScore: 14,
        finalScore: 73,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 80,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0614",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 90,
        penaltyScore: 14,
        finalScore: 76,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 84,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0615",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 60,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 2
    },
    expected: {
      screen05: {
        weightedScore: 91,
        penaltyScore: 14,
        finalScore: 77,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 87,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0616",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 87,
        penaltyScore: 33,
        finalScore: 54,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 63,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0617",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 90,
        penaltyScore: 21,
        finalScore: 69,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 75,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0618",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 92,
        penaltyScore: 21,
        finalScore: 71,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 79,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0619",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 94,
        penaltyScore: 21,
        finalScore: 73,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 83,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0620",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 80,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 3
    },
    expected: {
      screen05: {
        weightedScore: 96,
        penaltyScore: 21,
        finalScore: 75,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 86,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0621",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 40,
      cashRunwayMonths: 3,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 91,
        penaltyScore: 40,
        finalScore: 51,
        reasons: ["screen05:cash-runway-below-6m", "screen05:compliance-posture-below-60", "screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 61,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0622",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 60,
      cashRunwayMonths: 6,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 94,
        penaltyScore: 28,
        finalScore: 66,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 73,
        reasons: ["screen06:blocked-by-screen05", "screen06:cash-runway-below-9m", "screen06:execution-score-below-75", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0623",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 75,
      cashRunwayMonths: 9,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 96,
        penaltyScore: 28,
        finalScore: 68,
        reasons: ["screen05:final-score-below-70", "screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 77,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0624",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 90,
      cashRunwayMonths: 12,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 99,
        penaltyScore: 28,
        finalScore: 71,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 81,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  },
  {
    id: "case_0625",
    input: {
      industrialReliability: 100,
      softwareCompleteness: 100,
      tractionStrength: 100,
      compliancePosture: 100,
      cashRunwayMonths: 18,
      unresolvedCriticalIssues: 4
    },
    expected: {
      screen05: {
        weightedScore: 100,
        penaltyScore: 28,
        finalScore: 72,
        reasons: ["screen05:unresolved-critical-issues"],
        decision: "hold"
      },
      screen06: {
        executionScore: 84,
        reasons: ["screen06:blocked-by-screen05", "screen06:more-than-one-critical-issue"],
        band: "blocked"
      }
    },
    expectedTransitions: {
      draftRunScreen05: "screen05-assessed",
      draftRunScreen06: "screen05-assessed",
      approvalState: "screen06-assessed",
      approvalLock: "approval-gates-not-satisfied",
      runScreen06Lock: "screen05-not-advanced",
      rejectionState: "rejected",
      resetState: "draft"
    }
  }
] as const;
