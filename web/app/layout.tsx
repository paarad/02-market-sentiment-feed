import type { ReactNode } from "react";

export const metadata = {
	title: "Market Sentiment Feed",
	description: "Crypto-first market sentiment with ISR LLM analysis",
	icons: {
		icon: '/favicon.ico',
	},
};

export default function RootLayout({ children }: { children: ReactNode }) {
	return (
		<html lang="en">
			<body style={{ fontFamily: "ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu", background: "#0b0f14", color: "#e5e7eb", margin: 0 }}>
				<div style={{ maxWidth: 980, margin: "0 auto", padding: 20 }}>
					{children}
				</div>
			</body>
		</html>
	);
} 