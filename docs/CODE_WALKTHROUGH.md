# Code Walkthrough

A beginner-friendly tour of [products.py](../products.py). The "Lines" columns refer to the line
numbers in that file.

---

## 0. Meet the restaurant

Picture the program as a small restaurant. Typing a command in the terminal is placing an order.

| Role in the story | Job | Who it is in the code | Lines |
|---|---|---|---|
| **Front desk** | Takes the order and checks it is filled in correctly; **never goes into the kitchen** | `build_parser` | 249–331 |
| **Front desk checklist** | Checks that a name, price, quantity or ID is acceptable | `parse_name`, `parse_price`, `parse_quantity`, `parse_id` | 47–76 |
| **Manager** | Hands the order to a cook, then tells the customer the result | `main` | 334–348 |
| **Cooks** | Do the real work, one cook per command | `cmd_add`, `cmd_list`, `cmd_get`, `cmd_update`, `cmd_delete`, `cmd_search` | 190–244 |
| **Raising a hand** | A cook who hits a problem does not talk to the customer; they raise a hand for the manager | `raise CLIError(...)` | throughout |
| **The ledger** | The file that stores every product | `products.json` | — |
| **Opening the ledger** | Reads the file and checks its content | `load_store` | 85–105 |
| **Closing the ledger** | Safely writes changes back to the file | `save_store` | 150–177 |

---

## 1. The map: five blocks from top to bottom

| # | Block | Lines | What it does | In the story |
|---|---|---|---|---|
| 1 | Setup | 1–40 | Imports, constants, and the "raise a hand" error type | Laying out the tools before opening |
| 2 | Input checks | 42–76 | Four gatekeeper functions | The front desk checklist |
| 3 | Reading and writing the file | 79–177 | Open, check and close the ledger | Looking after the ledger |
| 4 | The six commands | 180–244 | The real work | The cooks |
| 5 | Wiring | 247–352 | Defines what each command looks like, and runs everything | The menu and the manager |

---

## 2. One command from start to finish (`get 1`)

| Step | Story | Code | Lines | In plain words |
|---|---|---|---|---|
| 1 | A customer walks in | `sys.exit(main())` | 351–352 | The program starts and calls the manager. The number the manager returns (0/1/2) becomes the exit code |
| 2 | The front desk checks the order | `args = parser.parse_args(argv)` | 337 | Recognizes the command `get`; hands `"1"` to `parse_id`, which turns it into the number 1 |
| 2a | The order is written wrong | (handled at the front desk) | — | For example `get abc`: the front desk stops it on the spot, prints one error line, exit code **2**. **The ledger is never opened** |
| 3 | The manager assigns the job | `result = args.handler(args)` | 339 | `handler` is the cook written on the menu (line 294: `handler=cmd_get`), so this calls `cmd_get` |
| 4 | The cook opens the ledger | `store = load_store(args.file)` | 210 | Reads `products.json` |
| 5 | The cook finds the product | `return find_product(store, args.id)` | 211 | Found it: hands the product back to the manager |
| 5a | Not found | `raise CLIError(...)` | 187 | The cook raises a hand: "there is no product with this ID" |
| 6 | The manager wraps up (success) | `print(json.dumps(result, indent=2))` and `return EXIT_OK` | 347–348 | Prints the result as JSON, exit code **0** |
| 6a | The manager wraps up (failure) | `print(f"error: {e}", file=sys.stderr)` and `return e.exit_code` | 340–342 | Prints one `error: ...` line, exit code **1** (or 2) |

**The key idea: cooks only cook; they never talk to the customer.** A cook either returns a
result (`return`) or raises a hand (`raise CLIError`). What gets printed and which exit code is
used are decided in one place, `main`. That is why all six commands report errors the same way,
and why a traceback never appears.

---

## 3. Setup (lines 1–40)

