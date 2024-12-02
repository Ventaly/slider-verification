import cv2
import numpy as np
import asyncio
import  os
from GetImage import get_image_src_and_download
import cv2 as cv
import numpy as np
import random

import random

import random


async def check_text1(page, text):
    """检查页面上是否存在指定文本"""
    elements = await page.query_selector_all(f'text="{text}"')
    print(elements)
    if elements:
        print(f"页面上存在文本为‘{text}’的元素")
        return True
    else:
        print(f"页面上不存在文本为‘{text}’的元素")
        return False


def find_gap(background_path, block_path):
    """
    使用 OpenCV 定位拼图缺口的 x 坐标，并计算滑块中心到缺口中心的距离
    :param background_path: 背景图片路径
    :param block_path: 拼图块图片路径
    :return: 缺口的 x 坐标以及滑块中心到缺口中心的距离
    """
    # 读取背景图片和拼图块图片
    background = cv.imread(background_path, cv.IMREAD_COLOR)
    block = cv.imread(block_path, cv.IMREAD_COLOR)

    # 滑块的宽高
    block_h, block_w = block.shape[:2]

    # 计算滑块的中心位置
    block_center_x = block_w / 2
    block_center_y = block_h / 2
    print(f"滑块中心位置: ({block_center_x}, {block_center_y})")

    # 高斯模糊处理减少噪声
    blurred = cv.GaussianBlur(background, (5, 5), 0)

    # Canny边缘检测
    canny = cv.Canny(blurred, 100, 200)

    # 轮廓检测
    contours, hierarchy = cv.findContours(canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # 用红色框标出所有轮廓
    for contour in contours:
        # 获取每个轮廓的外接矩形
        x, y, w, h = cv.boundingRect(contour)

        # 过滤条件：面积和周长范围
        if 6000 < cv.contourArea(contour) <= 8000 and 300 < cv.arcLength(contour, True) < 500:
            # 绘制外接矩形
            cv.rectangle(background, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # 输出每个符合条件的轮廓的坐标与大小
            print(f"Found contour at x: {x}, y: {y}, w: {w}, h: {h}")

            # 假设目标缺口位置在滑块附近
            if x <= 200:  # 排除非目标区域的轮廓
                continue

            # 计算缺口的中心位置
            gap_center_x = x + w / 2
            gap_center_y = y + h / 2

            # 计算滑块中心到缺口中心的距离
            distance_x = abs(gap_center_x - block_center_x)
            distance_y = abs(gap_center_y - block_center_y)
            distance = (distance_x ** 2 + distance_y ** 2) ** 0.5
            print(f"缺口中心位置: ({gap_center_x}, {gap_center_y})")
            print(f"滑块中心到缺口中心的距离: {distance}")

            # 在背景上绘制缺口的中心位置
            cv.circle(background, (int(gap_center_x), int(gap_center_y)), radius=10, color=(255, 0, 0), thickness=-1)

            # 显示结果
            cv.imshow("Detected Contours with Gap Marked", background)
            cv.waitKey(5000)  # 等待 1 秒后自动关闭
            cv.destroyAllWindows()  # 确保关闭窗口

            # 返回缺口的 x 坐标以及滑块中心到缺口中心的距离
            return gap_center_x

    # 如果未找到缺口
    cv.imshow("Detected Contours", background)
    cv.waitKey(0)
    cv.destroyAllWindows()
    print("未找到匹配的缺口")
    return None, None


def generate_track(distance):
    """
    根据距离生成滑动轨迹，模拟人类滑动行为
    :param distance: 缺口距离
    :return: 滑动轨迹列表
    """
    track = []
    current = 0

    # 第一步快速接近目标位置
    first_move = random.uniform(distance * 0.8, distance * 0.95)  # 接近目标的 80%-95%
    current += first_move
    track.append(round(first_move))  # 记录第一步

    # 第二步略微超出目标
    overshoot = random.uniform(5, 15)  # 随机超出 5 到 15 像素
    current += overshoot
    track.append(round(overshoot))  # 记录第二步

    # 第三步回调到目标
    final_move = distance - current
    track.append(round(final_move))  # 精准对齐

    return track


async def solve_slider(page):
    """
    使用 Playwright 解决滑动验证
    :param background_path: 背景图片路径
    :param block_path: 拼图块图片路径
    :param url: 滑动验证页面的 URL
    """
    background_path = "background.jpg"
    block_path = "block.jpg"
    # 删除旧文件
    #在每次运行前删除可能存在的旧文件，确保下载的文件是新的。
    for file_path in [background_path, block_path]:
        if os.path.exists(file_path):
            os.remove(file_path)
    # 获取验证图片路径
    await get_image_src_and_download(page, 'slideBg', background_path)
    print("111111")
    await asyncio.sleep(10)

    # 提取拼图块图片 URL 并下载
    await get_image_src_and_download(page, 'slideBlock', block_path)
    print("3333333333")
    if os.path.exists(background_path) and os.path.exists(block_path):
        gap_x = find_gap(background_path, block_path)  # 获取缺口位置

    # 定位滑块元素

    iframe = page.frame_locator("#tcaptcha_iframe")
    captcha_div = iframe.locator('img#slideBlock')
    background_div = iframe.locator('img#slideBg')

    # 获取背景图片的位置信息
    background_box = await background_div.bounding_box()
    background_x = background_box['x']
    background_y = background_box['y']

    # 获取滑块的位置
    slider_box = await captcha_div.bounding_box()
    slider_x = slider_box['x']
    slider_y = slider_box['y']

    # 计算滑块相对于背景图片的坐标
    relative_x = slider_x - background_x
    relative_y = slider_y - background_y

    print(f"滑块相对于背景图片的 x 坐标: {relative_x}")
    print(f"滑块相对于背景图片的 y 坐标: {relative_y}")

    # 页面代码中获取图片的实际显示宽度和高度
    iframe = page.frame_locator("#tcaptcha_iframe")
    background_element = iframe.locator(f'img#slideBg')

    bg_box = await background_element.bounding_box()

    # 背景图片实际显示的宽高
    bg_display_width = bg_box['width']

    # 加载背景图片的实际尺寸
    background_image = cv2.imread(background_path)

    img_actual_height, bg_image_width = background_image.shape[:2]
    print(f"背景图片显示宽度: {bg_display_width}, 原始宽度: {bg_image_width}")
    # 计算比例
    scale_x = bg_display_width / bg_image_width
    gap_x_page = gap_x * scale_x
    # 获取滑块的初始位置
    box = await captcha_div.bounding_box()  # 获取滑块的初始位置
    if not box:
        print("无法获取滑块位置")
        return
    slider_width = box['width']
    slider_height = box['height']
    slider_x_start = box['x']

    slider_y_start = box['y']
    # 计算滑动距离
    distance = gap_x_page - slider_x

    if distance > 0:
        distance = gap_x_page - slider_x
    else:
        distance = gap_x_page - relative_x
    # 根据 distance 生成模拟人类滑动行为的轨迹（即滑动的每一步距离）。
    track = generate_track(distance)

    # 模拟鼠标移动
    current_x = slider_x_start
    # 计算滑块中心点
    center_x = slider_x_start + slider_width / 2
    center_y = slider_y_start + slider_height / 2
    # 移动到滑块起点
    await page.mouse.move(center_x, center_y)
    # 检查鼠标是否位于滑块范围内
    mouse_x = center_x
    mouse_y = center_y
    if slider_x_start <= mouse_x <= slider_x_start + slider_width and \
            slider_y_start <= mouse_y <= slider_y_start + slider_height:
        print("鼠标已经移动到滑块上")
    else:
        print("鼠标未移动到滑块上")
    await page.mouse.down()

    # 遍历滑动轨迹 track 中的每一步。
    # 每次增加 move 的值到 current_x，并调用 page.mouse.move 移动鼠标。
    # time.sleep(0.01): 增加短暂延迟，模拟人类滑动的真实速度。
    for move in track:
        current_x += move
        await page.mouse.move(current_x, slider_y_start + slider_height / 2)
        await asyncio.sleep(0.01)  # 模拟人类滑动延迟

    await page.mouse.up()  # 松开滑块
    await asyncio.sleep(0.01)


