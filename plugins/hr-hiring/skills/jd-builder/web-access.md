# Reaching the web

Research needs two things: search results, and the ability to open and read the pages behind them. Try these in order and use the first that works. Move on automatically, without asking, unless a step below says to ask.

| # | Route | How | When it is enough |
|---|---|---|---|
| 1 | Claude's web tools | `WebSearch` to find pages, `WebFetch` to read them (load them with ToolSearch if they are listed as deferred) | Normal case in the Claude desktop app, Cowork and Claude Code |
| 2 | Claude's built-in browser | The browser pane tools (`mcp__Claude_Browser__*`, or `mcp__remote-devices__Claude_Browser__*`); load the `anthropic-skills:built-in-browser` skill first | When `WebFetch` can't open a page but a browser can (sites that block plain fetches, pages that need JavaScript) |
| 3 | Claude in Chrome | The `mcp__claude-in-chrome__*` tools; load the `anthropic-skills:chrome-browser` skill first. Work in a new tab and never touch the user's open tabs | When the built-in browser isn't available |
| 4 | The local terminal | `curl -sL <url>` (or `Invoke-WebRequest` on Windows) through Bash, then read the saved HTML | When the browser tools aren't available but the computer can reach the site |
| 5 | Ask the user | One short message: "To research this role I need to open web pages. May I use your browser?" Then turn on the browser or Chrome tool they allow (for example via `enable__mcp__claude-in-chrome` or `enable__mcp__remote-devices__Claude_Browser`) and continue from route 2 or 3 | When routes 1–4 all fail, or a route needs permission the session doesn't have |

Rules:
- Search snippets alone are never enough: open a page before citing it, whatever the route.
- If search works but one site refuses every route, skip that site and use another source.
- Record the route used for each source (`"via": "webfetch|browser|chrome|terminal"`) in the research file.
- Stop only if every route fails after the user has said yes or no to route 5. Tell them in one plain sentence what happened and that you'll continue as soon as the web can be reached. Never write a JD from memory.
- The user never has to set anything up by hand. If a permission prompt appears, tell them in one line to click **Allow**.
