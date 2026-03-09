# Address Parser & Data Cleaner

A high-performance Python tool designed to automate the cleaning, standardizing, and parsing of messy address data. This tool is specifically optimized for Indonesian address formats, housing complexes, and regional structures.

## 🚀 Key Features
* **Smart RT/RW Logic**: Intelligently distinguishes between administrative slashes (e.g., `RT 05/01` → `RT 05 RW 01`) and housing block slashes (e.g., `C6/12` → `C6 Nomor 12`).
* **Backward-Priority Extraction**: Prevents false-positive region detection by searching from the end of the string.
* **Entity Sanitization**: Automatically removes identified cities/provinces from the street address to eliminate redundancy.
* **Technical Term Recovery**: Ensures terms like `RT`, `RW`, `SR`, and Roman numerals remain correctly capitalized.
* **Professional Progress UI**: Integrated with `tqdm` for real-time processing feedback.