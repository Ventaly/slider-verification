import cv2
import numpy as np

# def find_gap(background_path, block_path):
#     """
#     使用 OpenCV 定位拼图缺口的 x 坐标
#     :param background_path: 背景图片路径
#     :param block_path: 拼图块图片路径
#     :return: 缺口的 x 坐标
#     """
#     # 读取图片
#     background = cv2.imread(background_path, cv2.IMREAD_COLOR)  # 读取背景图片
#     block = cv2.imread(block_path, cv2.IMREAD_COLOR)  # 读取拼图块图片
#
#     # 转换为灰度图
#     background_gray = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
#     block_gray = cv2.cvtColor(block, cv2.COLOR_BGR2GRAY)
#
#     # 模板匹配
#     result = cv2.matchTemplate(background_gray, block_gray, cv2.TM_CCOEFF_NORMED)
#
#     # 获取匹配结果中的最大匹配位置
#     _, _, _, max_loc = cv2.minMaxLoc(result)
#
#     # max_loc[0] 是拼图块的左上角的 x 坐标。根据此位置推算缺口位置。
#     gap_x = max_loc[0]  # 获取左上角的 x 坐标
#
#     # 如果拼图块与缺口边缘有重叠，可以在 gap_x 位置微调或进一步处理。
#     return gap_x
#
# # 示例
# background_path = 'background.jpg'
# block_path = 'block.jpg'
# gap_x = find_gap(background_path, block_path)
# print(f"缺口的 x 坐标: {gap_x}")

import cv2 as cv
import numpy as np


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
            distance = (distance_x**2 + distance_y**2)**0.5
            print(f"缺口中心位置: ({gap_center_x}, {gap_center_y})")
            print(f"滑块中心到缺口中心的距离: {distance}")

            # 在背景上绘制缺口的中心位置
            cv.circle(background, (int(gap_center_x), int(gap_center_y)), radius=10, color=(255, 0, 0), thickness=-1)

            # 显示结果
            cv.imshow("Detected Contours with Gap Marked", background)
            cv.waitKey(1000)  # 等待 1 秒后自动关闭
            cv.destroyAllWindows()  # 确保关闭窗口

            # 返回缺口的 x 坐标以及滑块中心到缺口中心的距离
            return gap_center_x, distance

    # 如果未找到缺口
    cv.imshow("Detected Contours", background)
    cv.waitKey(0)
    cv.destroyAllWindows()
    print("未找到匹配的缺口")
    return None, None

import cv2 as cv

# 调用定位缺口的函数
def test_find_gap(background_path, block_path):
    gap_x, gap_y = find_gap(background_path, block_path)
    if gap_x is not None and gap_y is not None:
        print(f"缺口位置: x={gap_x}, y={gap_y}")
    else:
        print("未找到缺口位置")

# 测试示例
background_path = 'background.jpg'  # 背景图片路径
block_path = 'block.jpg'  # 拼图块图片路径

test_find_gap(background_path, block_path)
