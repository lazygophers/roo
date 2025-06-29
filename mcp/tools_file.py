import os
import shutil

from croe import mcp


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
	name="file_ln",
	title="Create a symbolic link",
	description="Create a symbolic link",
)
async def ln(src: str, dest: str) -> bool:
	os.symlink(src, dest)
	return True


@mcp.tool(
	name="file_mv",
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
	name="file_cp",
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
	name="file_edit",
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
	name="file_append",
	title="Append content to a file",
	description="Append content to a file",
)
async def append_file(path: str, content: str) -> bool:
	with open(path, 'a', encoding='utf8') as f:
		f.write(content)
	return True