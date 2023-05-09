import argparse
import export
import import_dashboard


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "mode",
        metavar="export/import",
        type=str,
        help="export or import",
    )
    args = parser.parse_args()

    if args.mode == "export":
        export.export()
    elif args.mode == "import":
        import_dashboard.import_dashboard()
    else:
        print("Invalid mode")


if __name__ == "__main__":
    main()
