from PyQt5.QtGui import QImage, QPixmap
import yaml
import os
import numpy as np
from PIL import Image

class MapManager:
  def __init__(self, main_window):
    self.main_window = main_window

  def load_map_yamlfile(self, yamlfile_path):
    self.yamlfile_path = yamlfile_path
    try:
      with open(yamlfile_path, 'r') as file:
        map_info = yaml.safe_load(file)
    except FileNotFoundError:
      print(f"{self.__class__} : FileNotFoundError")
      return False

    self.resolution = map_info['resolution']
    self.origin = map_info['origin']
    self.negate = map_info['negate']
    self.occupied_thresh = map_info['occupied_thresh']
    self.free_thresh = map_info['free_thresh']
    pgmfile_name = map_info['image']
    map_dir = os.path.dirname(yamlfile_path)
    self.pgmfile_path = os.path.join(map_dir, pgmfile_name)
    self.load_map_pgmfile(self.pgmfile_path)

    return True

  def load_map_pgmfile(self, pgmfile_path):
    with open(pgmfile_path, 'rb') as file:
      self.map_type = file.readline()
      file.readline() # to read comment line
      self.width, self.height = map(int, file.readline().split())
      self.max_val = int(file.readline())
      if self.map_type == b'P5\n':
        self.map_bytes = file.read()
        self.map_pil = self.bytes2pil()
      else:
        print(f"{self.__class__} : Unsupported map type: {self.map_type}")
        self.map_bytes = None
        self.map_pil = None

  # NOTE: Show the map on the map_widget, but clear all current items by calling map_widget.set_map().
  def show_map(self):
    map_q = QImage(self.map_pil.tobytes(), self.map_pil.width, self.map_pil.height, QImage.Format_Grayscale8)
    pixmap = QPixmap.fromImage(map_q)
    self.main_window.map_widget.set_map(pixmap)

  # TODO: color categolize? more properlly
  def bytes2pil(self):
    np_map = np.zeros((self.height, self.width), dtype=np.uint8)
    for i in range(len(self.map_bytes)):
      if self.negate:
        cell = (self.max_val - self.map_bytes[i]) / self.max_val
      else:
        cell = self.map_bytes[i] / self.max_val

      if cell > self.occupied_thresh:
        np_map[i//self.width, i%self.width] = self.max_val
      elif cell < self.free_thresh:
        np_map[i//self.width, i%self.width] = 0
      else:
        np_map[i//self.width, i%self.width] = 100

    return Image.fromarray(np_map)

  def pixel2coord(self, xy):
    x, y = xy
    x = x * self.resolution + self.origin[0]
    y = -y * self.resolution - self.origin[1]
    return x, y

  def coord2pixel(self, xy):
    x, y = xy
    x = (x - self.origin[0]) / self.resolution
    y = -(y + self.origin[1]) / self.resolution
    return x, y
