type Props = { values: number[]; color?: string };

export default function Sparkline({ values, color = "#22c55e" }: Props) {
	const data = (values && values.length ? values : Array.from({ length: 24 }, (_, i) => 0.5 + 0.4 * Math.sin(i / 3)))
		.map(v => Math.max(0, Math.min(1, v)));
	const w = 600;
	const h = 80;
	const pad = 8;
	const step = (w - pad * 2) / Math.max(1, data.length - 1);
	const points = data.map((v, i) => {
		const x = pad + i * step;
		const y = pad + (1 - v) * (h - pad * 2);
		return `${x},${y}`;
	}).join(" ");
	return (
		<svg width={w} height={h} style={{ display: "block", background: "#0f172a", border: "1px solid #1f2937", borderRadius: 8 }}>
			<polyline fill="none" stroke={color} strokeWidth="2" points={points} />
		</svg>
	);
} 