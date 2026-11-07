# Manual Test Checklist

A black-box checklist for `products.py`: every test is a command you type in a terminal, with
what you should see, what counts as a bug, and what the test is really checking.

**Last full run:** 2026-11-06, macOS, Python 3.12.15 and Python 3.9.6 — all tests passed.

---

## How to run the tests

1. Open a terminal in the folder that contains `products.py`.
2. Run the sections **in order**, starting from section 1. Later tests build on the results of earlier ones.
3. For every test, check three things:

| Check | How | What to look for |
|---|---|---|
| Screen output | Read it | Success prints JSON (`{...}` or `[...]`); failure prints one line starting with `error:` |
| Exit code | Run `echo $?` right after the command | 0 = success; 1 = not found or a file problem; 2 = bad syntax or an invalid value |
| Data file | `cat products.json` for the content; `shasum products.json` for a fingerprint | Two identical fingerprints mean the file did not change by a single byte |

4. **Reading the tables:** when a test says "error", the program is *supposed* to refuse. A refusal is a **pass**. Only the "Bug if" column describes a failure.
5. **Always a bug, in any test:**
   - a `Traceback` (a multi-line Python crash report) appears
   - the program stops and waits for you to type something
   - a command that failed still changed the data file
6. **Shell tips:**
   - `$` has a special meaning in the shell, so quote prices like `'$4'` with single quotes.
   - `command not found` or exit code 127 means you left out `python3 products.py` and the shell tried to run `update` or `get` as a program. Code 127 comes from the shell, not from this tool.
   - If `python3` on your machine is older than 3.9, use a newer interpreter such as `python3.12`.

---

## 1. Help

| ID | Command | Expected | Bug if | What it checks |
|---|---|---|---|---|
| T01 | `python3 products.py --help` | Usage text listing add, list, get, update, delete and search; exit 0; `ls products.json` says the file does not exist | A command is missing; products.json was created | Help only describes the tool; it must never touch the data file |
| T02 | `python3 products.py add --help` | Lists `--name`, `--price`, `--quantity`; exit 0 | An option is missing | add's help: all three options are required |
| T03 | `python3 products.py update --help` | Lists ID and the three optional fields; exit 0 | — | update's help: ID is required, and you supply only the fields you want to change |
| T04 | `python3 products.py delete --help` | Mentions `--yes`; exit 0 | — | delete needs `--yes`, a guard against accidents |
| T05 | `python3 products.py get --help` and `python3 products.py list --help` | Each shows its own help; exit 0 | — | Every command has its own `--help` |
| T06 | `echo "garbage" > bad.json`, then `python3 products.py --file bad.json --help` | Help is shown, exit 0; `cat bad.json` still says `garbage` | An error; bad.json changed | A deliberately broken data file: if help opened it, there would be an error. Clean help = the file was never opened; unchanged content = never written |

## 2. Standard workflow

Start with **no** `products.json`.

| ID | Command | Expected | Bug if | What it checks |
|---|---|---|---|---|
| T07 | `ls products.json` | `No such file or directory` | The file exists (run `rm products.json` first) | Clean starting point: no data file yet |
| T08 | `python3 products.py list` | `[]`, exit 0; the file still does not exist | An error; the file was created | A missing file is an empty store; a read-only command must not create the file |
| T09 | `python3 products.py add --name "Notebook" --price 4.5 --quantity 10` | `"id": 1`, `"price": "4.50"`, `"quantity": 10`; exit 0; the file is created | Price shown as `4.5` or `4.50` without quotes; id is not 1 | The first successful add creates the file; price 4.5 is normalized to the string "4.50" |
| T10 | `python3 products.py add --name "Pencil" --price 1.25 --quantity 5` | `"id": 2` | id is not 2 | IDs count up automatically |
| T11 | `python3 products.py list` | Two products: Notebook (1) first, Pencil (2) second | Wrong order; one is missing | list prints every product sorted by ID |
| T12 | `python3 products.py get 1` | Notebook | Another product is shown | get looks up one product by ID |
| T13 | `python3 products.py update 1 --quantity 12` | quantity 12, price still `"4.50"`, name still Notebook | Another field changed or disappeared | update changes only the fields you supply |
| T14 | `python3 products.py delete 2 --yes` | `{"deleted_id": 2}` | Any other format, such as a sentence | A successful delete prints exactly `{"deleted_id": 2}` |
| T15 | `python3 products.py list` | Only Notebook, quantity 12 | Pencil is still there; Notebook is gone too | The deleted product is gone and the other one stays |
| T16 | `cat products.json` | `"next_id": 3`; price `"4.50"` **in quotes**; quantity `12` **without quotes** | next_id is not 3; price not quoted; quantity quoted | In the file itself: next_id never goes back after a delete; price is a string, quantity is a number |
| T17 | `python3 products.py get 1` again | Still quantity 12 | The data is lost | A fresh run still sees it = the data really was saved to disk |