| # | Lines | Code | In plain words |
|---|---|---|---|
| 3.1 | 1 | `#!/usr/bin/env python3` | Tells the system "run me with Python 3". Not needed when you run `python3 products.py` |
| 3.2 | 2–9 | `"""..."""` | A docstring: text for people; it does not run |
| 3.3 | 11–16 | `import argparse` and others | Borrowing tools. All are part of Python's standard library, so nothing needs installing |
| 3.4 | 18 | `DEFAULT_FILE = "products.json"` | The data file used when `--file` is not given |
| 3.5 | 21–23 | `EXIT_OK = 0` and others | Names for 0, 1 and 2; a name is easier to read than a bare number |
| 3.6 | 26–28 | `PRICE_PATTERN = re.compile(...)` | The "shape rules" (regular expressions) for prices and integers that the gatekeepers compare against |
| 3.7 | 30–31 | `STORE_KEYS`, `PRODUCT_KEYS` | The exact fields the file and each product must have, no more and no less |
| 3.8 | 34–39 | `class CLIError(Exception)` | The restaurant's single way of raising a hand: a message plus an exit code (1 unless stated) |

**What each imported tool is for:**

| Tool | Used for |
|---|---|
| `argparse` | The front desk: parses the command you typed |
| `json` | Converts between the file's text and Python data |
| `os` | Talks to the file system: checks permissions, replaces and removes files |
| `re` | Regular expressions: checks the shape of prices and integers |
| `sys` | Sets the exit code; sends errors to stderr |
| `tempfile` | Creates the temporary file used while saving |

---

## 4. The front desk checklist: four gatekeepers (lines 47–76)

These four functions are attached to the menu (lines 271–275, `type=parse_name` and so on).
Every value the front desk receives goes to its gatekeeper first.

**When a gatekeeper says no** (`raise argparse.ArgumentTypeError`), the front desk prints one error
line and exits with code **2**. No cook has started and the ledger has not been opened, so the file
cannot change.

| # | Gatekeeper | Lines | Checks | Returns when valid | Examples |
|---|---|---|---|---|---|
| 4.1 | `parse_name` | 47–51 | Is anything left after trimming spaces? | The trimmed name | `"  Pen  "` → `"Pen"`; `"   "` → rejected |
| 4.2 | `parse_price` | 54–62 | Is it "digits, at most two decimals"? | A two-decimal **string** | `4.5` → `"4.50"`; `-1`, `$4`, `4.555` → rejected |
| 4.3 | `parse_quantity` | 65–70 | Is it 0 or a positive whole number? | An integer | `10` → `10`; `-1`, `2.5` → rejected |
| 4.4 | `parse_id` | 73–76 | Is it a positive integer (not 0)? | An integer | `1` → `1`; `0`, `abc` → rejected |

### `parse_price` step by step (for `4.5`)

| Step | Line | Code | Result | In plain words |
|---|---|---|---|---|
| 1 | 56 | `PRICE_PATTERN.fullmatch(text)` | passes | The *whole* text must match "digits, optionally a point and 1–2 decimals" |
| 2 | 60 | `whole, _, cents = text.partition(".")` | `whole="4"`, `cents="5"` | Split at the decimal point |
| 3 | 61 | `whole.lstrip("0") or "0"` | `"4"` | Drop extra leading zeros (`007` → `7`); if nothing is left, use `0` |
| 4 | 62 | `cents.ljust(2, '0')` | `"50"` | Pad the decimals with zeros on the right to two digits |
| 5 | 62 | `f"{whole}.{cents...}"` | `"4.50"` | Join them |

Two more examples: `0` becomes `"0.00"`, and `007.5` becomes `"7.50"`.

---

## 5. Opening the ledger: `load_store` (lines 85–105)

Every cook calls this to read the file. It checks things in order and, **at the first problem,
raises a hand with exit code 1 without touching the file**.

