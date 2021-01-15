import os
import setuptools


def package_files(directory):
    paths = []
    for (path, _, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join("..", path, filename))
    return paths


setuptools.setup(
    name="argflow-ui",
    version="0.1",
    description="Web portal for visualising Argflow explanations",
    url="https://clarg.doc.ic.ac.uk/",
    author="Adam, Bogdan, Edi, Hasan, Peter, Pranav",
    author_email="ham418@ic.ac.uk",
    license="MIT",
    packages=setuptools.find_packages(),
    scripts=["scripts/argflow-ui"],
    package_data={"argflow_ui": package_files("argflow_ui/client") + ["visualisers/js/*.js"]},
    install_requires=[
        "aiofiles>=0.5",
        "gunicorn>=20.0",
        "pyaml>=20.4",
        "requests>=2.24",
        "starlette>=0.13",
        "uvicorn[standard]>=0.12",
        "watchgod>=0.6",
    ],
)
