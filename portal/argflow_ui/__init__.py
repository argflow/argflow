from argflow_ui.visualisers import ConversationVisualiser
from argflow.portal import ExplanationGenerator
from argflow_ui.app import ArgflowUI


def main():
    import importlib.util
    import inspect
    import os
    import sys

    from argparse import ArgumentParser
    from argflow_ui.visualisers import GraphVisualiser

    parser = ArgumentParser()

    parser.add_argument(
        "dir",
        nargs="?",
        default=None,
        help="directory to search for explanation graphs and other resource files",
    )

    parser.add_argument(
        "--no-launch", action="store_true", help="suppress launching web browser on startup"
    )

    parser.add_argument("--hub-url", help="url of the model hub")

    parser.add_argument(
        "--generator",
        nargs="+",
        help="path to a custom explanation generator",
    )

    args = parser.parse_args()

    resource_path = args.dir if args.dir else os.getenv("ARGFLOW_RESOURCE_PATH")
    hub_url = args.hub_url if args.hub_url else os.getenv("ARGFLOW_HUB_URL")

    if resource_path is not None:
        resource_path = os.path.abspath(resource_path)

    if resource_path and not os.path.isdir(resource_path):
        print(f"Not a directory: {args.dir}", file=sys.stderr)
        sys.exit(1)

    app = ArgflowUI(resource_path=resource_path, hub_url=hub_url)

    if args.generator:
        for generator in args.generator:
            spec = importlib.util.spec_from_file_location("argflow.custom_generator", generator)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            warn = True

            for name, cls in inspect.getmembers(mod, inspect.isclass):
                if cls.__module__ == "argflow.custom_generator" and issubclass(
                    cls, ExplanationGenerator
                ):
                    app.add_explanation_generator(generator, name)
                    warn = False

            if warn:
                print(
                    f"Warning: No generators found at {generator}. Generators must inherit \
    from argflow_ui.generator.ExplanationGenerator"
                )

    app.register_visualiser(GraphVisualiser())
    app.register_visualiser(ConversationVisualiser())

    app.run(launch_browser=not args.no_launch)