| # | Lines | Code | Situation | Result |
|---|---|---|---|---|
| 5.1 | 87–89 | `with open(path, "r", encoding="utf-8") as f:` and `text = f.read()` | Open the file and read all of it | Continue |
| 5.2 | 90–91 | `except FileNotFoundError:` | **The file does not exist** | Treated as an empty store: `{"next_id": 1, "products": []}`. **No file is created** |
| 5.3 | 92–93 | `except UnicodeDecodeError:` | The file is not UTF-8 text | Raise a hand |
| 5.4 | 94–95 | `except OSError as e:` | It cannot be opened: no permission, or the path is a folder | Raise a hand |
| 5.5 | 97–98 | `if not text.strip():` | The file is empty or only whitespace | Raise a hand |
| 5.6 | 99–102 | `json.loads(text)` | Turn the text into Python data; it is not valid JSON | Raise a hand, naming the line |
| 5.7 | 104 | `check_store(store, path)` | It is valid JSON, but does it follow every rule? | Raise a hand if not (see below) |
| 5.8 | 105 | `return store` | Everything is fine | Hand the store to the cook |

### What `check_store` checks (lines 113–147)

| # | Lines | Check | Example that fails |
|---|---|---|---|
| 5.7.1 | 118–119 | The top level has exactly `next_id` and `products` | An extra `"owner"` field |
| 5.7.2 | 120–122 | `next_id` is a positive integer | `"next_id": "3"`, `"next_id": true` |
| 5.7.3 | 123–124 | `products` is a list | `"products": {}` |
| 5.7.4 | 128–129 | Every product has exactly id, name, price and quantity | `quantity` is missing |
| 5.7.5 | 131–132 | A product ID is a positive integer | `"id": 0` |
| 5.7.6 | 133–134 | No duplicate IDs | Two products with ID 1 |
| 5.7.7 | 135–136 | `next_id` is greater than every ID | ID 3 exists but `next_id` is 2, so the next add would collide |
| 5.7.8 | 139–141 | The name is a non-empty string with no extra outer spaces | `"name": " Pen"` |
| 5.7.9 | 142–144 | The price is a two-decimal string like `"4.50"` | `"price": 4.5` (a number, not a string) |
| 5.7.10 | 145–147 | The quantity is 0 or a positive integer | `"quantity": -1` |

**Why `is_int` exists (lines 108–110):** Python counts `True` and `False` as integers (`True`
equals 1). `is_int` rules them out; otherwise `"next_id": true` would slip through as 1.

---

## 6. Closing the ledger: `save_store` (lines 150–177)

**The core idea: never edit the original in place.** First copy the whole ledger onto a fresh
sheet (a temporary file). Only when that succeeds, swap the fresh sheet in for the original. If
anything fails along the way, only the fresh sheet is spoiled and the original is untouched.

| # | Lines | Code | In plain words |
|---|---|---|---|
| 6.1 | 157–158 | `if os.path.exists(path) and not os.access(path, os.W_OK):` | The file exists but is read-only: raise a hand instead of quietly replacing it |
| 6.2 | 159 | `folder = os.path.dirname(os.path.abspath(path))` | Find the file's folder; the fresh sheet must be in the same folder |
| 6.3 | 162 | `tempfile.mkstemp(dir=folder, ...)` | Get a fresh sheet in that folder, named like `.products-abc123.tmp` |
| 6.4 | 163–165 | `json.dump(store, f, indent=2, ensure_ascii=False)` | Write the whole store onto it. `indent=2` keeps it tidy; `ensure_ascii=False` keeps non-English text as written |
| 6.5 | 167 | `os.chmod(temp_path, 0o644)` | A fresh temp file is private by default; give it normal file permissions |
| 6.6 | 168 | `os.replace(temp_path, path)` | **The key step**: swap the fresh sheet in. It either fully happens or does not happen at all |
| 6.7 | 169 | `temp_path = None` | Note that the fresh sheet has been used |
| 6.8 | 170–171 | `except OSError as e:` | Any step failed (for example the folder does not exist): raise a hand, exit code 1 |
| 6.9 | 172–177 | `finally:` and `os.remove(temp_path)` | Runs whether it worked or not: if the fresh sheet was not used, throw it away so no clutter is left |

---

## 7. The six cooks (lines 183–244)

**One rule for every cook: the file is always written last.** Everything is prepared first, and
`save_store` is the final step. So if anything goes wrong earlier, the file is never touched and no
ID is used up.

