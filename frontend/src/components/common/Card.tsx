import React from 'react';
import { useTheme } from '../../store/themeContext';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  headerAction?: React.ReactNode;
  footer?: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  title,
  subtitle,
  headerAction,
  footer
}) => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <div className={`${
      isDark
        ? 'bg-[#0B111E] border-slate-800/90 text-slate-100 shadow-sm'
        : 'bg-white border-slate-200 text-slate-900 shadow-xs'
    } border rounded-lg flex flex-col transition-colors ${className}`}>
      {(title || headerAction) && (
        <div className={`px-4 py-3 border-b ${
          isDark ? 'border-slate-800/80 bg-slate-900/30' : 'border-slate-100 bg-slate-50/60'
        } flex items-center justify-between gap-3`}>
          <div>
            {title && (
              <h3 className={`text-xs font-semibold uppercase tracking-wider ${
                isDark ? 'text-slate-200' : 'text-slate-800'
              } font-sans`}>
                {title}
              </h3>
            )}
            {subtitle && (
              <p className={`text-[11px] ${isDark ? 'text-slate-400' : 'text-slate-500'} font-sans mt-0.5`}>
                {subtitle}
              </p>
            )}
          </div>
          {headerAction && <div className="shrink-0">{headerAction}</div>}
        </div>
      )}
      <div className="p-4 flex-1">{children}</div>
      {footer && (
        <div className={`px-4 py-2.5 border-t ${
          isDark ? 'border-slate-800/80 bg-slate-900/20 text-slate-400' : 'border-slate-100 bg-slate-50/40 text-slate-600'
        } text-xs font-sans`}>
          {footer}
        </div>
      )}
    </div>
  );
};
