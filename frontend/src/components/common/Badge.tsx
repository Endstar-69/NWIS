import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'neutral' | 'purple' | 'sky';
  size?: 'xs' | 'sm' | 'md';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  size = 'sm',
  className = ''
}) => {
  const variantStyles = {
    primary: 'bg-sky-500/10 text-sky-400 border-sky-500/25 dark:text-sky-400',
    sky: 'bg-sky-500/10 text-sky-600 dark:text-sky-400 border-sky-500/30',
    success: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30',
    warning: 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30',
    danger: 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/30',
    neutral: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border-slate-200 dark:border-slate-700',
    purple: 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/30'
  };

  const sizeStyles = {
    xs: 'text-[10px] px-1.5 py-0.2',
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1 font-medium'
  };

  return (
    <span className={`inline-flex items-center gap-1 font-sans font-medium rounded border ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}>
      {children}
    </span>
  );
};
