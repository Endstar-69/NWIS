import React from 'react';

interface RiskPillProps {
  level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | string;
  probability?: number;
  showIcon?: boolean;
  size?: 'sm' | 'md';
}

export const RiskPill: React.FC<RiskPillProps> = ({
  level,
  probability,
  showIcon = true,
  size = 'sm'
}) => {
  const normLevel = (level || 'LOW').toUpperCase();

  const styles: Record<string, { bg: string; text: string; border: string; dot: string }> = {
    LOW: {
      bg: 'bg-emerald-500/10 dark:bg-emerald-950/40',
      text: 'text-emerald-700 dark:text-emerald-400',
      border: 'border-emerald-500/30 dark:border-emerald-700/50',
      dot: 'bg-emerald-500'
    },
    MEDIUM: {
      bg: 'bg-amber-500/10 dark:bg-amber-950/40',
      text: 'text-amber-700 dark:text-amber-400',
      border: 'border-amber-500/30 dark:border-amber-700/50',
      dot: 'bg-amber-500'
    },
    HIGH: {
      bg: 'bg-orange-500/10 dark:bg-orange-950/40',
      text: 'text-orange-700 dark:text-orange-400',
      border: 'border-orange-500/30 dark:border-orange-700/50',
      dot: 'bg-orange-500'
    },
    CRITICAL: {
      bg: 'bg-rose-500/10 dark:bg-rose-950/50',
      text: 'text-rose-700 dark:text-rose-400',
      border: 'border-rose-500/30 dark:border-rose-700/50',
      dot: 'bg-rose-500'
    }
  };

  const style = styles[normLevel] || styles.LOW;

  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded border ${
      size === 'sm' ? 'text-xs' : 'text-sm font-semibold px-2.5 py-1'
    } font-sans font-medium tracking-tight ${style.bg} ${style.text} ${style.border}`}>
      {showIcon && (
        <span className={`w-1.5 h-1.5 rounded-full ${style.dot} ${
          normLevel === 'CRITICAL' || normLevel === 'HIGH' ? 'animate-pulse' : ''
        }`} />
      )}
      <span className="font-semibold">{normLevel}</span>
      {probability !== undefined && (
        <span className="opacity-80 font-mono text-[11px]">
          ({(probability * 100).toFixed(0)}%)
        </span>
      )}
    </span>
  );
};
