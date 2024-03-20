import argparse
import asyncio
import logging
from aiopath import AsyncPath
from aioshutil import copyfile


parser = argparse.ArgumentParser(description="Sorting files")
parser.add_argument("--source", "-s", required=True, help="Source dir")
parser.add_argument("--output", "-o", help="Output dir", default="destination")
args = vars(parser.parse_args())

source = AsyncPath(args["source"])
output = AsyncPath(args["output"])


# Asynchronously sorts files in the source directory into subdirectories in the output directory based on file extensions.
async def sort_files(source: AsyncPath, output: AsyncPath):
    # Iterate through each item in the source directory.
    async for file in source.iterdir():
        if await file.is_dir():
            # If the item is a directory, recurse into it to sort its files.
            await sort_files(file, output)
        else:
            # If the item is a file, copy it to the appropriate subdirectory in the output directory.
            await copy_file(file, output)


# Asynchronously copies a file to the appropriate subdirectory in the output directory based on its extension.
async def copy_file(file: AsyncPath, output: AsyncPath):
    # Determine the subdirectory name based on the file extension (excluding the dot).
    folder = output / file.suffix[1:]
    try:
        # Ensure the subdirectory exists (create it if not).
        await folder.mkdir(exist_ok=True, parents=True)
        # Copy the file to the subdirectory.
        await copyfile(file, folder / file.name)
    except OSError as e:
        # Log any errors that occur during the file copy operation.
        logging.error(f"Error copying file {file}: {e}")


if __name__ == "__main__":
    format = "%(threadName)s %(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    # Run the asynchronous sort_files function to start sorting files.
    asyncio.run(sort_files(source, output))

    # Log a message once all files have been sorted.
    logging.info(f"All files have been sorted into {output}.")