## 3. Update details

| ID | Command | Expected | Bug if | What it checks |
|---|---|---|---|---|
| T18 | `python3 products.py update 1 --name "  Big Notebook  " --price 5` | Name `"Big Notebook"` (outer spaces trimmed), price `"5.00"`, quantity still 12, id still 1 | Spaces kept; quantity changed | Leading and trailing spaces are trimmed, inner ones kept; fields not supplied stay the same |
| T19 | `python3 products.py update 1 --name "Notebook" --price 4.50 --quantity 12` | All three fields change back | A field did not change | Supplying all three fields changes all three |
| T20 | `cat products.json` | `next_id` is still 3 | next_id changed | Updates never affect next_id |

## 4. ID rules

Uses a separate file, `ids.json`, so products.json is not affected.

| ID | Command | Expected | Bug if | What it checks |
|---|---|---|---|---|
| T21 | `python3 products.py --file ids.json add --name A --price 1 --quantity 1` | id 1 | — | A fresh file via `--file`: IDs start at 1, so results are predictable and products.json is untouched |
| T22 | `python3 products.py --file ids.json add --name B --price 1 --quantity 1` | id 2 | — | IDs keep counting up |
| T23 | `python3 products.py --file ids.json delete 2 --yes` | `{"deleted_id": 2}` | — | Delete ID 2 |
| T24 | `python3 products.py --file ids.json add --name C --price 1 --quantity 1` | id **3** | id is 2 (a deleted ID was reused) | ID 2 is never used again: new IDs come only from next_id, never from gaps |
| T25 | `python3 products.py --file ids.json delete 3 --yes`, then `python3 products.py --file ids.json add --name D --price 1 --quantity 1` | D gets id **4** | id is 3 | Even the highest deleted ID is never reused |
| T26 | `cat ids.json` | `next_id` is 5; only ids 1 and 4 remain | — | Confirm the file: next_id 5, ids 1 and 4 |

## 5. `--file` and data-file rules

| ID | Command | Expected | Bug if | What it checks |
|---|---|---|---|---|
| T27 | `shasum products.json`, then `python3 products.py --file demo.json add --name "Notebook" --price 4.50 --quantity 10`, then `shasum products.json` | demo.json is created; products.json has the same fingerprint before and after | products.json changed | `--file` touches only the chosen file |
| T28 | `python3 products.py --file demo.json list` | Only the Notebook from demo.json | Shows products.json's content | list reads the file named by `--file` and nothing else |
| T29 | `python3 products.py --file "my data.json" add --name "Pen" --price 2 --quantity 3` | Success; `my data.json` is created | A space in the file name breaks it | A file name with a space needs quotes so the shell passes it as one argument |
| T30 | `mkdir -p sub`, then `python3 products.py --file sub/x.json add --name A --price 1 --quantity 1` | Success; `sub/x.json` is created | — | Relative paths work from the current folder; you create `sub` yourself because the tool never creates folders |
| T31 | `python3 products.py --file nodir/x.json add --name A --price 1 --quantity 1` | Error, exit 1; `ls nodir` says it does not exist | The tool created the nodir folder | The tool creates files, never folders; a missing folder is an error (1) |
| T32 | `python3 products.py list --file demo.json` | Error, exit 2 | demo.json is listed | `--file` must come before the command; after it, it is a syntax error (2) |
| T33 | `python3 products.py --file new.json get 1` | Error: ID 1 not found, exit 1; new.json is not created | new.json was created | Looking something up in a missing file: "not found", and no file is created |
| T34 | `python3 products.py --file new.json update 1 --quantity 1` | Error, exit 1; new.json is not created | new.json was created | Same for update |
| T35 | `python3 products.py --file new.json delete 1 --yes` | Error, exit 1; new.json is not created | new.json was created | Same for delete |
| T36 | `python3 products.py --file new.json list` | `[]`, exit 0; new.json is not created | new.json was created | list on a missing file shows `[]` and creates nothing |
| T36b | `python3 products.py add --name "笔记本" --price 3 --quantity 2`, then `cat products.json` | Success; the file shows 笔记本 as written | An error; garbled text in the file | Non-ASCII names are stored as UTF-8. The screen may show `笔...` escapes, which mean the same thing; the file is what counts |

