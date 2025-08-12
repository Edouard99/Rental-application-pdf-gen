# PDF Watermarking and Document Combination Tool

This tool automatically watermarks PDF files from multiple folders (representing different people) and combines them into a single master document with a title page, table of contents, bookmarks, and separator pages for easy navigation.

## Features

- 🔒 **Watermarking**: Adds customizable watermarks to all PDF files
- 📑 **Smart Combination**: Combines all PDFs into a single document
- 📋 **Table of Contents**: Auto-generated with clickable links
- 🔖 **Bookmarks (Signets)**: PDF bookmarks for easy navigation
- 🏷️ **Separator Pages**: Clean separation between different people's documents
- ⚙️ **Configuration**: Optional JSON configuration for custom ordering and aliases
- 🔄 **Automatic Scaling**: Watermark text auto-scales to fit page width

## Installation

### Windows (PowerShell)
```powershell
.\setup_environment.ps1
```

### Windows (Command Prompt)
```cmd
setup_environment.bat
```

### Linux/macOS (Bash)
```bash
./setup_environment.sh
```

These scripts will:
1. Create a Python virtual environment
2. Install required dependencies (reportlab, PyPDF2, PyCryptodome)
3. Set up the environment for immediate use

## Input Folder Structure

Create your input folder with the following structure:

```
YourInputFolder/
├── Person1/
│   ├── Document1.pdf
│   ├── Document2.pdf
│   └── ...
├── Person2/
│   ├── Document1.pdf
│   ├── Document2.pdf
│   └── ...
├── Person3/
│   └── ...
└── generation.json (optional)
```

### Important Notes:
- Each subfolder represents one person
- PDF files should follow the naming convention: `DocumentType-OtherInfo.pdf`
- The part before the first `-` will be used as the document name in the table of contents
- Underscores (`_`) in document names will be replaced with spaces

### Document Naming Examples:
- `CNI-John.pdf` → "CNI"
- `RIB-BankAccount.pdf` → "RIB"
- `Contract_Work-2024.pdf` → "Contract Work"

## Optional Configuration (generation.json)

Create a `generation.json` file in your input folder to customize:

```json
{
    "Person1": {
        "alias": "John DOE",
        "order": 1
    },
    "Person2": {
        "alias": "Jane SMITH", 
        "order": 2
    },
    "Person3": {
        "alias": "Bob JOHNSON",
        "order": 3
    }
}
```

### Configuration Options:
- **`alias`**: Display name for the person (shown in table of contents and bookmarks)
- **`order`**: Processing order (lower numbers = processed first)

Without configuration, folders are processed in alphabetical order using folder names.

## Usage

### Basic Usage
```bash
python generate_loc_file.py -s ./InputFolder
```

### With Custom Watermark
```bash
python generate_loc_file.py -s ./InputFolder -w "CONFIDENTIAL - RENTAL APPLICATION"
```

### With Custom Title
```bash
python generate_loc_file.py -s ./InputFolder -t "Smith Family Rental Documents"
```

### Complete Example
```bash
python generate_loc_file.py -s ./RentalDocs -w "RESERVED FOR APARTMENT RENTAL" -t "Complete Rental Application - Smith Family"
```

### Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--source` | `-s` | Input folder path | **Required** |
| `--watermark` | `-w` | Watermark text | "RESERVED FOR APARTMENT RENTAL" |
| `--title` | `-t` | Document title | "Rental Application" |

## Output

The tool generates a single PDF file named after your title (e.g., `Smith_Family_Rental_Documents.pdf`) containing:

1. **Title Page** - Shows document title and generation date
2. **Table of Contents** - Clickable links to all sections
3. **Separator Pages** - One per person with "PersonName - Documents"
4. **Documents** - All watermarked PDFs organized by person (alphabetically within each person)

### Navigation Features:
- **Clickable TOC**: Click any entry to jump to that page
- **PDF Bookmarks**: Use your PDF viewer's bookmark panel
- **Separator Pages**: Visual breaks between different people's documents

## Troubleshooting

### Common Issues:

1. **"No PDF files found"**
   - Check that PDF files are in subfolders, not the root input folder
   - Ensure files have `.pdf` extension

2. **"PyCryptodome required"**
   - Some encrypted PDFs need additional decryption
   - Try with unencrypted versions of the PDFs

3. **Watermark text too large**
   - The tool automatically scales down font size
   - Very long text may be truncated with "..."

4. **Wrong processing order**
   - Check your `generation.json` file syntax
   - Ensure folder names match exactly (case-sensitive)

### Excluded Folders:
The following folders are automatically excluded from processing:
- `Dossier Location`
- `protected_files`
- `temp_watermarked`

## Requirements

- Python 3.7+
- reportlab
- PyPDF2
- PyCryptodome

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

