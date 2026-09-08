import sys
import os
import json
from zipfile import ZipFile
import xml.etree.ElementTree as ET


def local_name(tag):
    return tag.split('}')[-1] if '}' in tag else tag


def extract(pptx_path, out_dir):
    with ZipFile(pptx_path, 'r') as z:
        # find slide files
        slide_files = sorted([n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')], key=lambda x: int(''.join(filter(str.isdigit, x)) or 0))
        assets_dir = os.path.join(out_dir, 'public', 'assets')
        os.makedirs(assets_dir, exist_ok=True)
        slides_out = []

        for slide_path in slide_files:
            data = z.read(slide_path)
            root = ET.fromstring(data)
            texts = [el.text for el in root.findall('.//{*}t') if el.text]

            # find rels for this slide to map images
            rels_path = slide_path.replace('ppt/slides/', 'ppt/slides/_rels/') + '.rels'
            images = []
            if rels_path in z.namelist():
                rels_data = z.read(rels_path)
                rels_root = ET.fromstring(rels_data)
                for rel in rels_root.findall('.//{*}Relationship'):
                    r_type = rel.attrib.get('Type', '')
                    target = rel.attrib.get('Target', '')
                    if 'image' in r_type and target:
                        # target like ../media/image1.png
                        img_path = os.path.normpath(os.path.join(os.path.dirname(rels_path), target)).lstrip('\\/')
                        # normalize to ppt/media/...
                        img_path = img_path.replace('..\\', '').replace('../', '')
                        if img_path in z.namelist():
                            img_name = os.path.basename(img_path)
                            out_img_path = os.path.join(assets_dir, img_name)
                            with open(out_img_path, 'wb') as f:
                                f.write(z.read(img_path))
                            images.append(f"/assets/{img_name}")

            slides_out.append({
                'index': int(''.join(filter(str.isdigit, slide_path)) or 0),
                'texts': texts,
                'images': images
            })

        public_dir = os.path.join(out_dir, 'public')
        os.makedirs(public_dir, exist_ok=True)
        with open(os.path.join(public_dir, 'slides.json'), 'w', encoding='utf-8') as f:
            json.dump(slides_out, f, ensure_ascii=False, indent=2)

        print(f"Extracted {len(slides_out)} slides to {public_dir}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python extract_pptx_no_deps.py input.pptx output_dir")
        sys.exit(1)
    pptx_path = sys.argv[1]
    out_dir = sys.argv[2]
    if not os.path.exists(pptx_path):
        print('PPTX 파일이 존재하지 않습니다:', pptx_path)
        sys.exit(1)
    extract(pptx_path, out_dir)


if __name__ == '__main__':
    main()
