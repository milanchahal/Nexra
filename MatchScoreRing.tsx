interface MatchScoreRingProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showBreakdown?: boolean;
}

export function MatchScoreRing({ score, size = 'md', showBreakdown = true }: MatchScoreRingProps) {
  // Size configuration
  const sizes = {
    sm: { outer: 60, stroke: 4, font: 'text-lg' },
    md: { outer: 100, stroke: 6, font: 'text-2xl' },
    lg: { outer: 140, stroke: 8, font: 'text-3xl' },
  };
  
  const config = sizes[size];
  const radius = (config.outer - config.stroke) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (score / 100) * circumference;
  
  // Color based on score
  const getColor = () => {
    if (score >= 80) return { stroke: '#10b981', bg: 'from-emerald-500/20 to-teal-500/20', text: 'text-emerald-400' };
    if (score >= 60) return { stroke: '#f59e0b', bg: 'from-yellow-500/20 to-orange-500/20', text: 'text-yellow-400' };
    return { stroke: '#ef4444', bg: 'from-red-500/20 to-pink-500/20', text: 'text-red-400' };
  };
  
  const colors = getColor();
  
  // Match label
  const getLabel = () => {
    if (score >= 90) return 'STRONG MATCH';
    if (score >= 70) return 'GOOD MATCH';
    if (score >= 50) return 'FAIR MATCH';
    return 'LOW MATCH';
  };

  // Breakdown scores (simulated based on overall)
  const breakdown = {
    expLevel: Math.min(100, Math.round(score + Math.random() * 10 - 5)),
    skill: Math.min(100, Math.round(score + Math.random() * 10 - 5)),
    industryExp: Math.min(100, Math.round(score - Math.random() * 15)),
  };

  return (
    <div className="flex flex-col items-center gap-2">
      {/* Main Ring */}
      <div className={`relative bg-gradient-to-br ${colors.bg} rounded-2xl p-4`}>
        <svg
          width={config.outer}
          height={config.outer}
          className="transform -rotate-90"
        >
          {/* Background circle */}
          <circle
            cx={config.outer / 2}
            cy={config.outer / 2}
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={config.stroke}
            className="text-muted/30"
          />
          {/* Progress circle */}
          <circle
            cx={config.outer / 2}
            cy={config.outer / 2}
            r={radius}
            fill="none"
            stroke={colors.stroke}
            strokeWidth={config.stroke}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        
        {/* Score text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`${config.font} font-bold ${colors.text}`}>
            {score}%
          </span>
        </div>
      </div>
      
      {/* Label */}
      <div className={`text-xs font-bold ${colors.text} tracking-wider`}>
        {getLabel()}
      </div>
      
      {/* Additional badges */}
      {score >= 80 && (
        <div className="px-2 py-1 bg-muted/50 rounded-full text-xs text-muted-foreground">
          • No H1B
        </div>
      )}
      
      {/* Breakdown */}
      {showBreakdown && size !== 'sm' && (
        <div className="flex gap-3 mt-2">
          <div className="text-center">
            <div className={`text-sm font-bold ${colors.text}`}>{breakdown.expLevel}%</div>
            <div className="text-[10px] text-muted-foreground">Exp. Level</div>
          </div>
          <div className="text-center">
            <div className={`text-sm font-bold ${colors.text}`}>{breakdown.skill}%</div>
            <div className="text-[10px] text-muted-foreground">Skill</div>
          </div>
          <div className="text-center">
            <div className={`text-sm font-bold ${colors.text}`}>{breakdown.industryExp}%</div>
            <div className="text-[10px] text-muted-foreground">Industry Exp.</div>
          </div>
        </div>
      )}
    </div>
  );
}
