export default function MarksCard({ subject }) {
  const { name, marks } = subject;

  // Check if it's a grade-only subject (like "- Grade" with value "A+")
  const isGradeOnly =
    marks.length === 1 &&
    marks[0].element.toLowerCase().includes('grade');

  // Calculate totals
  let totalMax = 0;
  let totalObtained = 0;
  let hasNumericMarks = false;

  marks.forEach((m) => {
    const max = parseFloat(m.total);
    const obt = parseFloat(m.obtained);
    if (!isNaN(max) && !isNaN(obt)) {
      totalMax += max;
      totalObtained += obt;
      hasNumericMarks = true;
    }
  });

  const percentage = totalMax > 0 ? ((totalObtained / totalMax) * 100).toFixed(1) : null;

  return (
    <div className="card marks-card">
      <div className="subject-header">
        {name}
        {percentage && (
          <span
            style={{
              float: 'right',
              fontSize: '0.85rem',
              fontWeight: 500,
              color:
                parseFloat(percentage) >= 75
                  ? 'var(--success)'
                  : parseFloat(percentage) >= 50
                    ? 'var(--warning)'
                    : 'var(--danger)',
            }}
          >
            {percentage}%
          </span>
        )}
      </div>

      {isGradeOnly ? (
        <div style={{ textAlign: 'center', padding: '12px 0' }}>
          <span className="grade-badge">{marks[0].obtained}</span>
        </div>
      ) : (
        <table className="marks-table">
          <thead>
            <tr>
              <th>Component</th>
              <th>Total</th>
              <th>Obtained</th>
            </tr>
          </thead>
          <tbody>
            {marks.map((m, i) => (
              <tr key={i}>
                <td>{m.element}</td>
                <td>{m.total}</td>
                <td>{m.obtained}</td>
              </tr>
            ))}
            {hasNumericMarks && (
              <tr className="marks-total-row">
                <td>Total</td>
                <td>{totalMax}</td>
                <td>{totalObtained}</td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}
