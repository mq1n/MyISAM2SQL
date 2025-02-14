#!/usr/bin/env python3
import argparse
import os
import subprocess
import time
import tempfile
import shutil
import uuid
import sys

try:
	import sqlparse
except ImportError:
	os.system('python -m pip install sqlparse')
	import sqlparse

def exec_cmd(command, capture_output=False, check=True):
	print(f"Running command: {' '.join(command)}")
 
	result = subprocess.run(command, capture_output=capture_output, text=True)
	if check and result.returncode != 0:
		print(f"Command failed with code {result.returncode}.")
		if result.stderr:
			print("Error output:", result.stderr)
		sys.exit(1)
  
	return result

def main(*args):
	parser = argparse.ArgumentParser(
		description=(
			"Convert MyISAM files (.frm, .MYD, .MYI) to an SQL dump using Docker. "
			"Supports MySQL (including 8) and MariaDB. Optionally pretty prints the SQL dump."
		)
	)
	parser.add_argument(
		"--source",
		required=True,
		help=(
			"Path to the database directory containing your MyISAM files. "
			"For example, if your table files are in '/path/to/mydatabase', "
			"then --source should point to that directory."
		),
	)
	parser.add_argument(
		"--database",
		help=(
			"Database name. If not provided, the script uses the basename of the source directory."
		),
	)
	parser.add_argument(
		"--output",
		required=True,
		help="Path to the output SQL file that will be created.",
	)
	parser.add_argument(
		"--engine",
		choices=["mysql", "mariadb"],
		default="mysql",
		help="Database engine to use: 'mysql' or 'mariadb'. Default is mysql.",
	)
	parser.add_argument(
		"--version",
		default="5.7",
		help=(
			"Database server version to use. For MySQL, you can specify '5.7', '8.0', etc. "
			"For MariaDB, specify the version accordingly (e.g., '10.5'). Default is 5.7."
		),
	)
	parser.add_argument(
		"--password",
		default="password",
		help="Root password for the database server (default: password).",
	)
	parser.add_argument(
		"--wait-time",
		type=int,
		default=20,
		help="Seconds to wait for the database container to initialize (default: 20).",
	)
	parser.add_argument(
		"--pretty",
		action="store_true",
		help="If set, the SQL dump will be formatted for readability using sqlparse.",
	)
	args = parser.parse_args()

	# Resolve and verify the source directory
	source_dir = os.path.abspath(args.source)
	if not os.path.isdir(source_dir):
		print("Error: Source directory does not exist or is not a directory.")
		return 1

	# Determine the database name (default to source directory's basename)
	database_name = args.database if args.database else os.path.basename(source_dir.rstrip("/"))
	output_file = os.path.abspath(args.output)

	# Create a temporary directory for the database data
	temp_data_dir = tempfile.mkdtemp(prefix="db_data_")
	print(f"Created temporary data directory: {temp_data_dir}")

	dest_dir = os.path.join(temp_data_dir, database_name)
	try:
		shutil.copytree(source_dir, dest_dir)
		print(f"Copied source database '{database_name}' into temporary data directory.")
	except Exception as e:
		print("Error copying source directory:", e)
		shutil.rmtree(temp_data_dir)
		return 1

	# Generate a unique container name
	container_name = f"db_converter_{uuid.uuid4().hex[:8]}"
	print(f"Using Docker container name: {container_name}")

	# Determine the Docker image based on engine and version
	if args.engine == "mysql":
		docker_image = f"mysql:{args.version}"
	elif args.engine == "mariadb":
		docker_image = f"mariadb:{args.version}"
	else:
		print("Unsupported engine.")
		shutil.rmtree(temp_data_dir)
		return 1

	# Run the Docker container with the temporary data directory mounted
	run_cmd = [
		"docker",
		"run",
		"--name",
		container_name,
		"-e",
		f"MYSQL_ROOT_PASSWORD={args.password}",
		"-v",
		f"{temp_data_dir}:/var/lib/mysql",
		"-d",
		docker_image,
	]
	try:
		exec_cmd(run_cmd)
	except Exception as e:
		print("Error starting Docker container:", e)
		shutil.rmtree(temp_data_dir)
		return 1

	# Wait for the database server to initialize
	print("Waiting for the database server to initialize...")
	time.sleep(args.wait_time)

	# Run mysqldump inside the container to create an SQL dump
	dump_cmd = [
		"docker",
		"exec",
		container_name,
		"mysqldump",
		"-u",
		"root",
		f"-p{args.password}",
		database_name,
	]
	try:
		result = exec_cmd(dump_cmd, capture_output=True)
	except Exception as e:
		print("Error running mysqldump:", e)
		subprocess.run(["docker", "stop", container_name])
		subprocess.run(["docker", "rm", container_name])
		shutil.rmtree(temp_data_dir)
		return 1

	dump_output = result.stdout

	# Format the SQL dump
	if args.pretty:
		try:
			dump_output = sqlparse.format(
				dump_output,
				reindent=True,
				keyword_case='upper',
				indent_width=2,
				strip_comments=False
			)
			print("SQL dump has been formatted for readability.")
		except Exception as e:
			print("Error during SQL formatting:", e)
	
	# Write the dump to the output SQL file
	try:
		with open(output_file, "w", encoding="utf-8") as f:
			f.write(dump_output)
		print(f"SQL dump successfully written to {output_file}")
	except Exception as e:
		print("Error writing output file:", e)

	# Clean up; stop and remove the container, then remove the temporary data directory
	exec_cmd(["docker", "stop", container_name])
	exec_cmd(["docker", "rm", container_name])
 
	shutil.rmtree(temp_data_dir)
 
	print("Cleaned up Docker container and temporary resources.")
	return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
