import React from 'react';
export function PrismoQuestionChips({ questions = [], onPick }: { questions?: string[]; onPick?: (question: string)=>void }) {
  return <div className="prismo-question-chips">{questions.slice(0, 8).map((q) => <button key={q} onClick={() => onPick?.(q)}>{q}</button>)}</div>;
}
