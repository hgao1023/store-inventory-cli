#!/usr/bin/env python3
"""products.py - a command-line inventory tool for a small store.

Product records are saved in a local JSON file (products.json by default).
Each run performs exactly one command and exits; it never asks for input.

Usage:
    python3 products.py [--file PATH] COMMAND [OPTIONS]
"""

import argparse
import json
import os
import re
import sys
import tempfile

DEFAULT_FILE = "products.json"

# Exit codes used by this tool.
EXIT_OK = 0
EXIT_DATA_ERROR = 1   # product not found, invalid stored data, file read/write failure
EXIT_USAGE_ERROR = 2  # invalid syntax, missing arguments, invalid input values (argparse uses 2 too)

# [0-9] instead of \d so that only plain ASCII digits are accepted.
PRICE_PATTERN = re.compile(r"[0-9]+(\.[0-9]{1,2})?")
STORED_PRICE_PATTERN = re.compile(r"[0-9]+\.[0-9]{2}")
INTEGER_PATTERN = re.compile(r"[0-9]+")

STORE_KEYS = {"next_id", "products"}
PRODUCT_KEYS = {"id", "name", "price", "quantity"}


class CLIError(Exception):
    """An expected failure: main() prints the message to stderr and exits with exit_code."""

    def __init__(self, message, exit_code=EXIT_DATA_ERROR):
        super().__init__(message)
        self.exit_code = exit_code


# ---------- Checking values typed on the command line ----------
# argparse passes the raw text of an argument to its "type" function.
# Raising ArgumentTypeError makes argparse print the message and exit with
# code 2, before the data file is ever opened.

def parse_name(text):
    name = text.strip()
    if not name:
        raise argparse.ArgumentTypeError("name must contain at least one non-whitespace character")
    return name


def parse_price(text):
    """Accept 0, 4.5 or 4.50 and return the price as a string with two decimals, e.g. "4.50"."""
    if not PRICE_PATTERN.fullmatch(text):
        raise argparse.ArgumentTypeError(
            f"invalid price {text!r}: use digits with up to two decimal places, e.g. 4.50"
        )
    whole, _, cents = text.partition(".")
    whole = whole.lstrip("0") or "0"
    return f"{whole}.{cents.ljust(2, '0')}"


def parse_quantity(text):
    if not INTEGER_PATTERN.fullmatch(text):
        raise argparse.ArgumentTypeError(
            f"invalid quantity {text!r}: must be a whole number, 0 or greater"
        )
    return int(text)


def parse_id(text):
    if not INTEGER_PATTERN.fullmatch(text) or int(text) == 0:
        raise argparse.ArgumentTypeError(f"invalid ID {text!r}: must be a positive integer")
    return int(text)


# ---------- Reading and writing the data file ----------

def empty_store():
    return {"next_id": 1, "products": []}


