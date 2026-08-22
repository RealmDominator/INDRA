export default function StatusBadge({ value = 'UNKNOWN', className = '' }) {
  if (!value && value !== 0) {
    return <span className={`status status-unavailable ${className}`}>UNAVAILABLE</span>;
  }

  const strVal = String(value).toUpperCase();
  const normalizedClass = strVal.toLowerCase().replace(/[^a-z0-9_-]/g, '_');

  return (
    <span className={`status status-${normalizedClass} ${className}`}>
      {strVal}
    </span>
  );
}
