import React from 'react';
import { cn } from '@/lib/utils';
import { cva, type VariantProps } from 'class-variance-authority';

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2',
  {
    variants: {
      variant: {
        success: 'border-emerald-500/20 bg-emerald-500/10 text-emerald-400',
        info: 'border-blue-500/20 bg-blue-500/10 text-blue-400',
        warning: 'border-amber-500/20 bg-amber-500/10 text-amber-400',
        danger: 'border-red-500/20 bg-red-500/10 text-red-400',
        neutral: 'border-slate-500/20 bg-slate-500/10 text-slate-400',
        primary: 'border-purple-500/20 bg-purple-500/10 text-purple-400',
      },
      size: {
        sm: 'text-[10px] px-2 py-0',
        md: 'text-xs',
      },
    },
    defaultVariants: {
      variant: 'neutral',
      size: 'md',
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, size, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant, size }), className)} {...props} />
  );
}
