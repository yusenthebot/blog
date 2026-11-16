# Development branch audit — 2026-11-16

Compared all existing local and fetched remote branches with `main`, checking both commit ancestry and the current implementation.

| Branch / commit | Feature | Resolution |
| --- | --- | --- |
| `wip/home-discovery` / `29abac2` | Home search, series filters, reading guide, tag links, related posts | Already merged through `42f0838` |
| `blog/center-article-layout` / `82f728a` | Centred article and right contents rail | Already on main |
| `dec7d14` | Contents reading cursor and page transition | Already on main |
| `abbb87f` | Pixel reading progress | Restored in `91ae2ad` |
| `8f61597` | X, LinkedIn, Email and Copy URL | Restored in `91ae2ad` |
| `46ce9e1` | Full-screen figure viewer for EP10 and MacMimic | Restored with this audit; fixed hidden-image CSS and keyboard focus at zoom limits |

No other feature commits were found outside main. The old branch still has three commits absent from main's ancestry because their functionality was ported into the current layout rather than merging the old template wholesale. Do not infer missing features from `git cherry` alone.

For future releases, compare outstanding branch commits by feature, then check the built pages. Keep the existing scope of opt-in features unless an expansion is requested.

Follow-up: the user requested the viewer on every article and every body image. The two-post allowlist has now been replaced by automatic original-image mapping, including all six images in `agentic-robot-next-half`.
