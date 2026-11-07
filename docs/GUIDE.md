# Project Guide

A plain-language description of what this tool does and the rules it follows. It is the
specification that the code in `products.py` and the checks in [TESTING.md](TESTING.md) are built against.

---

## 1. In one sentence

A small program you use **by typing commands in a terminal**, to keep a store's inventory:
which products it has, what each one costs, and how many are left.

| Thing | What it is | Think of it as |
|---|---|---|
| `products.py` | The Python program | The bookkeeper |
| `products.json` | The file where the data lives | The ledger |
| A command you type, e.g. `python3 products.py list` | One request | What you tell the bookkeeper to do |

Every command does one job and then exits. The program **never stops to ask you a question**.

## 2. The six commands

| Command | In plain words | Example | Prints on success |
|---|---|---|---|
| `add` | Stock a new product | `add --name "Notebook" --price 4.5 --quantity 10` | The new product |
| `list` | Show every product | `list` | All products sorted by ID; `[]` if there are none |
| `get` | Look up one product | `get 1` | Product 1 |
| `update` | Change some details of a product | `update 1 --quantity 12` | The product after the change (fields you did not mention stay the same) |
| `delete` | Remove a product | `delete 2 --yes` | `{"deleted_id": 2}` |
| `search` | Find products by part of their name | `search --name note` | Matching products sorted by ID; `[]` if none match |

Two options work everywhere:

- `--help` shows usage. It also works after any command, e.g. `update --help`.
- `--file PATH` uses a different data file instead of the default `products.json`. It **must come before the command**, e.g. `--file demo.json list`.

## 3. What is stored for each product

| Field | Rule | Accepted | Rejected |
|---|---|---|---|
| id | Assigned automatically, starting at 1 and counting up. **A deleted ID is never reused** | — | Choosing your own ID |
| name | At least one character; leading and trailing spaces are trimmed; duplicate names are allowed | `"  Pen  "` is stored as `"Pen"` | Empty, or only spaces |
| price | A plain number with at most two decimals, always stored as a two-decimal **string** | `0`, `4.5`, `4.50` (stored like `"4.50"`) | `-1`, `+1`, `$4`, `1e3`, `4.555`, `4.`, `.5` |
| quantity | 0 or a positive whole number | `0`, `10` | `-1`, `2.5` |

## 4. Rules for the data file

- The file holds two things: `next_id` (the ID the next new product will get) and `products` (the list of products).
- **A file that does not exist yet** counts as an empty store: `list` prints `[]`; `get`, `update` and `delete` report "not found". **The file is created by the first successful `add`.**
- **Read-only commands** (`list`, `get`, `search`, `--help`) never create or change the file.
- **A file that is empty, corrupted or in the wrong format** is an error, and the tool **leaves it untouched**.
- Every change is fully saved before the tool reports success.
- If the folder given in `--file` does not exist, that is an error; the tool never creates folders.

## 5. When something goes wrong

Every error follows four rules:

1. Print **one short line** that says what went wrong. A "not found" error names the ID.
2. **Never show a Python traceback** (the long crash report Python prints when a program fails).
3. **Leave the data file exactly as it was.** A failed command does not use up an ID either.
4. Report the result with an **exit code**: a number the program leaves behind when it finishes. You do not see it on screen, but scripts and automated tests can check it (`echo $?` shows it):

| Exit code | When | Examples |
|---|---|---|
| 0 | Success, including an empty `list` and `--help` | `list` |
| 1 | The product was not found, or the data file has a problem | `get 99`; a corrupted data file |
| 2 | The command was typed wrong, something is missing, or a value is invalid | `add` without `--price`; price `-1`; `delete` without `--yes`; `update` with no fields |

Rule of thumb: **wrongly written = 2; written fine but cannot be done = 1.**

## 6. The custom feature: search by name

Beyond the five basic commands, the tool adds `search`:

```bash
python3 products.py search --name note
```

- **Who it helps:** store staff who cannot remember a product's full name; typing part of it is enough
- **How it matches:** ignores upper and lower case; a product matches when its name **contains** the text
- **What it prints:** the matching products sorted by ID, or `[]` when nothing matches (that is not an error)
- **Also:** works with `--file`, appears in `--help`, and does not change how the other five commands behave

See the README for a full example you can run.

## 7. A typical session

Starting with no `products.json`:

```bash
python3 products.py --help
python3 products.py add --name "Notebook" --price 4.5 --quantity 10
python3 products.py add --name "Pencil" --price 1.25 --quantity 5
python3 products.py list
python3 products.py get 1
python3 products.py update 1 --quantity 12
python3 products.py delete 2 --yes
python3 products.py list
```

Afterwards `products.json` holds only the Notebook, with price `"4.50"`, quantity 12 and `next_id` 3.
Running any command again shows the data is still there.
