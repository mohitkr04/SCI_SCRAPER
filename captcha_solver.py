from PIL import Image
import io

def solve_captcha(captcha_element):
    captcha_img = Image.open(io.BytesIO(captcha_element.screenshot_as_png))
    return "dummy_captcha_solution"