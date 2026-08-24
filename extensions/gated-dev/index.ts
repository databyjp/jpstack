import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";

type Mode = "off" | "locked" | "approved";

const BLOCKED_WHILE_LOCKED = new Set(["bash", "edit", "write"]);

export default function gatedDevelopment(pi: ExtensionAPI): void {
	let mode: Mode = "off";
	let approvedSlice = "";

	function statusText(): string {
		if (mode === "locked") return "design locked";
		if (mode === "approved") return `approved: ${approvedSlice}`;
		return "off";
	}

	function updateStatus(ctx: ExtensionContext): void {
		const status = mode === "off" ? undefined : `gated-dev: ${statusText()}`;
		ctx.ui.setStatus("gated-dev", status);
	}

	function showStatus(ctx: ExtensionContext): void {
		ctx.ui.notify(`Gated development is ${statusText()}.`, "info");
	}

	pi.registerCommand("gated-dev", {
		description: "Control gated development: start, approve <slice>, status, or off",
		handler: async (args, ctx) => {
			const input = args.trim();
			const [action = "status", ...rest] = input.split(/\s+/);

			if (action === "start") {
				mode = "locked";
				approvedSlice = "";
			} else if (action === "approve") {
				if (mode !== "locked") {
					ctx.ui.notify("Start gated development before approving a slice.", "warning");
					return;
				}

				approvedSlice = rest.join(" ").trim();
				if (!approvedSlice) {
					ctx.ui.notify("Describe the slice to approve.", "warning");
					return;
				}
				mode = "approved";
			} else if (action === "off") {
				mode = "off";
				approvedSlice = "";
			} else if (action !== "status") {
				ctx.ui.notify("Usage: /gated-dev start | approve <slice> | status | off", "warning");
				return;
			}

			updateStatus(ctx);
			showStatus(ctx);
		},
	});

	pi.on("tool_call", event => {
		if (mode !== "locked" || !BLOCKED_WHILE_LOCKED.has(event.toolName)) return;

		return {
			block: true,
			reason: "The design gate is locked. Obtain human approval with /gated-dev approve <slice>.",
		};
	});

	pi.on("before_agent_start", () => {
		if (mode === "locked") {
			return {
				message: {
					customType: "gated-development",
					content:
						"The design gate is active. Investigate with read-only tools. " +
						"Present the gated-development change brief and stop. Do not implement.",
					display: false,
				},
			};
		}

		if (mode === "approved") {
			return {
				message: {
					customType: "gated-development",
					content:
						`Implement only this approved vertical slice: ${approvedSlice}\n` +
						"Validate it, report its scope, and stop. Do not start another slice.",
					display: false,
				},
			};
		}
	});

	pi.on("agent_settled", (_event, ctx) => {
		if (mode !== "approved") return;

		mode = "locked";
		approvedSlice = "";
		updateStatus(ctx);
		ctx.ui.notify("Slice complete. The design gate is locked again.", "info");
	});
}
