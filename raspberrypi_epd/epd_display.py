"""
2025/01/10  RPi.GPIOを使わないgpiozero方式とした
"""
import numpy as np
import raspberrypi_epd.commands as cmd
import logging
import time
import spidev
from gpiozero import OutputDevice, InputDevice
from enum import Enum
from raspberrypi_epd.buffer import DisplayBuffer
#from bdfparser import Font

class Color(Enum):
    BLACK = 0
    WHITE = 1
    RED = 2

BLACK = np.uint8(0x00)
WHITE = np.uint8(0xFF)
RED = np.uint8(0xFF)

class WeAct213:
    HEIGHT = 296
    WIDTH = 128
    WIDTH_VISIBLE = 128
    CONTROLLER = "SSD1680"
    # Timings
    POWER_ON_TIME = 100
    POWER_OFF_TIME = 250
    FULL_REFRESH_TIME = 4100
    PARTIAL_REFRESH_TIME = 750
    RESET_WAIT_TIME = 10
    LUT_PARTIAL = np.array(
        [
            0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x80, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0A, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x02, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x00, 0x00, 0x00], dtype=np.uint8)

    def __init__(self, dc: int, cs: int, busy: int, reset: int):
        self._DC = OutputDevice(dc)
        self._CS = OutputDevice(cs)
        self._RESET = OutputDevice(reset)
        self._BUSY = InputDevice(busy)
        self._RESET.on()
        self._spi = spidev.SpiDev()
        self._spi.open(bus=0, device=0)
        self._spi.max_speed_hz = 500000  # 500KHz
        self._spi.mode = 0  # Clock polarity/phase
        self._bw_buffer = DisplayBuffer(self.WIDTH, self.HEIGHT)
        self._red_buffer = DisplayBuffer(self.WIDTH, self.HEIGHT, bg=0, fg=1)
        self.powered = False
        self._using_partial_mode = False
        self._partial_area = (0, 0, 0, 0)
        self._initial_refresh = True
        self._font = None
        self._rotation = 0

    def init(self):
        logging.debug("Initializing display")
        self.reset()
        self._startup()
        self._power_on()
        self._using_partial_mode = False

    def _power_on(self):
        if not self.powered:
            self._write_command(cmd.DISPLAY_UPDATE_CONTROL_2)
            self._write_data_byte(np.uint8(0xF8))
            self._write_command(cmd.MASTER_ACTIVATION)
            self._wait_while_busy()
        self.powered = True
        logging.debug("Power on complete")

    def _power_off(self):
        if self.powered:
            self._write_command(cmd.DISPLAY_UPDATE_CONTROL_2)
            self._write_data_byte(np.uint8(0x83))
            self._write_command(cmd.MASTER_ACTIVATION)
            self._wait_while_busy()
        self.powered = False
        self._using_partial_mode = False

    def init_partial(self):
        logging.debug("Initializing partial update mode")
        self._startup()
        self._write_command(cmd.WRITE_LUT_REG)
        self._write_data(self.LUT_PARTIAL)
        self._power_on()
        self._using_partial_mode = True

    def reset(self):
        logging.debug("Reseting the display")
        self._RESET.off()
        time.sleep(0.01)
        self._RESET.on()
        self._write_command(cmd.SW_RESET)
        self._wait_while_busy()
        time.sleep(0.01)
        self._wait_while_busy()
        logging.debug("Display was reset")

    def close(self):
        self._spi.close()

    def _wait_while_busy(self):
        counter = 0
        while self._BUSY.is_active:
            time.sleep(0.005)
            counter += 1
        logging.debug(f"Display was busy for {counter*5} ms")

    def _startup(self):
        self._write_command(cmd.DRIVER_OUTPUT_CONTROL)
        self._write_data_byte(np.uint8(0x27))
        self._write_data_byte(np.uint8([0x01]))
        self._write_data_byte(np.uint8([0x00]))
        self._write_command(cmd.DATA_ENTRY_MODE)
        self._write_data_byte(np.uint8([0x03]))
        self._write_command(cmd.BORDER_WAVEFORM_CONTROL)
        self._write_data_byte(np.uint8(0x05))
        self._write_command(cmd.TEMP_SENSOR_CONTROL)
        self._write_data_byte(np.uint8(0x80))
        self._write_command(cmd.DISPLAY_UPDATE_CONTROL)
        self._write_data_byte(np.uint8(0x00))
        self._write_data_byte(np.uint8(0x80))
        self._partial_area = (0, 0, self.WIDTH, self.HEIGHT)

    def _set_partial_area(self, x, y, width, height):
        self._write_command(cmd.DATA_ENTRY_MODE)
        self._write_data_byte(np.uint8(0x03))
        self._write_command(cmd.SET_RAM_X_STARTEND)
        start_x_address = np.uint8(x / 8)
        end_x_address = np.uint8((x + width - 1) / 8)
        self._write_data_byte(start_x_address)
        self._write_data_byte(end_x_address)
        self._write_command(cmd.SET_RAM_Y_STARTEND)
        start_y_mod = np.uint8(y % 256)
        start_y_mult = np.uint8(y / 256)
        self._write_data_byte(start_y_mod)
        self._write_data_byte(start_y_mult)
        end_y_mod = np.uint8((y + height - 1) % 256)
        end_y_mult = np.uint8((y + height - 1) / 256)
        self._write_data_byte(end_y_mod)
        self._write_data_byte(end_y_mult)

    def _write_command(self, command):
        self._DC.off()
        # self._spi.xfer([command])
        self._spi.xfer([int(command)])

    def _write_data_byte(self, data):
        self._DC.on()
        MAX_TRANSFER_SIZE = 4096  # spidevの制限
        # データがnumpy配列の場合はリストに変換
        if isinstance(data, np.ndarray):
            data = data.tolist()
        # データが単一の値の場合はリストに変換
        if isinstance(data, (np.uint8, int)):
            data = [int(data)]
        # データを分割して送信
        for i in range(0, len(data), MAX_TRANSFER_SIZE):
            chunk = data[i:i + MAX_TRANSFER_SIZE]
            self._spi.xfer(chunk)

    def _write_data(self, data):
        self._DC.on()
        MAX_TRANSFER_SIZE = 4096  # spidevの制限
        # データをリスト形式に変換
        if isinstance(data, (bytes, bytearray)):
            data = list(data)
        elif isinstance(data, np.ndarray):  # numpy配列の場合
            data = data.tolist()
        # データを分割して送信
        for i in range(0, len(data), MAX_TRANSFER_SIZE):
            chunk = data[i:i + MAX_TRANSFER_SIZE]
            self._spi.xfer(chunk)  # spidev.xferにリストを渡す

    def _update_full(self):
        """
        Updates the whole screen
        :return: None
        """
        self._write_command(cmd.DISPLAY_UPDATE_CONTROL_2)
        self._write_data_byte(np.uint8(0xF4))
        self._write_command(cmd.MASTER_ACTIVATION)
        self._wait_while_busy()

    def _update_partial(self):
        """
        Make a partial update on the screen
        :return:
        """
        self._write_command(cmd.DISPLAY_UPDATE_CONTROL_2)
        self._write_data_byte(np.uint8(0xCC))  # F7
        self._write_command(cmd.MASTER_ACTIVATION)
        self._wait_while_busy()

    def fill(self, color: Color):
        """
        Fills the whole screen with the specified color
        :param color: The Color to paint the screen
        :return: None
        """
        if color == Color.RED:
            logging.debug("Filling the screen with RED color")
            self._bw_buffer.clear_screen(0)
            self._red_buffer.clear_screen(1)
        else:
            logging.debug(f"Filling the screen with {color.value}")
            self._bw_buffer.clear_screen(color.value)
            self._red_buffer.clear_screen(0)
        logging.debug(
            f"Sampling B&W RAM (0,0): 0x{self._bw_buffer.get_pixel_byte(0, 0).tobytes().hex()}"
        )
        logging.debug(
            f"Sampling RED RAM (0,0): 0x{self._red_buffer.get_pixel_byte(0, 0).tobytes().hex()}"
        )
        self.write_buffer()

    def set_rotation(self, degrees: int):
        """
        Changes the rotation angle of the screen
        :param degrees: One of [0, 90, 180, 270]
        :return: None
        """
        self._bw_buffer.rotate(degrees)
        self._red_buffer.rotate(degrees)

    def write_buffer(self):
        """
        Writes the complete buffers (B&W and Red) to the display
        :return: None
        """
        self._set_partial_area(0, 0, self.WIDTH, self.HEIGHT)
        # After this command, data entries will be written into the BW RAM until another command is written.
        self._write_command(cmd.WRITE_RAM_BW)
        bw_buffer_bytes = self._bw_buffer.serialize()
        self._write_data(bw_buffer_bytes)
        self._write_command(cmd.WRITE_RAM_RED)
        red_buffer_bytes = self._red_buffer.serialize()
        logging.debug(red_buffer_bytes)
        self._write_data(red_buffer_bytes)
        self._update_partial()

    def refresh(self, partial_mode=True):
        """
        Refreshes the screen
        :param partial_mode:
        :return:
        """
        if partial_mode:
            self.refresh_area(0, 0, self.WIDTH, self.HEIGHT)
        else:
            if self._using_partial_mode:
                self.init()
            self._update_full()

    def refresh_area(self, x, y, width, height):
        """
        Refreshes a partial area of the screen
        :param x: X Coordinate of the upper left corner
        :param y: Y Coordinate of the upper left corner
        :param width: Area width
        :param height: Area height
        :return: None
        """
        x1, y1, w1, h1 = self._get_visible_bbox(x, y, width, height)
        if not self._using_partial_mode:
            self.init()
        self._set_partial_area(x1, y1, w1, h1)
        self._update_partial()

    #def set_font(self, path: str):
        """
        Sets the font to draw text with.
        :param path: The path to a bfd font in the local filesystem
        :return: None
        """
    #    self._font = Font(path)

    def draw_pixel(self, x: int, y: int, color: Color):
        """
        Draws a single pixel in the screen
        :param x: X Coordinate of the point
        :param y: Y Coordinate of the point
        :param color: Color (enum) of the pixel
        :return: None
        """
        if color is Color.BLACK or color is Color.WHITE:
            color_value = np.uint8(0) if color is Color.BLACK else np.uint8(1)
            self._bw_buffer.draw_pixel(x, y, color_value)
            self._red_buffer.draw_pixel(x, y, np.uint8(0))
        else:
            self._red_buffer.draw_pixel(x, y, np.uint8(1))

    def draw_line(self, x1: int, y1: int, x2: int, y2: int, color: Color):
        """
        Draw a line in the screen. It only has a width of 1 pixel
        :param x1: X Coordinate of the starting point
        :param y1: Y Coordinate of the starting point
        :param x2: X Coordinate of the end point
        :param y2: Y Coordinate of the end point
        :param color: Color (enum) of the line
        :return: None
        """
        logging.debug("Drawing a line")
        if x1 == x2 and y1 == y2:
            self.draw_pixel(x1, y1, color)
            logging.debug(f"Same start/end points. Drawing a pixel at ({x1},{y1})")
            return
        if color is Color.BLACK or color is Color.WHITE:
            color_value = np.uint8(0) if color is Color.BLACK else np.uint8(1)
            logging.debug(f"Line will be drawn to B&W with value {color_value}")
            self._bw_buffer.draw_line(x1, y1, x2, y2, color_value)
            self._red_buffer.draw_line(x1, y1, x2, y2, np.uint8(0))
        else:
            # Doesn't matter what it's written in the B&W buffer
            logging.debug("Line will be drawn to RED buffer")
            self._red_buffer.draw_line(x1, y1, x2, y2, np.uint8(1))

    def draw_bitmap(self, bitmap: np.array, x: int, y: int, width: int, height: int, color: Color):
        """
        Draws a bitmap on the screen. The bitmap is binary where the set bits are to be painted
        with the specified color and those unset will respect their current state.
        Bitmap dimmensions (in pixels) have to be multiples of 8 (pad them with zeros if you must)
        :param bitmap: A 1-dimmension array of bytes representing the bitmap, the size is (width x lenght)/8
        :param x: X Coordinate of the upper left corner
        :param y: Y Coordinate of the upper left corner
        :param width: Width of the bitmap to draw
        :param height: Height of the bitmap to draw
        :param color: Color (enum) to paint the bitmap with
        :return: None
        """
        if color is Color.BLACK or color is Color.WHITE:
            color_value = np.uint8(0) if color is Color.BLACK else np.uint8(1)
            self._bw_buffer.draw_bitmap(bitmap, x, y, width, height, color_value)
            self._red_buffer.draw_bitmap(bitmap, x, y, width, height, np.uint8(0))
        else:
            self._red_buffer.draw_bitmap(bitmap, x, y, width, height, np.uint8(1))
            

    #def draw_text(self, text: str, x: int, y: int, color: Color):
        """
        Draw text in the screen. To use this, a font is needed to be set (see set_font method)
        :param text: The string to draw
        :param x: X Coordinate of the upper left corner of the text
        :param y: Y Coordinate of the upper left corner of the text
        :param color: Color (enum) of the text
        :return: None
        """
        """
        if self._font is None:
            logging.warning('Font is not set!')
            return
        if color is Color.BLACK or color is Color.WHITE:
            color_value = np.uint8(0) if color is Color.BLACK else np.uint8(1)
            self._bw_buffer.draw_text(text, self._font, x, y, color_value)
            self._red_buffer.draw_text(text, self._font, x, y, np.uint8(0))
        else:
            self._red_buffer.draw_text(text, self._font, x, y, np.uint8(1))
        """

    def draw_circle(self, x: int, y: int, r: int, color: Color):
        """
        Draws a circle in the screen. It is limited to be drawn with a 1 pixel width line
        :param x: X Coordinate of the circle's center
        :param y: Y Coordinate of the circle's center
        :param r: Radius of the circle
        :param color: Color (enum) of the circle
        :return: None
        """
        if color is Color.BLACK or color is Color.WHITE:
            color_value = np.uint8(0) if color is Color.BLACK else np.uint8(1)
            self._bw_buffer.draw_circle(x, y, r, color_value)
            self._red_buffer.draw_circle(x, y, r, np.uint(0))
        else:
            self._red_buffer.draw_circle(x, y, r, np.uint8(1))

    def draw_rectangle(self, x: int, y: int, width: int, height: int, color: Color):
        """
        Draws a rectangle of the specified characteristics. Limited to 1 pixel lines and no fill
        :param x: X Coordinate of the upper left corner
        :param y: Y Coordinate of the upper left corner
        :param width: Width of the rectangle
        :param height: Height of the rectangle
        :param color: Color of the lines
        :return: None
        """
        if color is Color.BLACK or color is Color.WHITE:
            color_value = np.uint8(0) if color is Color.BLACK else np.uint8(1)
            self._bw_buffer.draw_rectangle(x, y, width, height, color_value)
            self._red_buffer.draw_rectangle(x, y, width, height, 0)
        else:
            self._red_buffer.draw_rectangle(x, y, width, height, np.uint8(1))

    def _get_visible_bbox(self, x, y, w, h):
        """
        Compute the intersection area of a given bounding box with the screen
        :param x: X Coordinate of the upper left corner of the bounding box
        :param y: Y Coordinate of the upper left corner of the bounding box
        :param w: Width of the bounding box
        :param h: Height of the bounding box
        :return: A 4-tuple representing the upper left coordinates of the intersection followed by its width and height
        """
        x1, y1, w1, h1 = [0] * 4
        if x < 0:
            x1 = 0
        elif x < self.WIDTH:
            x1 = x
        else:
            raise ValueError("Image located completely outside of the display")

        if y < 0:
            y1 = 0
        elif y < self.HEIGHT:
            y1 = y
        else:
            raise ValueError("Image located completely outside of the display")

        if x + w < 0 or x > self.WIDTH:
            w1 = w
        elif x < 0:
            w1 = x + w
        elif x + w > self.WIDTH:
            w1 = self.WIDTH - x
        else:
            w1 = w

        if y + h < 0 or y > self.HEIGHT:
            # the image is completely outside of bounds
            h1 = h
        elif y < 0:
            h1 = y + h
        elif y + h > self.HEIGHT:
            h1 = self.HEIGHT - y
        else:
            h1 = h
        return x1, y1, w1, h1
