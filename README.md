# MyISAM2SQL

Provides a quick Python based script that converts MySQL's MyISAM table files (`.frm`, `.MYD`, and `.MYI`) into an SQL dump. The conversion is performed using a Docker container running either MySQL or MariaDB.

## Prerequisites

- **Python 3.6+**  
- **Docker Desktop:**  
  Ensure Docker is installed and running. Switch to Linux containers if required.
- **sqlparse (Optional):**  
  For pretty printing, install sqlparse:
  ```bash
  pip install sqlparse
  ```

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/mq1n/MyISAM2SQL.git
   cd MyISAM2SQL
   ```

2. **(Optional) Set Up a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use venv\Scripts\activate
   ```

3. **Install Required Python Packages:**
   ```bash
   pip install sqlparse
   ```

## Usage

Run the script from the command line with the required arguments:

```bash
python MyISAM2SQL.py --source <source_directory> --output <output_file> [options]
```

### Arguments

- `--source`: **(Required)** Path to the database directory containing your MyISAM files (e.g., `/path/to/mydatabase`).
- `--output`: **(Required)** Path to the output SQL file (e.g., `dump.sql`).
- `--database`: Optional database name. If omitted, the script uses the basename of the source directory.
- `--engine`: Database engine to use. Choose between `mysql` or `mariadb`. Default is `mysql`.
- `--version`: Database server version to use. For MySQL, e.g., `5.7`, `8.0`; for MariaDB, e.g., `10.5`. Default is `5.7`.
- `--password`: Root password for the database server (default is `password`).
- `--wait-time`: Seconds to wait for the container to initialize (default is `20`).
- `--pretty`: If set, the SQL dump will be formatted for readability using sqlparse.

## Troubleshooting

- **Docker Connection Issues:** If you see errors related to Docker connectivity (e.g., "docker: error during connect..."), ensure that Docker Desktop is installed, running, and configured to use Linux containers.
- **SQL Formatting Issues:** If you enable the `--pretty` flag but the formatting doesn't work as expected:
  - Make sure you're using the latest version of `sqlparse`:
    ```bash
    pip install --upgrade sqlparse
    ```
  - Consider tweaking the formatting options in the script.
  - For complex dumps, you may need a custom post-processing solution.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Contributions are welcome! Please open issues or pull requests for any bugs or enhancements.
