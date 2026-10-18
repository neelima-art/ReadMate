from book_processor import extract_book_text

file_path = "uploads/The Lost World - Arthur Conan Doyle.pdf"

text = extract_book_text(file_path)

lines = text.splitlines()

print("Total lines:", len(lines))
print()

for i, line in enumerate(lines):

    if "chapter" in line.lower():

        print("=" * 70)

        start = max(0, i - 2)
        end = min(len(lines), i + 5)

        for j in range(start, end):
            print(f"{j}: {lines[j]}")

print("=" * 70)