import requests
import os
async def get_image_src_and_download(page, selector, image_name):
    try:
        iframe = page.frame_locator("#tcaptcha_iframe")
        captcha_div = iframe.locator(f'img#{selector}')
        image_src = await captcha_div.get_attribute('src')
        print(f"图片 URL: {image_src}")
        print("22222222222")
        if image_src:
            print(f"{image_name} URL: {image_src}")
            await download_image(image_src, image_name)
            return image_src
        else:
            print("未能提取图片的 URL")
    except Exception as e:
        print(f"提取图片 URL 时出错: {e}")
def download_image(url, filename):

    response = requests.get(url)
    with open(filename, "wb") as f:
        f.write(response.content)
    print(f"{filename} 下载完成!")
