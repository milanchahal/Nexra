import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface JobsColumnProps {
  title: string;
  count: number;
  children: ReactNode;
  className?: string;
}

export function JobsColumn({ title, count, children, className }: JobsColumnProps) {
  return (
    <div className={cn('flex flex-col h-full min-w-[300px] bg-muted/30 rounded-xl p-4', className)}>
      <div className="flex items-center justify-between mb-4 px-1">
        <h2 className="font-semibold text-foreground flex items-center gap-2">
          {title}
          <span className="text-xs font-normal text-muted-foreground bg-muted px-2 py-0.5 rounded-full">
            {count}
          </span>
        </h2>
      </div>
      <div className="flex-1 overflow-y-auto space-y-3 min-h-0 custom-scrollbar pr-1">
        {children}
      </div>
    </div>
  );
}
