export default function AttendanceCard({ subject, index }) {
  const percentage = parseFloat(subject.TotalPercentage) || 0;
  const delivered = subject.Total_Delv ?? 0;
  const attended = subject.Total_Attd ?? 0;

  // SVG circular progress
  const radius = 25;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  // Color based on percentage
  let level = 'high';
  if (percentage < 65) level = 'low';
  else if (percentage < 75) level = 'medium';

  const delay = Math.min(index, 5);

  return (
    <div className={`card attendance-card fade-in stagger-${delay + 1}`}>
      <div className="attendance-ring">
        <svg viewBox="0 0 56 56">
          <circle className="ring-bg" cx="28" cy="28" r={radius} />
          <circle
            className={`ring-fill ${level}`}
            cx="28"
            cy="28"
            r={radius}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
          />
        </svg>
        <span className={`ring-text ${level}`}>{percentage}%</span>
      </div>
      <div className="attendance-info">
        <div className="subject-name" title={subject.Title}>
          {subject.Title}
        </div>
        <div className="subject-stats">
          <span>
            <span className="stat-dot delivered" />
            {delivered} delivered
          </span>
          <span>
            <span className="stat-dot attended" />
            {attended} attended
          </span>
        </div>
      </div>
    </div>
  );
}
