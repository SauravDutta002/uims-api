export default function ProfileCard({ profile, uid }) {
  const initials = profile?.name
    ? profile.name
        .split(' ')
        .map((w) => w[0])
        .join('')
        .slice(0, 2)
        .toUpperCase()
    : '?';

  return (
    <div className="card profile-card fade-in">
      <div className="profile-avatar">{initials}</div>
      <div className="profile-info">
        <h2>{profile?.name || 'Student'}</h2>
        <div className="uid">{uid}</div>
        <div className="program">Chandigarh University</div>
      </div>
    </div>
  );
}