### 7.0 Helper: `find_product` (lines 183–187)

| Lines | Code | In plain words |
|---|---|---|
| 184 | `for product in store["products"]:` | Look at the products one by one |
| 185–186 | `if product["id"] == product_id:` and `return product` | The ID matches: hand that product back |
| 187 | `raise CLIError(f"product with ID {product_id} not found")` | None matched: raise a hand and name the ID |

Used by `get`, `update` and `delete`.

### 7.1 `cmd_add`: stock a new product (lines 190–201)

| Step | Line | Code | In plain words |
|---|---|---|---|
| 1 | 191 | `store = load_store(args.file)` | Open the ledger |
| 2 | 192–197 | `product = {"id": store["next_id"], ...}` | Fill in a new product card: the ID is the ledger's "next ID"; name, price and quantity are the values the front desk already checked |
| 3 | 198 | `store["products"].append(product)` | Add the card to the list (only in memory so far, nothing saved yet) |
| 4 | 199 | `store["next_id"] += 1` | Move "next ID" up by one |
| 5 | 200 | `save_store(args.file, store)` | Close the ledger: actually save to disk. **If the file did not exist, this is where it gets created** |
| 6 | 201 | `return product` | Hand the new product to the manager to print |

**Why is a deleted ID never reused?** Because `next_id` only ever goes up, on line 199. Deleting
does not touch it, and it never goes back.

### 7.2 `cmd_list`: show every product (lines 204–206)

| Line | Code | In plain words |
|---|---|---|
| 205 | `store = load_store(args.file)` | Open the ledger |
| 206 | `return sorted(store["products"], key=lambda product: product["id"])` | Sort by ID and hand it back. An empty store gives the empty list `[]` |

Read-only, so there is no `save_store`.

### 7.3 `cmd_get`: look up one product (lines 209–211)

Open the ledger, find the product with `find_product`, hand it back. Read-only.

### 7.4 `cmd_update`: change a product (lines 214–225)

| Step | Lines | Code | In plain words |
|---|---|---|---|
| 1 | 216–218 | `changes = {field: getattr(args, field) for field in (...) if ... is not None}` | Collect the fields the user supplied (name, price, quantity). A field not supplied is `None` and is skipped |
| 2 | 219–220 | `if not changes:` and `raise CLIError(..., EXIT_USAGE_ERROR)` | Nothing supplied: raise a hand, exit code **2** (the order is incomplete). The ledger has not been opened yet |
| 3 | 221 | `store = load_store(args.file)` | Open the ledger |
| 4 | 222 | `product = find_product(store, args.id)` | Find the product; if it is missing, raise a hand, exit code 1 |
| 5 | 223 | `product.update(changes)` | Change only the supplied fields; everything else, including the ID, stays the same |
| 6 | 224 | `save_store(args.file, store)` | Close the ledger |
| 7 | 225 | `return product` | Hand back the updated product |

### 7.5 `cmd_delete`: remove a product (lines 228–235)

| Step | Lines | Code | In plain words |
|---|---|---|---|
| 1 | 229–230 | `if not args.yes:` and `raise CLIError(..., EXIT_USAGE_ERROR)` | No `--yes`: raise a hand, exit code 2. The program never asks "are you sure?" |
| 2 | 231 | `store = load_store(args.file)` | Open the ledger |
| 3 | 232 | `product = find_product(store, args.id)` | Find the product |
| 4 | 233 | `store["products"].remove(product)` | Take it out of the list. `next_id` is left alone |
| 5 | 234 | `save_store(args.file, store)` | Close the ledger |
| 6 | 235 | `return {"deleted_id": product["id"]}` | Hand back a result like `{"deleted_id": 2}` |

### 7.6 `cmd_search`: find by name (lines 238–244) — the custom feature

