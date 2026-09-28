# File Tidy

A tiny command-line tool that organizes messy folders — sorts files by
type, by date, or both. Safe by default: it shows a plan first and moves
nothing until you say `--apply`. Every move is logged, so any run can be
reverted with a single `--undo`.

**No dependencies** — pure Python 3 standard library. Python 3.10+.

## Quick start

```bash
# preview what would happen (nothing is moved)
python tidy.py by-type --dir ~/Downloads

# actually move the files
python tidy.py by-type --dir ~/Downloads --apply

# change your mind
python tidy.py --undo --dir ~/Downloads
```

## Modes

| Mode           | Layout                        | Example                    |
| -------------- | ----------------------------- | -------------------------- |
| `by-type`      | one folder per category       | `Images/photo.jpg`         |
| `by-date`      | year folders (`--month` for `YYYY-MM`) | `2024/` or `2024-03/` |
| `by-type-date` | category + date               | `Images/2024-03/photo.jpg` |

Dates are taken from the file modification time (mtime).

## Categories (by-type)

| Category   | Extensions |
| ---------- | ---------- |
| Images     | jpg, jpeg, png, gif, webp, bmp, svg, ico, tif, tiff, heic |
| Documents  | pdf, doc, docx, xls, xlsx, ppt, pptx, txt, md, rtf, odt, csv |
| Audio      | mp3, wav, flac, ogg, m4a, aac, wma |
| Video      | mp4, mkv, avi, mov, webm, wmv, flv, m4v |
| Archives   | zip, rar, 7z, tar, gz, bz2, xz, iso |
| Code       | py, js, ts, html, css, json, xml, yml, yaml, sh, bat, ps1, sql, c, cpp, java, go, rs |
| Other      | everything else |

## Options

```
tidy.py [mode] [options]

  mode                  by-type | by-date | by-type-date
  --dir PATH            folder to tidy (default: current)
  --apply               actually move files (default: dry run)
  --undo                revert the last applied run
  -r, --recursive       include subfolders
  -e, --exclude PATTERN skip matching files, glob-style (repeatable)
  --month               by-date: use YYYY-MM folders instead of YYYY
  -V, --version         show version
  -h, --help            show help
```

## Safety

- **Dry run by default.** Without `--apply` you only get a table of
  planned moves.
- **Name conflicts** are resolved with a numeric suffix: `report.pdf`,
  `report (1).pdf`, `report (2).pdf`…
- **Undo journal.** Each applied run appends JSON lines to `moves.log`
  next to the sorted folder:
  ```json
  {"from": "C:/Downloads/a.txt", "to": "C:/Downloads/Documents/a.txt", "ts": "2024-05-01T12:00:00"}
  ```
  `--undo` replays the journal in reverse, restoring every file to its
  original location, then deletes the journal. Files that are already
  gone are skipped with a warning.
- **Errors don't stop the run.** Locked or read-protected files are
  reported and skipped; everything else is still processed.
- `moves.log` and the script itself are never moved.

## Testing

```bash
python scripts/make_fixtures.py   # creates ./tidy-demo with 18 sample files
python tidy.py by-type --dir tidy-demo            # dry run
python tidy.py by-type --dir tidy-demo --apply    # sort
python tidy.py --undo --dir tidy-demo             # restore
```

## Русский

**File Tidy** — крошечная консольная утилита для наведения порядка в
папках: раскладывает файлы по типу, дате или и тому и другому.

- **Безопасно по умолчанию:** без `--apply` показывается только план
  (таблица «файл → папка»), ничего не перемещается.
- **Режимы:** `by-type` (Images/Documents/Audio/Video/Archives/Code/Other
  по расширению), `by-date` (папки-годы, с `--month` — `ГГГГ-ММ`),
  `by-type-date` (комбо: `Images/2024-03`).
- **Отмена:** каждое перемещение пишется в журнал `moves.log`
  (JSON: from, to, ts). `python tidy.py --undo --dir ПАПКА` вернёт всё
  как было.
- **Конфликты имён** решаются суффиксом: `report (1).pdf`.
- **Ошибки** (нет прав, файл занят) не прерывают работу — файл
  пропускается с предупреждением.

```bash
python tidy.py by-type --dir ~/Downloads            # показать план
python tidy.py by-type --dir ~/Downloads --apply    # разложить
python tidy.py --undo --dir ~/Downloads             # вернуть назад
python tidy.py by-date --dir ~/Downloads --month -r -e "*.tmp"
```

Зависимостей нет — только стандартная библиотека Python.
