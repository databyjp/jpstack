import type {
	ExtensionAPI,
	ExtensionContext,
} from "@earendil-works/pi-coding-agent";

const ENTRY_TYPE = "mindful-session";
const WIDGET_ID = "mindful-session-intention";

interface IntentionEntryData {
	kind: "set-intention";
	text: string | null;
}

export default function mindfulSessionExtension(pi: ExtensionAPI): void {
	let intention: string | undefined;

	function renderIntention(ctx: ExtensionContext): void {
		if (!ctx.hasUI) return;
		ctx.ui.setWidget(WIDGET_ID, [
			intention
				? `Intention: ${intention}`
				: "Intention: not set - use /intention",
		]);
	}

	function restoreIntention(ctx: ExtensionContext): void {
		intention = undefined;
		for (const entry of ctx.sessionManager.getEntries()) {
			if (entry.type !== "custom" || entry.customType !== ENTRY_TYPE) continue;
			const data = entry.data as IntentionEntryData | undefined;
			if (data?.kind !== "set-intention") continue;
			intention = data.text?.trim() || undefined;
		}
	}

	pi.on("session_start", (_event, ctx) => {
		restoreIntention(ctx);
		renderIntention(ctx);
	});

	pi.registerCommand("intention", {
		description: "Set the intention for this session",
		handler: async (args, ctx) => {
			let nextIntention = args.trim();

			if (!nextIntention) {
				if (!ctx.hasUI) return;
				const response = await ctx.ui.input(
					"Set session intention",
					intention ?? "What are you trying to achieve?",
				);
				if (response === undefined) return;
				nextIntention = response.trim();
			}

			intention = nextIntention || undefined;
			pi.appendEntry(ENTRY_TYPE, {
				kind: "set-intention",
				text: intention ?? null,
			} satisfies IntentionEntryData);
			renderIntention(ctx);
			ctx.ui.notify(intention ? "Intention updated" : "Intention cleared", "info");
		},
	});
}