def load_store(path):
    """Read the store from path. A missing file counts as an empty store."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return empty_store()
    except UnicodeDecodeError:
        raise CLIError(f"data file {path} is not valid UTF-8")
    except OSError as e:
        raise CLIError(f"cannot read data file {path}: {e.strerror}")

    if not text.strip():
        raise CLIError(f"data file {path} is empty")
    try:
        store = json.loads(text)
    except json.JSONDecodeError as e:
        raise CLIError(f"data file {path} is not valid JSON ({e.msg} at line {e.lineno})")

    check_store(store, path)
    return store


def is_int(value):
    """True for real integers. bool is excluded because Python counts True/False as ints."""
    return isinstance(value, int) and not isinstance(value, bool)


def check_store(store, path):
    """Raise CLIError unless the data follows every rule for next_id and the products."""
    def invalid(reason):
        raise CLIError(f"data file {path} has invalid data: {reason}")

    if not isinstance(store, dict) or set(store) != STORE_KEYS:
        invalid("expected an object with exactly the keys next_id and products")
    next_id = store["next_id"]
    if not is_int(next_id) or next_id < 1:
        invalid("next_id must be a positive integer")
    if not isinstance(store["products"], list):
        invalid("products must be a list")

    seen_ids = set()
    for product in store["products"]:
        if not isinstance(product, dict) or set(product) != PRODUCT_KEYS:
            invalid("each product must have exactly id, name, price and quantity")
        product_id = product["id"]
        if not is_int(product_id) or product_id < 1:
            invalid("product id must be a positive integer")
        if product_id in seen_ids:
            invalid(f"product id {product_id} appears more than once")
        if product_id >= next_id:
            invalid(f"next_id must be greater than product id {product_id}")
        seen_ids.add(product_id)

        name = product["name"]
        if not isinstance(name, str) or not name.strip() or name != name.strip():
            invalid(f"product {product_id} must have a trimmed, non-empty name")
        price = product["price"]
        if not isinstance(price, str) or not STORED_PRICE_PATTERN.fullmatch(price):
            invalid(f'product {product_id} must have a price string like "4.50"')
        quantity = product["quantity"]
        if not is_int(quantity) or quantity < 0:
            invalid(f"product {product_id} must have a whole-number quantity, 0 or greater")


def save_store(path, store):
    """Write the store without ever leaving a half-written data file.

    The JSON goes into a temporary file in the same folder first. Only when that
    succeeds does os.replace swap it in for the real file, so a failure part-way
    through leaves the original file exactly as it was.
    """
    if os.path.exists(path) and not os.access(path, os.W_OK):
        raise CLIError(f"cannot write data file {path}: permission denied")
    folder = os.path.dirname(os.path.abspath(path))
    temp_path = None
    try:
        fd, temp_path = tempfile.mkstemp(dir=folder, prefix=".products-", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2, ensure_ascii=False)
            f.write("\n")
        # mkstemp makes the file private (rw-------); give it normal file permissions.
        os.chmod(temp_path, 0o644)
        os.replace(temp_path, path)
        temp_path = None
    except OSError as e:
        raise CLIError(f"cannot write data file {path}: {e.strerror or e}")
    finally:
        if temp_path is not None:
            try:
                os.remove(temp_path)
            except OSError:
                pass


# ---------- Commands ----------
# Each command returns its result; main() prints it as JSON.

def find_product(store, product_id):
    for product in store["products"]:
        if product["id"] == product_id:
            return product
    raise CLIError(f"product with ID {product_id} not found")


def cmd_add(args):
    store = load_store(args.file)
    product = {
        "id": store["next_id"],
        "name": args.name,
        "price": args.price,
        "quantity": args.quantity,
    }
    store["products"].append(product)
    store["next_id"] += 1
    save_store(args.file, store)
    return product


def cmd_list(args):
    store = load_store(args.file)
    return sorted(store["products"], key=lambda product: product["id"])


def cmd_get(args):
    store = load_store(args.file)
    return find_product(store, args.id)


def cmd_update(args):
    # The supplied values were already checked by argparse, so nothing invalid can reach the file.
    changes = {field: getattr(args, field)
               for field in ("name", "price", "quantity")
               if getattr(args, field) is not None}
    if not changes:
        raise CLIError("update needs at least one of --name, --price or --quantity", EXIT_USAGE_ERROR)
    store = load_store(args.file)
    product = find_product(store, args.id)
    product.update(changes)   # fields not supplied, and the id, stay as they were
    save_store(args.file, store)
    return product


def cmd_delete(args):
    if not args.yes:
        raise CLIError("delete needs --yes to confirm", EXIT_USAGE_ERROR)
    store = load_store(args.file)
    product = find_product(store, args.id)
    store["products"].remove(product)   # next_id is left alone, so the id is never reused
    save_store(args.file, store)
    return {"deleted_id": product["id"]}


def cmd_search(args):
    """Custom feature: find products whose name contains the search text, ignoring case."""
    text = args.name.casefold()
    store = load_store(args.file)
    # Plain substring test ("in"), so characters like "." or "*" have no special meaning.
    matches = [product for product in store["products"] if text in product["name"].casefold()]
    return sorted(matches, key=lambda product: product["id"])


# ---------- Command-line interface ----------

def build_parser():
    parser = argparse.ArgumentParser(
        prog="products.py",
        description="Manage a small store's product inventory saved in a local JSON file.",
        epilog='example: python3 products.py add --name "Notebook" --price 4.50 --quantity 10',
        allow_abbrev=False,
    )
    parser.add_argument(
        "--file",
        default=DEFAULT_FILE,
        metavar="PATH",
        help=f"JSON data file to use (default: {DEFAULT_FILE} in the current directory); "
             "must come before COMMAND",
    )
    commands = parser.add_subparsers(dest="command", metavar="COMMAND", required=True)

    add = commands.add_parser(
        "add",
        help="create a product and print it",
        description="Create one product. The ID is assigned automatically.",
        allow_abbrev=False,
    )
    add.add_argument("--name", required=True, type=parse_name,
                     help="product name (leading and trailing spaces are trimmed)")
    add.add_argument("--price", required=True, type=parse_price,
                     help="price such as 4, 4.5 or 4.50 (no signs, currency symbols or exponents)")
    add.add_argument("--quantity", required=True, type=parse_quantity, metavar="QTY",
                     help="whole number, 0 or greater")
    add.set_defaults(handler=cmd_add)

    list_cmd = commands.add_parser(
        "list",
        help="print all products sorted by ID",
        description="Print a JSON array of all products sorted by ID ([] when there are none).",
        allow_abbrev=False,
    )
    list_cmd.set_defaults(handler=cmd_list)

    get = commands.add_parser(
        "get",
        help="print one product by ID",
        description="Print the product with the given ID.",
        allow_abbrev=False,
    )
    get.add_argument("id", type=parse_id, metavar="ID", help="positive integer product ID")
    get.set_defaults(handler=cmd_get)

    update = commands.add_parser(
        "update",
        help="change some fields of a product and print it",
        description="Change only the supplied fields of a product. At least one field flag is required.",
        allow_abbrev=False,
    )
    update.add_argument("id", type=parse_id, metavar="ID", help="positive integer product ID")
    update.add_argument("--name", type=parse_name, help="new product name")
    update.add_argument("--price", type=parse_price, help="new price such as 4, 4.5 or 4.50")
    update.add_argument("--quantity", type=parse_quantity, metavar="QTY",
                        help="new quantity, a whole number 0 or greater")
    update.set_defaults(handler=cmd_update)

    delete = commands.add_parser(
        "delete",
        help="remove a product (requires --yes)",
        description="Remove the product with the given ID. --yes is required; there is no prompt.",
        allow_abbrev=False,
    )
    delete.add_argument("id", type=parse_id, metavar="ID", help="positive integer product ID")
    delete.add_argument("--yes", action="store_true", help="confirm the deletion (required)")
    delete.set_defaults(handler=cmd_delete)

    search = commands.add_parser(
        "search",
        help="find products by part of their name (custom feature)",
        description="Print a JSON array of products whose name contains TEXT, ignoring case, "
                    "sorted by ID ([] when nothing matches).",
        epilog="example: python3 products.py search --name note",
        allow_abbrev=False,
    )
    search.add_argument("--name", required=True, type=parse_name, metavar="TEXT",
                        help="part of a product name; leading and trailing spaces are ignored")
    search.set_defaults(handler=cmd_search)

    return parser


def main(argv=None):
    parser = build_parser()
    # parse_args exits by itself: code 0 after --help, code 2 for bad syntax or values.
    args = parser.parse_args(argv)
    try:
        result = args.handler(args)
    except CLIError as e:
        print(f"error: {e}", file=sys.stderr)
        return e.exit_code
    except Exception as e:
        # Safety net: even an unexpected problem gets one line on stderr, never a traceback.
        print(f"error: unexpected problem: {e}", file=sys.stderr)
        return EXIT_DATA_ERROR
    print(json.dumps(result, indent=2))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
