# Information Retrieval – Text Preprocessing

A Python implementation of a text preprocessing pipeline for Information Retrieval.

This project demonstrates how raw text can be processed into normalized terms using several fundamental Natural Language Processing techniques.

## Features

- Tokenization using regular expressions
- Lowercase normalization
- Abbreviation normalization (e.g. `U.S.A.` → `usa`)
- Possessive suffix removal
- Stop-word removal
- Porter Stemming algorithm (implemented from scratch)
- Precision and Recall evaluation against predefined gold-standard outputs
- JSON output generation
- Command-line interface using `argparse`

## Project Structure

```text
information-retrieval-text-preprocessing/
│
├── text_preprocessor.py
├── README.md
└── .gitignore
```

## Requirements

- Python 3.10 or higher
- No external dependencies

## Usage

### 1. Process built-in sample texts

```bash
python text_preprocessor.py
```

This processes three predefined sample texts and evaluates the results using Precision and Recall.

### 2. Process custom text

```bash
python text_preprocessor.py --text "Information Retrieval is an interesting field."
```

### 3. Process a text file

```bash
python text_preprocessor.py --file input.txt
```

### 4. Specify output filename

```bash
python text_preprocessor.py --text "Hello world" --out result.json
```

The default output filename is `outputs.json`.

## Evaluation

The project evaluates preprocessing results using:

- **Precision:** The proportion of produced terms that match the gold-standard terms.
- **Recall:** The proportion of gold-standard terms that appear in the produced output.

Evaluation is performed using predefined sample texts and their corresponding gold-standard outputs.

## Technologies

- Python
- Regular Expressions (`re`)
- Argument Parsing (`argparse`)
- JSON
- Porter Stemming

## Author
 
Ariana Ghanbarpour