## 6. Input validation

This section has two parts:

- **Should succeed** (T39–T44, T57): uses its own file, `acc.json`, so products.json is not touched
- **Should fail** (all the rest): uses products.json. Take a fingerprint first; after all of these commands it must be **unchanged**

| ID | Command | Expected | Bug if | What it checks |
|---|---|---|---|---|
| — | `shasum products.json` and note the result | A string of letters and digits | — | Fingerprint products.json to compare at the end of this section |
| T37–38 | `python3 products.py add --name "" --price 1 --quantity 1`, then the same with the name `"   "` | Both fail, exit 2 | A product was added | A name needs at least one non-space character |
| T39–40 | `python3 products.py --file acc.json add --name "  Pen  " --price 1 --quantity 1`, twice | Both succeed, both named `"Pen"`, ids 1 and 2 | The second is rejected as a duplicate; the second overwrote the first | Identical products are allowed and told apart by ID; add always creates, never overwrites |
| T40b | `python3 products.py --file acc.json delete 2 --yes`, then `python3 products.py --file acc.json list` | `{"deleted_id": 2}`; Pen with id 1 is **still there** | Both Pens deleted; id 1 deleted instead | With two identical products, delete removes only the one with the given ID |
| T41–44 | `python3 products.py --file acc.json add --name A --price VALUE --quantity 1` with VALUE = `0`, `4.5`, `4.50`, `10` | Stored as `"0.00"`, `"4.50"`, `"4.50"`, `"10.00"` | Rejected; not two decimals | Every valid price is stored as a two-decimal string |
| T45–56 | `python3 products.py add --name A --price VALUE --quantity 1` with VALUE = `-1`, `+1`, `'$4'`, `1e3`, `4.555`, `4.`, `.5`, `abc`, `""`, `4,50`, `inf`, `nan`, `４.５０` (full-width digits) | Every one fails, exit 2 | Any of them is accepted | A price is plain digits with an optional point and one or two decimals; nothing else |
| T57 | `python3 products.py --file acc.json add --name A --price 1 --quantity 0` | Success, quantity 0 | Rejected | Quantity 0 is valid (sold out for now: set it to 0 instead of deleting) |
| T58–62 | `python3 products.py add --name A --price 1 --quantity VALUE` with VALUE = `-1`, `2.5`, `abc`, `""`, `1e2` | Every one fails, exit 2 | Any of them is accepted | Quantity must be 0 or a positive whole number |
| T63–65 | `python3 products.py update 1 --price -1`, `python3 products.py update 1 --quantity 2.5`, `python3 products.py update 1 --name "   "` | All fail, exit 2 | The update succeeded | update validates every value the same way add does |
| T66 | `python3 products.py update 1 --name "Changed" --price -1`, then `python3 products.py get 1` | Error, exit 2; the name is **not** Changed | The name changed | One invalid value rejects the whole command: all or nothing |
| — | `shasum products.json` again | **Identical** to the fingerprint at the start of this section | It changed (a failing command modified the file) | Proves no failing command in this section touched the file |

## 7. Command syntax

| ID | Command | Expected | Bug if | What it checks |
|---|---|---|---|---|
| T67–73 | `python3 products.py` (no command), `python3 products.py sell`, `python3 products.py list --verbose`, `python3 products.py list extra`, `python3 products.py get 1 2`, `python3 products.py add --name A --price 1`, `python3 products.py get` | Every one fails, exit 2 | Any of them succeeds | Unknown, extra or missing arguments are all syntax errors (2) |
| T74–78 | `python3 products.py get 0`, `python3 products.py get -1`, `python3 products.py get abc`, `python3 products.py get 1.5`, `python3 products.py update 0 --quantity 1`, `python3 products.py delete 0 --yes` | Every one fails, exit 2 | Exit 1, or success | An ID must be a positive integer; 0, negatives, letters and decimals are syntax errors (2) |
| T79 | `python3 products.py update 1` | Error, exit 2 | Success | update needs at least one field |
| T80 | `python3 products.py delete 1`, then `python3 products.py get 1` | Error, exit 2; product 1 still exists | The product was deleted | Without `--yes`, nothing is deleted |
| T81 | `python3 products.py get 99` | Error, exit **1** | Exit 2 | Control case: the ID is well-formed but missing, so it is 1, not 2 |

