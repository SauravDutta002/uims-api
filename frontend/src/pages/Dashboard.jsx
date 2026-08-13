import { useState } from 'react';
import ProfileCard from '../components/ProfileCard';
import AttendanceCard from '../components/AttendanceCard';
import MarksCard from '../components/MarksCard';
import TimetableGrid from '../components/TimetableGrid';

export default function Dashboard({ data, uid, onLogout }) {
  const { profile, attendance, marks, timetable } = data;

  // Marks tab state
  const [activeSession, setActiveSession] = useState(() => {
    const current = marks?.sessions?.find((s) => s.isCurrent);
    // Default to session with marks data, fallback to current
    const sessionsWithData = marks?.sessions?.filter(
      (s) => marks.data[s.value]?.length > 0
    );
    return sessionsWithData?.[0]?.value || current?.value || marks?.sessions?.[0]?.value || '';
  });

  const attendanceSubjects = attendance?.subjects || [];
  const currentMarks = marks?.data?.[activeSession] || [];

  return (
    <div className="dashboard">
      {/* Top Bar */}
      <header className="topbar">
        <div className="topbar-left">
          <span className="topbar-logo">CUIMS Dashboard</span>
          <span className="topbar-divider" />
          <span className="topbar-name">{profile?.name || uid}</span>
        </div>
        <button className="logout-btn" onClick={onLogout}>
          Logout
        </button>
      </header>

      <main className="dashboard-content">
        {/* Profile Section */}
        <section className="section">
          <ProfileCard profile={profile} uid={uid} />
        </section>

        {/* Attendance Section */}
        <section className="section">
          <div className="section-header">
            <span className="section-icon">📊</span>
            <h2 className="section-title">Attendance</h2>
            <span className="section-badge">
              {attendanceSubjects.length} subjects
            </span>
          </div>

          {attendanceSubjects.length > 0 ? (
            <div className="grid-cards">
              {attendanceSubjects.map((subj, i) => (
                <AttendanceCard
                  key={subj.EncryptCode || i}
                  subject={subj}
                  index={i}
                />
              ))}
            </div>
          ) : (
            <div className="card">
              <div className="empty-state">
                <div className="icon">📊</div>
                <p>No attendance data available for this session yet.</p>
              </div>
            </div>
          )}
        </section>

        {/* Marks Section */}
        <section className="section">
          <div className="section-header">
            <span className="section-icon">📝</span>
            <h2 className="section-title">Marks</h2>
          </div>

          {/* Session Tabs */}
          {marks?.sessions?.length > 0 && (
            <div className="marks-tabs">
              {marks.sessions.map((sess) => (
                <button
                  key={sess.value}
                  className={`marks-tab ${activeSession === sess.value ? 'active' : ''}`}
                  onClick={() => setActiveSession(sess.value)}
                >
                  {sess.name}
                  {sess.isCurrent && ' ●'}
                </button>
              ))}
            </div>
          )}

          {/* Marks Cards */}
          {currentMarks.length > 0 ? (
            currentMarks.map((subj, i) => (
              <MarksCard key={`${activeSession}-${i}`} subject={subj} />
            ))
          ) : (
            <div className="card">
              <div className="empty-state">
                <div className="icon">📝</div>
                <p>No marks data available for this session.</p>
              </div>
            </div>
          )}
        </section>

        {/* Timetable Section */}
        <section className="section">
          <div className="section-header">
            <span className="section-icon">📅</span>
            <h2 className="section-title">Timetable</h2>
          </div>
          <div className="card" style={{ padding: '20px' }}>
            <TimetableGrid timetable={timetable} />
          </div>
        </section>
      </main>
    </div>
  );
}
