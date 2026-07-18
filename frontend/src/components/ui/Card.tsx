import React from 'react';
import { cn } from '@/lib/utils';
import { cva, type VariantProps } from 'class-variance-authority';

const cardVariants = cva(
  'rounded-xl border shadow-sm transition-all duration-300',
  {
    variants: {
      variant: {
        default: 'bg-slate-900/40 backdrop-blur-md border-slate-800/50',
        solid: 'bg-slate-900 border-slate-800',
        gradient: 'bg-slate-900/60 backdrop-blur-xl border-transparent bg-gradient-to-br from-slate-800 to-slate-900',
      },
      hover: {
        true: 'hover:-translate-y-1 hover:shadow-lg hover:shadow-blue-900/20 hover:border-blue-500/30',
        false: '',
      },
    },
    defaultVariants: {
      variant: 'default',
      hover: false,
    },
  }
);

export interface CardProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof cardVariants> {}

export function Card({ className, variant, hover, ...props }: CardProps) {
  return (
    <div className={cn(cardVariants({ variant, hover }), className)} {...props} />
  );
}
