# Privacy policy

`txt2md` is a local Windows desktop tool. This policy explains what data the program
handles.

## What the program does with your data

- The program watches the `.txt` files you explicitly add to its watch list, and sends
  the **text content of those files** to an AI service to reformat them into Markdown.
- The AI service is the **API endpoint you configure yourself** in Settings
  (default: `https://api.deepseek.com`), authenticated with **your own API key**.
  Nothing is sent anywhere unless you configure an endpoint and add files to watch.
- No data is sent to the project maintainers. There is no telemetry, no analytics,
  and no tracking.

## Data stored locally

- `config.json` (next to the program, or in `%APPDATA%\txt2md\`): your settings,
  including your API key in plain text. Keep this file private.
- `sync.log`: a local log of program activity. It never leaves your machine.
- Generated `.md` and backup `.md.bak` files next to each watched `.txt`.

## Third parties

When the program sends file content to your configured AI API endpoint, that provider's
privacy policy applies. For the default provider, see
<https://platform.deepseek.com/> (DeepSeek privacy policy).

## Summary statement

This program will not transfer any information to other networked systems unless
specifically requested by the user or the person installing or operating it.

## Uninstall

This is a portable program. To uninstall, delete the program folder (or `txt2md.exe`).
If settings were stored in `%APPDATA%\txt2md\`, delete that folder too.

## Contact

Open an issue at <https://github.com/duruoxian/txt2md/issues>.
