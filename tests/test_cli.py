from maclinux.cli import build_parser


def test_parser_has_plan_command():
    parser = build_parser()
    args = parser.parse_args(["plan"])
    assert args.command == "plan"


def test_parser_has_inventory_command():
    parser = build_parser()
    args = parser.parse_args(["inventory"])
    assert args.command == "inventory"


def test_parser_has_resolve_command():
    parser = build_parser()
    args = parser.parse_args(["resolve"])
    assert args.command == "resolve"