| Step | Line | Code | In plain words |
|---|---|---|---|
| 0 | (front desk) | `type=parse_name` (line 327) | The front desk checks first: after trimming, the search text cannot be empty, otherwise exit code 2 |
| 1 | 240 | `text = args.name.casefold()` | Make the search text case-insensitive: `NOTE` and `Note` both become `note` |
| 2 | 241 | `store = load_store(args.file)` | Open the ledger |
| 3 | 243 | `[product for product in store["products"] if text in product["name"].casefold()]` | Go through the products: keep each one whose name, also case-folded, **contains** the search text |
| 4 | 244 | `return sorted(matches, key=...)` | Sort by ID and hand back. No match gives `[]` |

**Summary of search:**

| Aspect | Details |
|---|---|
| Input | `--name` followed by part of a name, e.g. `note` |
| Processing | Case-insensitive; a name that **contains** the text matches; a plain "contains" test, so `.` and `*` have no special meaning |
| Output | The matching products sorted by ID; `[]` when nothing matches, still exit code 0 (no match is not an error) |

Read-only, so there is no `save_store`.

---

## 8. The menu: `build_parser` (lines 249–331)

It defines what every command looks like. Each command follows the same pattern:

| # | Lines | Code | In plain words |
|---|---|---|---|
| 8.1 | 250–255 | `parser = argparse.ArgumentParser(prog="products.py", ...)` | Build the front desk. `allow_abbrev=False` refuses abbreviations, so `--na` does not count as `--name` |
| 8.2 | 256–262 | `parser.add_argument("--file", default=DEFAULT_FILE, ...)` | The global `--file` option, written before the command |
| 8.3 | 263 | `commands = parser.add_subparsers(..., required=True)` | A place for the commands; `required=True` means a command must be given |
| 8.4 | 265–270 | `add = commands.add_parser("add", help=..., ...)` | Register a dish: `add`. `help` is the line shown in `--help` |
| 8.5 | 271–276 | `add.add_argument("--name", required=True, type=parse_name, ...)` | What the dish needs, whether it is required, and which gatekeeper checks it |
| 8.6 | 277 | `add.set_defaults(handler=cmd_add)` | Write on the menu "`cmd_add` makes this dish". This is how the manager finds the cook |
| 8.7 | 279–329 | The other five commands | The same pattern as 8.4 to 8.6 |

**Arguments for each command:**

| Command | Required | Optional |
|---|---|---|
| `add` | `--name`, `--price`, `--quantity` | — |
| `list` | — | — |
| `get` | ID | — |
| `update` | ID | `--name`, `--price`, `--quantity` (at least one, checked by `cmd_update`) |
| `delete` | ID | `--yes` (rejected by `cmd_delete` if missing) |
| `search` | `--name` | — |

---

## 9. The manager: `main` (lines 334–352)

| # | Lines | Code | In plain words |
|---|---|---|---|
| 9.1 | 335 | `parser = build_parser()` | Set up the front desk and the menu |
| 9.2 | 337 | `args = parser.parse_args(argv)` | Let the front desk check the order. A badly written order ends the program right here (exit code 2); `--help` also prints and ends here (exit code 0) |
| 9.3 | 338–339 | `try:` and `result = args.handler(args)` | Hand the order to the cook named on the menu and wait for the result |
| 9.4 | 340–342 | `except CLIError as e:` | A cook raised a hand: print `error: <message>` and use the exit code that came with it (1 or 2) |
| 9.5 | 343–346 | `except Exception as e:` | **Safety net**: even a problem nobody expected prints just one error line with exit code 1, never a traceback |
| 9.6 | 347 | `print(json.dumps(result, indent=2))` | Success: print the result as tidy JSON |
| 9.7 | 348 | `return EXIT_OK` | Exit code 0 |
| 9.8 | 351–352 | `if __name__ == "__main__":` and `sys.exit(main())` | When the file is run directly, start the manager and use the returned number as the exit code |

**Why do errors go to stderr (`file=sys.stderr`)?** A terminal has two output channels: stdout
for normal results, stderr for errors. Keeping them apart means another program reading the
results never mistakes an error message for data.

---

## 10. Exit codes at a glance: whoever finds the problem decides

