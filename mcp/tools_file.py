import os
import shutil
from pydantic import BaseModel, Field
from croe import mcp


class FileInfo(BaseModel):
	path: str = Field(..., description="The path to the file")
	size: int = Field(..., description="The size of the file")
	is_dir: bool = Field(..., description="Whether the file is a directory")

	mode: int = Field(..., description="The mode of the file")
	created_at: int = Field(..., description="The created at timestamp of the file")
	modified_at: int = Field(..., description="The modified at timestamp of the file")


@mcp.tool(
	name="read_file",
	title="Read a file",
	description="Read a file from a file",
)
async def read_file(file_path: str) -> str:
	with open(file_path, "r") as f:
		return f.read()


@mcp.tool(
	name="write_file",
	title="Write a file",
	description="Write a file to a file",
)
async def write_file(file_path: str, content: str) -> bool:
	with open(file_path, "w") as f:
		f.write(content)
	return True


@mcp.tool(
	name="delete_file",
	title="Delete a file",
	description="Delete a file",
)
async def delete_file(file_path: str) -> bool:
	try:
		os.remove(file_path)
	except FileNotFoundError:
		return False
	return True


@mcp.tool(
	name="mkdir",
	title="Create a directory",
	description="Create a directory",
)
async def mkdir(dir_path: str) -> bool:
	os.mkdir(dir_path)
	return True


@mcp.tool(
	name="rmdir",
	title="Remove a directory",
	description="Remove a directory",
)
async def rmdir(dir_path: str) -> bool:
	os.rmdir(dir_path)
	return True


@mcp.tool(
	name="file_exists",
	title="Check if a file exists",
	description="Check if a file exists",
)
async def file_exists(path: str) -> bool:
	return os.path.exists(path)


@mcp.tool(
	name="file_is_dir",
	title="Check if a path is a directory",
	description="Check if a path is a directory",
)
async def file_is_dir(path: str) -> bool:
	return os.path.isdir(path)


@mcp.tool(
	name="file_is_file",
	title="Check if a path is a file",
	description="Check if a path is a file",
)
async def file_is_file(path: str) -> bool:
	return os.path.isfile(path)


@mcp.tool(
	name="ln",
	title="Create a symbolic link",
	description="Create a symbolic link",
)
async def ln(src: str, dest: str) -> bool:
	os.symlink(src, dest)
	return True


@mcp.tool(
	name="mv",
	title="Move a file or directory",
	description="Move a file or directory",
)
async def mv(src: str, dest: str) -> bool:
	try:
		os.rename(src, dest)
		return True
	except Exception as e:
		print(e)
		return False


@mcp.tool(
	name="cp",
	title="Copy a file or directory",
	description="Copy a file or directory",
)
async def copy(src: str, dest: str) -> bool:
	try:
		shutil.copytree(src, dest)
	except FileNotFoundError:
		shutil.copy(src, dest)
	return True


@mcp.tool(
	name="edit_file",
	title="Edit a file",
	description="Edit a file",
)
async def edit_file(path: str, line_range: str = None) -> bool:
	with open(path, "r") as f:
		lines = f.readlines()
	if line_range:
		start, end = line_range.split("-")
		lines = lines[int(start):int(end)]
	with open(path, "w") as f:
		f.writelines(lines)
	return True


@mcp.tool(
	name="append_file",
	title="Append content to a file",
	description="Append content to a file",
)
async def append_file(path: str, content: str) -> bool:
	with open(path, 'a', encoding='utf8') as f:
		f.write(content)
	return True


@mcp.tool(
	name="list_files",
	title="List files in a directory",
	description="List files in a directory",
)
async def list_files(path: str, recursive: bool = False) -> list[FileInfo]:
	files = []

	for file in os.listdir(path):
		files.append(await file_info(os.path.join(path, file)))

		if os.path.isfile(os.path.join(path, file)):
			continue
		if not recursive:
			continue

		files.extend(await list_files(os.path.join(path, file), True))

	return files


@mcp.tool(
	name="file_info",
	title="File Info",
	description="Get information about a file",
)
async def file_info(path: str) -> FileInfo:
	return FileInfo(
		path=path,
		size=os.path.getsize(path),
		is_dir=os.path.isdir(path),
		mode=os.stat(path).st_mode,
		created_at=int(os.path.getctime(path)),
		modified_at=int(os.path.getmtime(path)),
	)