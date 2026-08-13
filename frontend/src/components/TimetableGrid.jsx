export default function TimetableGrid({ timetable }) {
  if (!timetable || !timetable.schedule) {
    return (
      <div className="empty-state">
        <div className="icon">📅</div>
        <p>Timetable not available for this session yet.</p>
      </div>
    );
  }

  const { schedule, days } = timetable;
  const dayList = days || Object.keys(schedule);

  // Collect all unique time slots across all days
  const timeSlots = new Set();
  dayList.forEach((day) => {
    if (schedule[day]) {
      Object.keys(schedule[day]).forEach((slot) => timeSlots.add(slot));
    }
  });

  const sortedSlots = Array.from(timeSlots);

  if (sortedSlots.length === 0) {
    return (
      <div className="empty-state">
        <div className="icon">📅</div>
        <p>Timetable data is empty.</p>
      </div>
    );
  }

  return (
    <div className="timetable-wrapper">
      <table className="timetable">
        <thead>
          <tr>
            <th>Time</th>
            {dayList.map((day) => (
              <th key={day}>{day}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedSlots.map((slot) => (
            <tr key={slot}>
              <td>{slot}</td>
              {dayList.map((day) => {
                const cellValue = schedule[day]?.[slot];
                return (
                  <td
                    key={day}
                    className={cellValue ? 'has-class' : ''}
                    title={cellValue || ''}
                  >
                    {cellValue
                      ? cellValue.length > 15
                        ? cellValue.slice(0, 15) + '...'
                        : cellValue
                      : '—'}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
