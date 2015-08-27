# config.json reference
This file documents `config.json`, the LaserQueue configuration file.

## Notes
- `config.json` is a standard JSON key/value store
- The config is generated from `defaultconf.json` when the queue first runs. Running the queue again with the `-r` flag will regenerate it.
- Both the frontend and backend rely on and can access values in `config.json`. The backend can change these values.
- The file is stored in the `www` directory so that the frontend can access it

## Keys and values

### `action_header`: `string`
Text for table header above action buttons.
#### Default: `"Action"`
#### Examples
- "Action"
- "Buttons"

---

### `admin_mode_enabled`: `boolean`
`true` enables admin mode.
#### Default: `true`
---
