export default function StatusBadge({ value = 'UNKNOWN' }) { return <span className={`status status-${value.toLowerCase()}`}>{value}</span>; }
