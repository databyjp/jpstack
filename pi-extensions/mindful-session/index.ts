import type {
	ExtensionAPI,
	ExtensionContext,
} from "@earendil-works/pi-coding-agent";
import { matchesKey, Text } from "@earendil-works/pi-tui";

const ENTRY_TYPE = "mindful-session";
const WIDGET_ID = "mindful-session-intention";

interface SessionNote {
	text: string;
	createdAt: string;
}

type MindfulEntryData =
	| { kind: "set-intention"; text: string | null }
	| { kind: "add-note"; note: SessionNote };

export default function mindfulSessionExtension(pi: ExtensionAPI): void {
	let intention: string | undefined;
	let notes: SessionNote[] = [];

	function updateUi(ctx: ExtensionContext): void {
		if (!ctx.hasUI) return;
		ctx.ui.setWidget(WIDGET_ID, [
			intention
				? `📝 Session Intent: ${intention}`
				: "📝 Session Intent: not set - use /intention",
		]);
		ctx.ui.setStatus(
			ENTRY_TYPE,
			`[${notes.length} ${notes.length === 1 ? "note" : "notes"}]`,
		);
	}

	function restoreState(ctx: ExtensionContext): void {
		intention = undefined;
		notes = [];
		for (const entry of ctx.sessionManager.getEntries()) {
			if (entry.type !== "custom" || entry.customType !== ENTRY_TYPE) continue;
			const data = entry.data as MindfulEntryData | undefined;
			if (data?.kind === "set-intention") {
				intention = data.text?.trim() || undefined;
			} else if (data?.kind === "add-note") {
				notes.push(data.note);
			}
		}
	}

	pi.on("session_start", (_event, ctx) => {
		restoreState(ctx);
		updateUi(ctx);
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
			} satisfies MindfulEntryData);
			updateUi(ctx);
			ctx.ui.notify(intention ? "Intention updated" : "Intention cleared", "info");
		},
	});

	pi.registerCommand("note", {
		description: "Add a private note to this session",
		handler: async (args, ctx) => {
			let text = args.trim();
			if (!text) {
				if (ctx.mode !== "tui") {
					ctx.ui.notify("Use /note <text> outside interactive mode", "error");
					return;
				}
				const response = await ctx.ui.editor("Add session note", "");
				if (response === undefined) return;
				text = response.trim();
			}
			if (!text) return;

			const note = {
				text,
				createdAt: new Date().toISOString(),
			} satisfies SessionNote;
			notes.push(note);
			pi.appendEntry(ENTRY_TYPE, {
				kind: "add-note",
				note,
			} satisfies MindfulEntryData);
			updateUi(ctx);
			ctx.ui.notify("Session note added", "info");
		},
	});

	pi.registerCommand("notes", {
		description: "Show private notes for this session",
		handler: async (_args, ctx) => {
			if (notes.length === 0) {
				ctx.ui.notify("No session notes", "info");
				return;
			}

			const content = notes
				.map((note, index) => `${index + 1}. ${note.text}`)
				.join("\n\n");
			if (ctx.mode !== "tui") {
				ctx.ui.notify(content, "info");
				return;
			}

			await ctx.ui.custom<void>((_tui, _theme, _keybindings, done) => {
				const text = new Text(
					`Session notes\n\n${content}\n\nPress Escape to close`,
					1,
					1,
				);
				return {
					render: (width) => text.render(width),
					handleInput: (data) => {
						if (matchesKey(data, "escape") || matchesKey(data, "ctrl+c")) done();
					},
					invalidate: () => text.invalidate(),
				};
			});
			updateUi(ctx);
		},
	});
}
