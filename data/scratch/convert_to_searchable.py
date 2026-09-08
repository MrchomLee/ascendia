import fitz
from rapidocr import RapidOCR
import sys
import time

def create_searchable_pdf(input_pdf, output_pdf, max_pages=None):
    print(f"Opening {input_pdf}")
    doc = fitz.open(input_pdf)
    ocr = RapidOCR()
    
    pages_to_process = min(max_pages, len(doc)) if max_pages else len(doc)
    start_time = time.time()
    
    for i in range(pages_to_process):
        page = doc.load_page(i)
        print(f"Processing page {i+1}/{pages_to_process}")
        
        # Get page image
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        
        # Run OCR
        try:
            res = ocr(img_bytes)
            if hasattr(res, 'boxes') and res.boxes:
                boxes = res.boxes
                texts = res.txts
                if boxes and texts:
                    for box, text in zip(boxes, texts):
                        # Box format: [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
                        scale = 72.0 / 150.0
                        x0 = box[0][0] * scale
                        y0 = box[0][1] * scale
                        
                        # Insert text in invisible mode
                        try:
                            page.insert_text(fitz.Point(x0, y0), text, fontsize=10, render_mode=3)
                        except Exception as e:
                            print(f"Warning: Failed to insert text on page {i+1}: {e}")
        except Exception as e:
            print(f"Error processing OCR on page {i+1}: {e}")
            
    print(f"Saving to {output_pdf}")
    doc.save(output_pdf)
    doc.close()
    
    elapsed = time.time() - start_time
    print(f"Done in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python convert_to_searchable.py <input> <output>")
        sys.exit(1)
        
    create_searchable_pdf(sys.argv[1], sys.argv[2])
