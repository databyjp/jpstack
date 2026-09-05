import type {
	ExtensionAPI,
	ExtensionContext,
} from "@earendil-works/pi-coding-agent";
import { matchesKey, Text, visibleWidth } from "@earendil-works/pi-tui";

const ENTRY_TYPE = "mindful-session";
const WIDGET_ID = "mindful-session-intention";

interface SessionNote {
	text: string;
	createdAt: string;
}

type MindfulEntryData =
	| { kind: "set-intention"; text: string | null }
	| { kind: "add-note"; note: SessionNote }
	| { kind: "edit-note"; index: number; text: string }
	| { kind: "delete-note"; index: number };

function parseNoteIndex(args: string): number | undefined {
	const noteNumber = args.trim();
	if (!/^[1-9]\d*$/.test(noteNumber)) return undefined;
	return Number(noteNumber) - 1;
}

export default function mindfulSessionExtension(pi: ExtensionAPI): void {
	let intention: string | undefined;
	let notes: SessionNote[] = [];

	function updateUi(ctx: ExtensionContext): void {
		if (!ctx.hasUI) return;
		const count = `[${notes.length} ${notes.length === 1 ? "note" : "notes"}]`;
		const intent = intention ?? "not set - use /intention";
		ctx.ui.setStatus(ENTRY_TYPE, undefined);
		const label = `${count} 📝 Session Intent:`;
		ctx.ui.setWidget(WIDGET_ID, [
			`${ctx.mode === "tui" ? ctx.ui.theme.fg("success", label) : label} ${intent}`,
		]);
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
			} else if (data?.kind === "edit-note" && notes[data.index]) {
				notes[data.index] = { ...notes[data.index], text: data.text };
			} else if (data?.kind === "delete-note" && notes[data.index]) {
				notes.splice(data.index, 1);
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

	pi.registerCommand("notes-add", {
		description: "Add a private note to this session",
		handler: async (args, ctx) => {
			let text = args.trim();
			if (!text) {
				if (ctx.mode !== "tui") {
					ctx.ui.notify("Use /notes-add <text> outside interactive mode", "error");
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

	pi.registerCommand("notes-edit", {
		description: "Edit a private session note by number",
		handler: async (args, ctx) => {
			const index = parseNoteIndex(args);
			const note = index === undefined ? undefined : notes[index];
			if (!note) {
				ctx.ui.notify("Use /notes-edit <note-number> from /notes-show", "error");
				return;
			}
			if (ctx.mode !== "tui") {
				ctx.ui.notify("Editing notes requires interactive mode", "error");
				return;
			}

			const response = await ctx.ui.editor(
				`Edit session note ${index + 1}`,
				note.text,
			);
			if (response === undefined) return;
			const text = response.trim();
			if (!text) {
				ctx.ui.notify("A note cannot be empty; use /notes-delete instead", "error");
				return;
			}

			notes[index] = { ...note, text };
			pi.appendEntry(ENTRY_TYPE, {
				kind: "edit-note",
				index,
				text,
			} satisfies MindfulEntryData);
			updateUi(ctx);
			ctx.ui.notify(`Session note ${index + 1} updated`, "info");
		},
	});

	pi.registerCommand("notes-delete", {
		description: "Delete a private session note by number",
		handler: async (args, ctx) => {
			const index = parseNoteIndex(args);
			const note = index === undefined ? undefined : notes[index];
			if (!note) {
				ctx.ui.notify("Use /notes-delete <note-number> from /notes-show", "error");
				return;
			}
			if (!ctx.hasUI) return;

			const confirmed = await ctx.ui.confirm(
				`Delete session note ${index + 1}?`,
				note.text,
			);
			if (!confirmed) return;
			notes.splice(index, 1);
			pi.appendEntry(ENTRY_TYPE, {
				kind: "delete-note",
				index,
			} satisfies MindfulEntryData);
			updateUi(ctx);
			ctx.ui.notify(`Session note ${index + 1} deleted`, "info");
		},
	});

	pi.registerCommand("notes-show", {
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

			await ctx.ui.custom<void>(
				(_tui, theme, _keybindings, done) => {
					const body = new Text(
						`Session notes\n\n${content}\n\nPress Escape to close`,
						1,
						1,
					);
					const border = (value: string) => theme.fg("borderMuted", value);
					return {
						render: (width) => {
							if (width < 2) return body.render(width);
							const innerWidth = width - 2;
							const horizontal = "─".repeat(innerWidth);
							const bodyLines = body.render(innerWidth).map((line) => {
								const padding = " ".repeat(
									Math.max(0, innerWidth - visibleWidth(line)),
								);
								return `${border("│")}${line}${padding}${border("│")}`;
							});
							return [
								border(`┌${horizontal}┐`),
								...bodyLines,
								border(`└${horizontal}┘`),
							];
						},
						handleInput: (data) => {
							if (matchesKey(data, "escape") || matchesKey(data, "ctrl+c")) done();
						},
						invalidate: () => body.invalidate(),
					};
				},
				{
					overlay: true,
					overlayOptions: {
						anchor: "left-center",
						offsetX: 2,
						width: "45%",
						minWidth: 40,
						maxHeight: "80%",
					},
				},
			);
		},
	});
}
