# LIOS Test Suite

Automated unit and integration tests for the **Linux-Intelligent-OCR-Solution (LIOS)** backend.

---

## Quick Start

```bash
# 1. Create the virtual environment (one-time)
python3 -m venv ~/.venvs/lios_tests
~/.venvs/lios_tests/bin/pip install pytest pytest-cov Pillow pyenchant

# 2. Run all tests from the project root
cd /path/to/lios
PYTHONPATH=. ~/.venvs/lios_tests/bin/python -m pytest Tests/
```

---

## How to Run

### All tests (with coverage)
```bash
PYTHONPATH=. ~/.venvs/lios_tests/bin/python -m pytest Tests/
```
Coverage report is printed in the terminal and saved as HTML to `Tests/coverage_html/index.html`.

### All tests (fast, no coverage)
```bash
PYTHONPATH=. ~/.venvs/lios_tests/bin/python -m pytest Tests/ --no-cov
```

### A single file
```bash
PYTHONPATH=. ~/.venvs/lios_tests/bin/python -m pytest Tests/test_ocr_engine_base.py -v
```

### A single test class or test
```bash
PYTHONPATH=. ~/.venvs/lios_tests/bin/python -m pytest Tests/test_ocr_engines.py::TestOcrEngineTesseract -v
PYTHONPATH=. ~/.venvs/lios_tests/bin/python -m pytest Tests/test_ocr_engines.py::TestOcrEngineTesseract::test_name_attribute -v
```

### Useful flags
| Flag | Effect |
|---|---|
| `-v` | Show each test name |
| `--tb=short` | Shorter tracebacks on failure |
| `-x` | Stop after first failure |
| `-k "tesseract"` | Filter tests by name |
| `-s` | Show `print()` / logging output |

---

## Test Files

| File | What It Tests |
|---|---|
| `test_macros.py` | Global constants, path resolution, `set_datadir`, mixed-case combos |
| `test_image_logics.py` | Rectangle overlap detection, box ordering, index finding |
| `test_ocr_engine_base.py` | `OcrEngineBase` abstract contract, all 3 language setters, edge cases |
| `test_ocr_engines.py` | All 6 concrete engines (Tesseract, Cuneiform, Gocr, Ocrad, ABBYY 9 & 11) — fully mocked |
| `test_tesseract_path_finder.py` | `FastTessdataFinder`: init, caching, env vars, glob matching, validation |
| `test_ocr_init.py` | `get_available_engines()` return type and filtering, all engine class imports |
| `test_text_to_audio.py` | `text_to_audio_converter` setters (volume/pitch/speed/voice) with mocked espeak |
| `test_mp_compat.py` | Multiprocessing compatibility: version detection, fork workaround, decorator |
| `test_dictionary.py` | Language name → code mapping correctness |
| `test_ocr_integration.py` | **Real** Tesseract OCR on actual PNG images *(auto-skipped if tesseract absent)* |
| `test_scanner_driver_base.py` | `DriverBase` abstract contract, `SCAN_AREA_*` constants |
| `test_scanner_sane_driver.py` | `DriverSane` with fully mocked `sane` module |
| `test_scanner_scanimage_driver.py` | `DriverScanimage` with mocked subprocess/os calls |

---

## Integration Tests (Real Tesseract)

`test_ocr_integration.py` runs real OCR — **no mocks**. It auto-skips if tesseract is not installed.

To install tesseract:
```bash
# Ubuntu / Debian
sudo apt install tesseract-ocr

# Arch
sudo pacman -S tesseract
```

---

## What These Tests Will Catch

- ✅ Breaking the `OcrEngineBase` language setter contract
- ✅ A new engine not implementing required methods
- ✅ Malformed tesseract shell commands (multi-lang `+` joining)
- ✅ Scanner device filtering broken (picks up webcams)
- ✅ Scan area calculations wrong (FULL/HALF/QUARTER)
- ✅ Import chain failures across the `lios.ocr` package
- ✅ Multiprocessing fork workaround wrongly applied

## What These Tests Won't Catch

- ❌ GTK UI bugs (requires a display server — use Xvfb for CI)
- ❌ Real scanner hardware failures
- ❌ Performance regressions

---

## Coverage

After running, open the HTML coverage report:
```bash
xdg-open Tests/coverage_html/index.html
```

Key module coverage:
- `lios/ocr/__init__.py` → **100%**
- `lios/ocr/ocr_engine_cuneiform.py` → **90%**
- `lios/ocr/ocr_engine_gocr.py` → **87%**
- `lios/ocr/ocr_engine_base.py` → **78%**
- `lios/scanner/sane_driver.py` → **65%**
- `lios/scanner/scanimage_driver.py` → **67%**

GTK UI files are 0% — they require a running GTK display.
