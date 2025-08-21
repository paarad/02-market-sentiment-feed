import { NextResponse } from "next/server";

export const revalidate = 43200; // 12 hours
// export const revalidate = 14400; // 4 hours

function clamp(n: number, lo = 0, hi = 1) {
	return Math.max(lo, Math.min(hi, n));
}

function formatPct(n: number) {
	return Math.round(n * 100);
}

async function fetchFeed(): Promise<any | null> {
	const url = process.env.NEXT_PUBLIC_FEED_URL as string;
	if (!url) return null;
	try {
		const res = await fetch(url, { cache: "no-store" });
		if (!res.ok) return null;
		return await res.json();
	} catch {
		return null;
	}
}

async function generateAnalysis(feed: any): Promise<string> {
	const key = process.env.OPENAI_API_KEY;
	const updatedAt = feed?.updated_at ?? null;
	const s = feed?.summary ?? {};
	const combined = typeof s?.combined_sentiment === "number" ? s.combined_sentiment : 0.5;
	const crypto = typeof s?.crypto_sentiment === "number" ? s.crypto_sentiment : 0.5;
	const global = typeof s?.global_sentiment === "number" ? s.global_sentiment : 0.5;
	const conf = typeof s?.confidence === "number" ? s.confidence : 0.0;

	const driversPos = feed?.drivers?.positive ?? [];
	const driversNeg = feed?.drivers?.negative ?? [];

	const fallback = `Combined ${formatPct(combined)}%, crypto ${formatPct(crypto)}%, global ${formatPct(global)}% (confidence ${formatPct(conf)}%). Pos drivers: ${driversPos.slice(0,3).map((d:any)=>d.title).join("; ")}. Neg drivers: ${driversNeg.slice(0,3).map((d:any)=>d.title).join("; ")}.`;

	console.log("OpenAI key present:", !!key);
	if (!key) return fallback;

	const prompt = `You are a crypto markets analyst writing for a professional audience. Analyze this market sentiment data and provide insights in 2-3 sentences. Be conversational and insightful, not just reporting numbers. Focus on what the sentiment means for traders and investors.

Data: ${JSON.stringify(feed).slice(0, 15000)}`;

	try {
		console.log("Calling OpenAI...");
		const { OpenAI } = await import("openai/index.mjs");
		const openai = new OpenAI({ apiKey: key });
		const resp = await openai.chat.completions.create({
			model: "gpt-4o-mini",
			messages: [
				{ role: "system", content: "You are a witty, insightful crypto analyst who provides valuable market commentary. Be engaging and provide actionable insights." },
				{ role: "user", content: prompt },
			],
			max_tokens: 180,
			temperature: 0.7,
		});
		const result = resp.choices?.[0]?.message?.content?.trim() || fallback;
		console.log("OpenAI response received:", result.substring(0, 100) + "...");
		return result;
	} catch (error) {
		console.log("OpenAI error:", error);
		return fallback;
	}
}

export async function GET() {
	const feed = await fetchFeed();
	const updatedAt = feed?.updated_at ?? null;
	const now = new Date();
	let stale = false;
	if (updatedAt) {
		const ts = new Date(updatedAt);
		const hours = (now.getTime() - ts.getTime()) / 3600000;
		stale = hours > 30; // consider stale if > ~30h for 12h cadence
	}

	const analysis = feed ? await generateAnalysis(feed) : "Feed unavailable; using last cached analysis if present.";

	const body = {
		analysis,
		updated_at: updatedAt,
		stale,
		summary: feed?.summary ?? null,
		drivers: feed?.drivers ?? { positive: [], negative: [] },
		history: feed?.history ?? [],
	};

	const res = NextResponse.json(body);
	res.headers.set("Cache-Control", "s-maxage=43200, stale-while-revalidate=600");
	return res;
} 