## 8. Error messages and broken data files

| ID | Command | Expected | Bug if | What it checks |
|---|---|---|---|---|
| T82 | `python3 products.py get 99` | The message contains `99`, exit 1 | The message does not name the ID | A "not found" error says which ID |
| T83 | `python3 products.py get 99 2>/dev/null` | Nothing at all | JSON is printed | `2>/dev/null` hides the error line; what is left (stdout) must be empty when a command fails |
| T84 | `python3 products.py update 99 --quantity 1`, `python3 products.py delete 99 --yes` | Messages contain `99`, exit 1 | — | update and delete report a missing ID the same way |
| T85 | `printf "" > bad.json`, then `python3 products.py --file bad.json list` | Error (empty file), exit 1; bad.json is still empty | Prints `[]` | `printf ""` makes a truly empty file (`echo` would add a newline). Missing = empty store; existing but empty = something went wrong, so it must not restart at ID 1 |
| T86 | `echo "{oops" > bad.json`, then `python3 products.py --file bad.json list` and `python3 products.py --file bad.json add --name A --price 1 --quantity 1` | Both fail, exit 1; `cat bad.json` is still `{oops` | bad.json was overwritten | Malformed JSON: both reading and adding fail, and the broken file is never overwritten |
| T87 | `echo '[]' > bad.json`, then `python3 products.py --file bad.json list` | Error, exit 1 | — | The file must be an object `{ }`, not a list |
| T88 | `echo '{"products": []}' > bad.json`, then `python3 products.py --file bad.json list` | Error (next_id missing), exit 1 | — | next_id is required |
| T89 | `echo '{"next_id": 2, "products": [{"id": 1, "name": "A", "price": 4.5, "quantity": 1}]}' > bad.json`, then `python3 products.py --file bad.json list` | Error (price must be a string), exit 1 | Listed normally | A stored price must be a quoted string |
| T90 | `echo '{"next_id": 1, "products": [{"id": 1, "name": "A", "price": "4.50", "quantity": 1}]}' > bad.json`, then `python3 products.py --file bad.json list` | Error (next_id must be greater than every ID), exit 1 | Listed normally | next_id must be above every ID, or the next add would collide |
| T91 | `echo '{"next_id": 3, "products": [{"id": 1, "name": "A", "price": "1.00", "quantity": 1}, {"id": 1, "name": "B", "price": "1.00", "quantity": 1}]}' > bad.json`, then `python3 products.py --file bad.json list` | Error (duplicate ID), exit 1 | Listed normally | IDs must be unique |
| T91b | `echo '{"next_id": 2, "products": [{"name": "A"}]}' > bad.json`, then `python3 products.py --file bad.json list` | Error (missing fields), exit 1 | A Traceback | A product with missing fields is a clean error, not a crash (regression test for an early bug) |
| T91c | `echo '{"next_id": true, "products": []}' > bad.json`, then `python3 products.py --file bad.json add --name X --price 1 --quantity 1` | Error, exit 1; bad.json unchanged | A product with `"id": true` is added | Python treats `true` as the integer 1, so it must be rejected explicitly (regression test for an early bug) |
| T91d | `echo '{"next_id": 4, "products": [{"id": 3, "name": "C", "price": "1.00", "quantity": 1}, {"id": 1, "name": "A", "price": "1.00", "quantity": 1}]}' > bad.json`, then `python3 products.py --file bad.json list` | Listed normally, **1 before 3** | 3 comes first | Products stored out of order are still listed by ID; `cat` shows the raw file order |
| T92 | `echo '{"next_id": 1, "products": []}' > locked.json`, `chmod 000 locked.json`, then `python3 products.py --file locked.json list` | Error (permission denied), exit 1. Afterwards run `chmod 644 locked.json` | — | `chmod 000` = nobody may read or write (`ls -l` shows `----------`). The content is valid; being unreadable is the only problem. The operating system enforces this, and Python cannot bypass it |
| T93 | `cp products.json ro.json`, `chmod 444 ro.json`, then `python3 products.py --file ro.json add --name A --price 1 --quantity 1` | Error (permission denied), exit 1; `cat ro.json` unchanged. Afterwards run `chmod 644 ro.json` | The add succeeded | `cp` makes a copy so the real file is safe; `chmod 444` = read-only. Readable but not writable must be an error that leaves the content alone (the tool checks write access before saving) |
| T94 | `python3 products.py --file sub list` | Error (sub is a folder), exit 1 | — | A folder used as the data file is an error |

