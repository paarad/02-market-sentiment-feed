type Driver = { title: string; url: string; source?: string; weight?: number };

export default function DriversList({ title, items, accent }: { title: string; items: Driver[]; accent: string }) {
	return (
		<div>
			<h3 style={{ margin: "6px 0 10px", fontSize: 16 }}>{title}</h3>
			<div style={{ display: "grid", gap: 8 }}>
				{(items || []).map((d, i) => (
					<a key={i} href={d.url} target="_blank" rel="noopener noreferrer" style={{ textDecoration: "none", color: "inherit" }}>
						<div style={{ padding: 10, background: "#0f172a", border: "1px solid #1f2937", borderRadius: 8 }}>
							<div style={{ display: "flex", alignItems: "center", gap: 10 }}>
								<span style={{ display: "inline-block", width: 6, height: 6, borderRadius: 999, background: accent }} />
								<span style={{ flex: 1 }}>{d.title}</span>
								{d.source && (
									<span style={{ fontSize: 11, background: "#1f2937", color: "#cbd5e1", padding: "2px 6px", borderRadius: 6 }}>{d.source}</span>
								)}
							</div>
						</div>
					</a>
				))}
				{(!items || items.length === 0) && (
					<div style={{ opacity: 0.7, fontSize: 12 }}>No items</div>
				)}
			</div>
		</div>
	);
} 