| Exit code | Found by | Situation | Examples |
|---|---|---|---|
| 0 | Nobody, all good | Success, including an empty result and `--help` | `list` prints `[]` |
| 2 | **The front desk** (gatekeepers) | The order is written wrong | `get abc`, price `-1`, `--price` missing |
| 2 | **A cook, before opening the ledger** | The order is incomplete | `update 1` with no fields, `delete 1` without `--yes` |
| 1 | **A cook, after opening the ledger** | The order is fine but cannot be carried out | `get 99` when there is no 99, a broken file, a file that cannot be written |

Rule of thumb: **wrongly written = 2; cannot be done = 1.**

---

## 11. Python glossary (as used in this file)

| Term | In plain words | Example here | Line |
|---|---|---|---|
| `import` | Borrow a tool | `import json` | 12 |
| `def` | Define a function (a named small task) | `def cmd_add(args):` | 190 |
| `return` | Hand back a result; the function ends here | `return product` | 201 |
| `raise` | Raise a hand with an error; the code after it does not run | `raise CLIError(...)` | 187 |
| `try` / `except` | Try something; if a certain problem happens, do the `except` part instead | `try: ... except FileNotFoundError:` | 87–91 |
| `finally` | Always runs at the end, success or failure | Throw away an unused temp file | 172 |
| `with open(...) as f` | Open a file and close it automatically afterwards | Reading the ledger | 88 |
| `if` / `if not` | If ... / if not ... | `if not args.yes:` | 229 |
| `for ... in ...` | Go through items one by one | `for product in store["products"]:` | 184 |
| `x in y` (inside an `if`) | Does y contain x? | `text in product["name"]` | 243 |
| `{...}` dictionary | A card with labeled fields | `{"id": 1, "name": "Pen", ...}` | 192–197 |
| `[...]` list | A row of items | `"products": []` | 82 |
| `store["next_id"]` | Read one field from a card | — | 193 |
| `.append(x)` | Add an item to the end of a list | `store["products"].append(product)` | 198 |
| `.remove(x)` | Take an item out of a list | `store["products"].remove(product)` | 233 |
| `+= 1` | Add one | `store["next_id"] += 1` | 199 |
| `.strip()` | Remove leading and trailing spaces | `text.strip()` | 48 |
| `.casefold()` | Make text case-insensitive for comparison | `args.name.casefold()` | 240 |
| `f"...{x}..."` | Put a variable's value into a sentence | `f"product with ID {product_id} not found"` | 187 |
| `None` | "Nothing", e.g. an option that was not given | `is not None` | 218 |
| `sorted(..., key=lambda p: p["id"])` | Sort, using each product's `id` | `cmd_list` | 206 |
| `[p for p in items if condition]` | Pick the items that meet a condition into a new list | `cmd_search` | 243 |
| `class` | Define a new kind of thing; here, a new way to raise a hand | `class CLIError(Exception)` | 34 |

---

## 12. Check your understanding

<details>
<summary>1. You type <code>get abc</code>. What is the exit code? Is the file opened?</summary>

Exit code 2. The gatekeeper `parse_id` rejects it at the front desk, no cook ever starts, so the
file is **not** opened.
</details>

<details>
<summary>2. You type <code>get 99</code> and there is no product 99. Who notices, and what is the exit code?</summary>

A cook. `99` is a well-formed number, so the front desk lets it through; the cook opens the ledger,
`find_product` finds nothing, and the cook raises a hand. Exit code 1.
</details>

<details>
<summary>3. <code>products.json</code> does not exist and you run <code>add</code> for the first time. At which step is the file created?</summary>

Step 5 of `cmd_add`, `save_store` (line 200). More precisely, `os.replace` inside `save_store`
(line 168) swaps the fresh sheet in as the real file. The earlier `load_store` only treats "missing"
as an empty store; it does not create anything.
</details>

<details>
<summary>4. After deleting product 2 you add a new product. What is its ID, and why?</summary>

Not 2, but whatever `next_id` was at that moment (for example 3). Deleting leaves `next_id` alone,
and it only goes up on add, so a deleted ID is never used again.
</details>

