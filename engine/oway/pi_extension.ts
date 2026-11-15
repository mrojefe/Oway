// Oway builder stop hook for pi (written by `oway install-hook --host pi`).
// At agent_before_settle it runs `oway stop-hook --format plain`. Exit 2 means
// an item of the active slice is still OPEN or FAIL: the reason is added for
// the model and one more turn is requested. The Oway hook itself lets a stuck
// worker go after a few idle blocks, so this cannot loop forever.
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const OWAY = "__OWAY_ENTRY__";

export default function (pi: ExtensionAPI) {
  pi.on("agent_before_settle", async (event: any, ctx: any) => {
    const result = await pi.exec("python3", [OWAY, "stop-hook", "--format", "plain"], {
      cwd: ctx?.cwd ?? process.cwd(),
      timeout: 60000,
    });
    if (result.code !== 2) return;
    return {
      entries: [
        ...event.entries,
        { type: "custom_message", customType: "oway-stop", content: result.stderr.trim(), display: true },
      ],
      continue: true,
    };
  });
}
