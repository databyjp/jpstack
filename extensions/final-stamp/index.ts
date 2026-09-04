import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import type { Component } from "@earendil-works/pi-tui";

const ENTRY_TYPE = "final-stamp";
const MONTHS = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
] as const;

interface TimestampEntryData {
  version: 1;
  role: "user" | "assistant";
  timestamp: number;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isValidTimestamp(value: unknown): value is number {
  return (
    typeof value === "number" &&
    Number.isFinite(value) &&
    !Number.isNaN(new Date(value).getTime())
  );
}

function isTimestampEntryData(value: unknown): value is TimestampEntryData {
  return (
    isRecord(value) &&
    value.version === 1 &&
    (value.role === "user" || value.role === "assistant") &&
    isValidTimestamp(value.timestamp)
  );
}

function formatTimestamp(timestamp: number): string {
  const date = new Date(timestamp);
  const pad = (value: number) => String(value).padStart(2, "0");

  return `${date.getFullYear()}-${MONTHS[date.getMonth()]}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function rightAlignedTimestamp(
  text: string,
  style: (value: string) => string,
): Component {
  return {
    render(width) {
      if (width < 1) return [];
      const visibleText =
        text.length > width ? text.slice(text.length - width) : text;
      return [`${" ".repeat(width - visibleText.length)}${style(visibleText)}`];
    },
    invalidate() {},
  };
}

function isFinalVisibleAssistantMessage(message: unknown): boolean {
  if (
    !isRecord(message) ||
    message.role !== "assistant" ||
    !Array.isArray(message.content)
  ) {
    return false;
  }

  let hasVisibleText = false;
  for (const part of message.content) {
    if (!isRecord(part)) continue;
    if (part.type === "toolCall") return false;
    if (
      part.type === "text" &&
      typeof part.text === "string" &&
      part.text.trim()
    ) {
      hasVisibleText = true;
    }
  }
  return hasVisibleText;
}

export default function finalStampExtension(pi: ExtensionAPI): void {
  pi.registerEntryRenderer<TimestampEntryData>(
    ENTRY_TYPE,
    (entry, _options, theme) => {
      if (!isTimestampEntryData(entry.data)) return undefined;
      return rightAlignedTimestamp(
        formatTimestamp(entry.data.timestamp),
        (text) => theme.fg("dim", text),
      );
    },
  );

  let tuiSessionActive = false;
  const pendingUserTimestamps: number[] = [];

  const appendTimestamp = (
    role: TimestampEntryData["role"],
    timestamp: number,
  ): void => {
    if (!tuiSessionActive || !isValidTimestamp(timestamp)) return;
    pi.appendEntry<TimestampEntryData>(ENTRY_TYPE, {
      version: 1,
      role,
      timestamp,
    });
  };

  // Delay user entries until the next message starts so each custom entry follows
  // the user message in session and transcript order.
  const flushPendingUsers = (): void => {
    while (tuiSessionActive && pendingUserTimestamps.length > 0) {
      const timestamp = pendingUserTimestamps.shift();
      if (timestamp !== undefined) appendTimestamp("user", timestamp);
    }
  };

  pi.on("session_start", (_event, ctx) => {
    pendingUserTimestamps.length = 0;
    tuiSessionActive = ctx.mode === "tui";
  });

  pi.on("message_start", () => {
    flushPendingUsers();
  });

  pi.on("message_end", (event) => {
    if (
      tuiSessionActive &&
      event.message.role === "user" &&
      isValidTimestamp(event.message.timestamp)
    ) {
      pendingUserTimestamps.push(event.message.timestamp);
    }
  });

  pi.on("turn_end", (event) => {
    if (isFinalVisibleAssistantMessage(event.message)) {
      appendTimestamp("assistant", event.message.timestamp);
    }
  });

  pi.on("agent_end", () => {
    flushPendingUsers();
  });

  pi.on("session_shutdown", () => {
    flushPendingUsers();
    pendingUserTimestamps.length = 0;
    tuiSessionActive = false;
  });
}
