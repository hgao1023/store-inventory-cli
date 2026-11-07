# products.py — Store Inventory CLI

A command-line tool for a small store's product inventory.
Products are saved in a local JSON file; each command does one thing and exits.

- Python 3, standard library only — nothing to install
- Entry point: `products.py`

## Usage

```
python3 products.py [--file PATH] COMMAND [OPTIONS]
```

`--file PATH` picks the data file (default: `products.json` in the current folder).
It must come **before** the command. Every command also supports `--help`.

| Command | What it does |
|---|---|
| `add --name NAME --price PRICE --quantity QTY` | Create a product and print it |
| `list` | Print all products sorted by ID (`[]` when empty) |
| `get ID` | Print one product |
| `update ID [--name NAME] [--price PRICE] [--quantity QTY]` | Change only the supplied fields (at least one is required) |
| `delete ID --yes` | Remove a product and print `{"deleted_id": ID}` |
| `search --name TEXT` | **Custom feature** — find products by part of their name |

Field rules:

- **name** — at least one non-space character; leading and trailing spaces are trimmed
- **price** — digits with up to two decimal places, such as `0`, `4.5` or `4.50`; always stored as a string like `"4.50"`
- **quantity** — a whole number, 0 or greater
- **ID** — assigned automatically, starting at 1; a deleted ID is never reused

## Custom feature: `search`

### Who it helps and why

This feature is for the people working at the store counter.

When a customer asks "Do you still have those spiral notebooks?", the staff member
usually doesn't know the product's ID, and may not remember its exact name or
spelling. With only the basic commands, they would have to run `list` and read
through every product to find it — slow, and easy to miss things once the store
has dozens of items.

`search` fixes that: type a few letters you remember, like `note`, and you get back
just the matching products with their price and how many are left. Upper or lower
case doesn't matter, so `NOTE`, `Note` and `note` all work. This makes it quick to
answer "how much is it?" and "is it in stock?" while the customer is still waiting.

### Syntax

```
python3 products.py [--file PATH] search --name TEXT
```

### Inputs

- `--name TEXT` (required): part of a product name
  - Matching ignores upper/lower case: `note`, `NOTE` and `Note` all find "Notebook"
  - A product matches when its name **contains** the text anywhere: `pen` finds both "Pen" and "Pencil"
  - Leading and trailing spaces are ignored; text that is empty after trimming is rejected
  - The text is matched literally, so characters such as `.` or `*` have no special meaning
- `--file PATH` (optional, before `search`): which data file to search

### Expected output

A JSON array of the matching products, sorted by ID, in the same format as `list`.
If nothing matches, it prints `[]`. `search` only reads the data file; it never
creates or changes it.

| Situation | Output | Exit code |
|---|---|---|
| One or more matches | JSON array of the matching products | 0 |
| No matches | `[]` | 0 |
| `--name` missing, empty, or only spaces | error message on stderr | 2 |
| Data file is empty, malformed, or unreadable | error message on stderr | 1 |

### Example you can run

```bash
python3 products.py --file demo.json add --name "Notebook" --price 4.50 --quantity 12
python3 products.py --file demo.json add --name "Pencil" --price 1.25 --quantity 5
python3 products.py --file demo.json add --name "Pen" --price 2 --quantity 10
python3 products.py --file demo.json search --name pen
```

Output:

```json
[
  {
    "id": 2,
    "name": "Pencil",
    "price": "1.25",
    "quantity": 5
  },
  {
    "id": 3,
    "name": "Pen",
    "price": "2.00",
    "quantity": 10
  }
]
```

Edge case — nothing matches:

```bash
python3 products.py --file demo.json search --name xyz
```

```
[]
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success (including an empty result or `--help`) |
| 1 | Product ID not found, invalid data file, or a file read/write failure |
| 2 | Invalid command syntax, missing arguments, or invalid values |

Errors print one line to stderr and nothing to stdout. A failed command never changes the data file.

## Data file

UTF-8 JSON with the next ID to assign and the list of products:

```json
{
  "next_id": 2,
  "products": [
    {"id": 1, "name": "Notebook", "price": "4.50", "quantity": 10}
  ]
}
```

A missing file counts as an empty store and is created by the first successful `add`.
Changes are written to a temporary file first and then swapped in, so a failed write
never leaves a half-written data file.

## How it was built

- Written with Claude Code (an AI coding agent) in incremental rounds: core commands,
  then update/delete and data-file checks, then the `search` feature — each round reviewed and tested
- Tested with Python 3.12
- Classmates' public submissions were read for comparison and critique; no code was copied
