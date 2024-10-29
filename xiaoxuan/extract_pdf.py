import pdfplumber


### 从PDF中提取文本和图片
def extract_text_images_from_pdf(pdf_path, image_folder):
    with pdfplumber.open(pdf_path) as pdf:
        all_text = ""

        for i, page in enumerate(pdf.pages):
            # 提取文本
            all_text += page.extract_text() + "\n"

            # 提取图片
            for j, image in enumerate(page.images):
                # 获取图片的位置信息
                x0, y0, x1, y1 = image['x0'], image['top'], image['x1'], image['bottom']

                # 转换页面为图片并裁剪
                img = page.to_image().original  # 转换页面为PIL图像
                cropped_img = img.crop((x0, y0, x1, y1))  # 裁剪出图片区域

                # 保存图片
                img_path = f"{image_folder}/page_{i + 1}_img_{j + 1}.png"
                cropped_img.save(img_path)
                print(f"已保存图片：{img_path}")

    return all_text


### 从PDF中仅仅提取文本
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        all_text = ""

        for i, page in enumerate(pdf.pages):
            # 提取文本
            all_text += page.extract_text() + "\n"

    return all_text


if __name__ == '__main__':
    pdf_path = r"D:\Scientific_Research\Education_Agent_Design\课程大纲&教案&逐字稿&习题.pdf"
    image_folder = "output_images"
    # text = extract_text_images_from_pdf(pdf_path, image_folder)
    text = extract_text_from_pdf(pdf_path)
    print(text)