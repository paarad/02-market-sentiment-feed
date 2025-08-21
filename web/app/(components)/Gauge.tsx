type Props = { label: string; value: number };

export default function Gauge({ label, value }: Props) {
	const pct = Math.round(Math.max(0, Math.min(1, value)) * 100);
	return (
		<div style={{ minWidth: 180, background: "#0f172a", border: "1px solid #1f2937", borderRadius: 8, padding: 12 }}>
			<div style={{ fontSize: 12, opacity: 0.8 }}>{label}</div>
			<div style={{ height: 10, background: "#1f2937", borderRadius: 999, overflow: "hidden", marginTop: 8 }}>
				<div style={{ width: `${pct}%`, height: "100%", background: "linear-gradient(90deg,#ef4444,#f59e0b,#22c55e)", transition: "width .5s" }} />
			</div>
			<div style={{ fontSize: 12, marginTop: 6 }}>{pct}%</div>
		</div>
	);
} 