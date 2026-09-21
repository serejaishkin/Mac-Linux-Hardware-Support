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


def test_parser_has_package_command():
    parser = build_parser()
    args = parser.parse_args(["package", "facetimehd", "--version", "1.0.0", "--source-sha256", "abc"])
    assert args.command == "package"
    assert args.driver == "facetimehd"
    assert args.source_sha256 == "abc"