<details>
<summary>5. Why write a temporary file first instead of editing the file directly?</summary>

If writing directly failed half-way, only half a ledger would be left and the file would be broken.
Writing to a temporary file and then swapping it in with `os.replace` means a failure part-way leaves
the original exactly as it was.
</details>

<details>
<summary>6. <code>search --name xyz</code> finds nothing. What is the exit code?</summary>

0. Finding nothing is not an error; it prints `[]`.
</details>

<details>
<summary>7. Why do all six commands report errors the same way, and never show a traceback?</summary>

Cooks never print errors themselves; they only raise a hand (`raise CLIError`). Printing and exit
codes are handled in one place, `main`. And for anything nobody expected, `main` has a safety net
(`except Exception`) that also prints just one line.
</details>

---

## 13. Building it from scratch: eight steps to the current version

The principle: **at the end of every step the program runs and can be tested.** Do not write it
all and test at the end; when something breaks, you know it was the part you just added.

### 13.1 The eight steps

| Step | Goal | What this step adds | Rough size afterwards | How to test this step |
|---|---|---|---|---|
| 0 | **Design first**, no code | Decide three things on paper: ① the split between front desk, manager and cooks; ② the file shape `{next_id, products}`; ③ two rules, "cooks only return or raise" and "write the file last" | 0 lines | Nothing to test yet, but this decides how easy everything after it is to change |
| 1 | **Add and list** | The `argparse` skeleton; `load_store` (missing file = empty store); a simple `save_store` (write directly); `cmd_add`, `cmd_list` | ~60 | `add` twice, `list` shows both |
| 2 | **All five basic commands** | `cmd_get`, `cmd_update`, `cmd_delete`; `find_product`; `CLIError` and `main` reporting errors in one place; exit code 1 for "not found" | ~100 | Normal use of all five commands works; `get 99` fails with exit code 1 |
| 3 | **Gatekeepers on duty** | `parse_name`, `parse_price` (including turning it into `"4.50"`), `parse_quantity`, `parse_id`; `update` needs a field; `delete` needs `--yes`; exit code 2 | ~150 | Bad input is rejected with exit code 2 and the file is unchanged |
| 4 | **Protect the file** | `load_store` handles empty, non-UTF-8 and non-JSON files; the `check_store` rules; `is_int` | ~220 | Hand-make a few broken files: each one fails with exit code 1 and is left unchanged |
| 5 | **Safe writes** | Temporary file plus `os.replace`; read-only files; missing folders; no leftover temp files; the `except Exception` safety net in `main` | ~280 | Read-only files and missing folders fail cleanly, no crash |
| 6 | **Polish** | `--help` text, `allow_abbrev=False`, `list` sorted by ID, all errors on stderr | ~320 | Go through `--help` and the output format item by item |
| 7 | **Custom feature and docs** | `cmd_search`, the README | ~350 | The 17 search tests; run the README example and compare the output |

### 13.2 Which steps matter most

- **Step 0** is the easiest to skip and the most important. It lays the foundation: cooks only raise a hand, the manager does all the talking, the file is written last. A foundation is painful to change later; decoration can always be added.
- **Step 2** is where the structure becomes real. Once `CLIError` plus "main does the talking" is in place, steps 3 to 7 only add to it, with no big rewrites.
- **Steps 4 and 5** are the most tiring and add no new features; they are all "what if" cases. They are also what makes the tool trustworthy with real data.

### 13.3 How it was actually built

It was built in three rounds with an AI coding agent, since the agent can write a lot in one go:

| Round | Matches steps |
|---|---|
| 1: `add`, `list`, `get`, `--help`, input checks | 0, 1 and 3, plus part of 2 |
| 2: `update`, `delete`, file checks, safe writes, error handling | the rest of 2, plus 4, 5 and 6 |
| 3: `search` and the README | 7 |

**The specification, the tests and the code push each other forward:** you write code from the
spec, testing reveals problems, and sometimes the fix is in the code while other times the spec was
unclear and needs filling in. Almost nobody gets it all right the first time.
