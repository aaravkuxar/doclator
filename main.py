import fitz  # pymupdf
import argparse
from deep_translator import GoogleTranslator
import time


def translate_text(text, source, target):
    """Translate text, handling empty strings and rate limits."""
    if not text.strip():
        return text
    try:
        translated = GoogleTranslator(source=source, target=target).translate(text)
        return translated if translated else text
    except Exception as e:
        print(f"  Warning: translation failed for snippet — {e}")
        return text  # fallback to original


def translate_pdf(input_path, output_path, source_lang, target_lang):
    doc = fitz.open(input_path)
    print(f"Opened '{input_path}' — {len(doc)} pages")

    for page_num, page in enumerate(doc):
        print(f"Processing page {page_num + 1}/{len(doc)}...")

        # Get all text blocks with positions
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if block["type"] != 0:  # 0 = text, 1 = image
                continue

            for line in block["lines"]:
                for span in line["spans"]:
                    original_text = span["text"]
                    if not original_text.strip():
                        continue

                    translated_text = translate_text(
                        original_text, source_lang, target_lang
                    )

                    if translated_text == original_text:
                        continue

                    # Cover original text with white rectangle
                    rect = fitz.Rect(span["bbox"])
                    page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

                    # Write translated text in same position and size
                    page.insert_text(
                        rect.tl,  # top-left corner
                        translated_text,
                        fontsize=span["size"],
                        color=(0, 0, 0),
                    )

                    # Small delay to avoid hitting API rate limits
                    time.sleep(0.05)

    doc.save(output_path)
    print(f"\nDone! Saved to '{output_path}'")


def main():
    parser = argparse.ArgumentParser(description="Translate a PDF file.")
    parser.add_argument("input", help="Path to input PDF")
    parser.add_argument("output", help="Path to output PDF")
    parser.add_argument("--source", default="de", help="Source language (default: de)")
    parser.add_argument("--target", default="en", help="Target language (default: en)")
    args = parser.parse_args()

    translate_pdf(args.input, args.output, args.source, args.target)


if __name__ == "__main__":
    main()