## 9. Failed commands change nothing and use up no IDs

| ID | Steps | Expected | Bug if | What it checks |
|---|---|---|---|---|
| T95 | ① `cat products.json` and note `next_id`; `shasum products.json` and note the fingerprint ② run these failing commands: `python3 products.py add --name A --price -1 --quantity 1`, `python3 products.py update 99 --quantity 1`, `python3 products.py update 1 --price abc`, `python3 products.py delete 1`, `python3 products.py delete 99 --yes` ③ `shasum products.json` again ④ `python3 products.py add --name Check --price 1 --quantity 1` | ② every command fails ③ same fingerprint as ① ④ the new product's ID equals the next_id from ① | ③ the fingerprint changed; ④ an ID was skipped | After a run of failures the file is byte-for-byte the same and no ID was used up |

## 10. Output format

| ID | Command | Expected | Bug if | What it checks |
|---|---|---|---|---|
| T96 | `python3 products.py list \| python3 -m json.tool` | Pretty-printed JSON | `Expecting value` or a similar error: something other than JSON was printed | The pipe hands the output to `json.tool`, which only accepts pure JSON, the way an automated checker would |
| T97 | `python3 products.py get 1 \| python3 -m json.tool` | Same as T96 | Same as T96 | Same check for get |
| T98 | Look back over every test | No command ever waited for input | A command waited for input | The tool never prompts; every command finishes on its own |

## 11. Custom feature: `search`

Set up the test data first:

```bash
python3 products.py --file search.json add --name "Notebook" --price 4.50 --quantity 12
python3 products.py --file search.json add --name "Pencil" --price 1.25 --quantity 5
python3 products.py --file search.json add --name "Spiral NOTEBOOK" --price 6 --quantity 3
python3 products.py --file search.json add --name "Pen" --price 2 --quantity 10
```

| ID | Command | Expected | Bug if | What it checks |
|---|---|---|---|---|
| S01 | `python3 products.py --file search.json search --name note` | Notebook (1) and Spiral NOTEBOOK (3) | One is missing | A name that *contains* the text matches |
| S02 | `python3 products.py --file search.json search --name NOTE` | Same as S01 | Different result | Matching ignores upper and lower case |
| S03 | `python3 products.py --file search.json search --name pen` | Pencil (2) and Pen (4) | Only Pen | "Pencil" contains "pen", so both match |
| S04 | `python3 products.py --file search.json search --name "  pen  "` | Same as S03 | Nothing found | Spaces around the search text are trimmed |
| S05 | `python3 products.py --file search.json search --name xyz` | `[]`, exit 0 | An error | No match prints `[]`; it is not an error |
| S06 | `python3 products.py --file search.json search --name "."` | `[]` | Every product is listed (`.` treated as "any character") | The text is matched literally; `.` is just a dot |
| S07–08 | `python3 products.py --file search.json search --name "   "` and `python3 products.py --file search.json search --name ""` | Error, exit 2 | Every product is listed | The search text cannot be empty or only spaces (that would just list everything) |
| S09–10 | `python3 products.py --file search.json search` (no `--name`) and `python3 products.py --file search.json search --name note extra` | Error, exit 2 | — | A missing `--name` or an extra argument is a syntax error |
| S11 | `python3 products.py search --name note` (no `--file`) | Searches products.json | — | Without `--file`, the default products.json is searched |
| S12 | `python3 products.py --file new.json search --name a` | `[]`; new.json is not created | new.json was created | A missing file shows `[]` and creates nothing |
| S13 | `echo "{oops" > bad.json`, then `python3 products.py --file bad.json search --name a` | Error, exit 1 | A Traceback | A broken file is a clean error, not a crash |
| S14 | `shasum search.json` before and after a search | Same fingerprint | The search changed the file | search only reads; it never writes |
| S15–16 | `python3 products.py --help`; `python3 products.py search --help` | Help lists search; search's help describes `--name` | search is missing from help | The custom feature is documented in `--help` too |
| S17 | Run section 2 again | Everything still passes | An existing command broke | Adding search did not break the original commands |

---

## Clean up

```bash
rm -rf products.json demo.json ids.json acc.json search.json bad.json locked.json ro.json new.json "my data.json" sub
```

Afterwards the folder should contain only the files from the repository.
