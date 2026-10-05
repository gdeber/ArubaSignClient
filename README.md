# Aruba Sign CLI

CLI for sending a PDF to the Aruba remote signing service and downloading the signed result.

## What it does

- Uploads a PDF to the Aruba signing portal
- Retrieves the remote certificate alias for the configured user
- Submits the OTP/password flow required by Aruba
- Downloads the signed ZIP archive and extracts the final file in the chosen output directory

## Requirements

- Python 3.11+
- Internet access to the Aruba signing endpoints
- Valid Aruba remote-signature credentials

## Installation

Create a virtual environment and install the project in editable mode:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

You can also run the project without installing it by using the local script directly:

```bash
./aruba_sign_cli path/to/file.pdf --user YOUR_USER --password YOUR_PASSWORD --otp YOUR_OTP
```

## Usage

```bash
./aruba_sign_cli FILE.pdf --user USER --password PASSWORD --otp OTP
```

Optional arguments:

- `-u`, `--user`: Aruba remote-signature username or fiscal code
- `-p`, `--password`: Aruba remote-signature password
- `-o`, `--otp`: OTP code from the app or SMS flow
- `-out`, `--output-dir`: destination folder for the signed file

If `--output-dir` is not specified, the output directory defaults to the folder containing the input PDF.

## Example

```bash
./aruba_sign_cli /tmp/document.pdf \
  --user mario.rossi \
  --password 'secret' \
  --otp 123456 \
  --output-dir ./signed
```

The script prints progress information while it initializes the session, uploads the document, signs it, and downloads the result.
