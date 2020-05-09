# ===========================================================================
#   rscanvas.py ---------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.imgtools as imgtools
import rsvis.utils.patches_ordered
import rsvis.utils.patches_unordered

import rsvis.tools.imgconcanvas

import numpy as np
import pathlib
from PIL import Image, ImageTk
from tkinter import Canvas, Frame, Listbox, Scrollbar, END, N, W, E, S

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class RSCanvas(rsvis.tools.imgconcanvas.ImageContainerCanvas):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
        self, 
        parent, 
        data,
        grid=list(), 
        obj_path=None,
        popup=None, 
        classes=dict(), 
        **kwargs
    ):
        
        super(RSCanvas, self).__init__(parent, shift=[4,4], **kwargs)
        
        self._new_popup = popup if popup else (lambda x: x)

        self._data = data
        self._index_list = rsvis.utils.index.Index(len(self._data))

        self._get_obj_path = obj_path

        self.bind("<Button-1>", self.mouse_button_1_pressed)
        self.bind("<ButtonRelease-1>", self.mouse_button_1_released)
        self.bind("<ButtonRelease-2>", self.mouse_button_2_released)
        self.bind("<Double-Button-1>", self.mouse_double_1_button)
        self.bind("<B1-Motion>", self.mouse_motion)

        self.mouse_area = list()
        self.mouse_point = list()

        self._area_event = 0

        self._grid_flag = 1
        self._grid = grid if grid else [1, 1]
        
        self._object_flag = 0

        self._selection = dict()
        self._patches_bbox = None
        self._patches_grid = None

        self._boxes = list()                        
        self._color = dict((c["name"], c["color"]) for c in classes)
        self._label = list(self._color.keys())[0] if self._color else None

        self._bbox = [0, 0, 0, 0]

        self._point = [0,0]

        self._mouse_sensitivity = 4

        self.bind("<a>", self.key_a)
        self.bind("<d>", self.key_d)
        self.bind("<f>", self.key_f)
        self.bind("<g>", self.key_g)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def clear(self, **kwargs):
        super(RSCanvas, self).clear(**kwargs)
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def resize_bbox(self, boxes, inverted=False):
        scale = [float(s)/i for s, i in zip(self.get_size(), self._img_size)]

        if inverted:
            scale = [1/s for s in scale]

        boxes_resize = list()
        for box in boxes:
            boxes_resize.append([
                int(box[0]*scale[1]), int(box[1]*scale[1]), 
                int(box[2]*scale[0]), int(box[3]*scale[0])])
        return boxes_resize

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def draw_image(self, **kwargs):
        img_resize = super(RSCanvas, self).draw_image(**kwargs)
        shape = np.asarray(img_resize).shape

        img = np.zeros((shape[0], shape[1], 3), dtype=np.uint8)
        
        self._patches_bbox = rsvis.utils.patches_unordered.UnorderedPatches(np.asarray(img_resize), bbox=self.resize_bbox([b["box"] for b in self._boxes if isinstance(b, dict)]))
        
        if self._object_flag:
            img = imgtools.draw_box(img, [], self.resize_bbox([b["box"] for b in self._boxes if isinstance(b, dict)]), [self._color[b["label"]] for b in self._boxes if isinstance(b, dict)])            

        self._patches_grid = rsvis.utils.patches_ordered.OrderedPatches(np.asarray(img_resize), num_patches=self._grid, logger=self._logger)

        if self._grid_flag:            
            img = imgtools.get_grid_image(img, [], self._patches_grid.get_bbox())

        if self._selection:
            img = imgtools.draw_box(img, [], self.resize_bbox([self._selection["box"]]), [self._selection["color"]])

        img = Image.fromarray(imgtools.get_transparent_image(img))

        img_label = img_resize.copy()
        img_label.paste(img, (0, 0), img)
        return img_label
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_container(self, index=None):
        index = self._index_list() if index is None else index   
        self.get_object()
        self.set_img_container(self._data[index])

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    @property
    def obj(self):
        return self._object_flag

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img(self, img, objects=list()):
        self._img_size = [img.shape[1], img.shape[0]]
        super(RSCanvas, self).set_img(img)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_index_list(self):
        return self._index_list()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_area_event(self, index=0, **kwargs):
        self._area_event = index
        if self._area_event==1:
            self._object_flag = 0
            self.show_objects()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_grid(self, grid):
        self._grid = grid
        if self._grid_flag: 
            self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_class(self, label):
        self._label = label

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_grid(self):
        self._grid_flag = 0 if self._grid_flag else 1
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_objects(self):
        self._object_flag = 0 if self._object_flag  else 1
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_objects(self):
        return self._boxes

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_object(self):
        self._boxes = list()

        path = self.get_obj_path()
        if path:
            self.logger("[READ] '{}'".format(path))
            self._boxes = rsvis.utils.yaml.yaml_to_data(path)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def write_object(self):
        path = self.get_obj_path()

        self.logger("[SAVE] '{}'".format(path))
        rsvis.utils.yaml.data_to_yaml(path, self.get_objects())  
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def remove_object(self):
        if self._selection and self._patches_bbox:
            idx = self._patches_bbox.equal(self.resize_bbox([self._selection["box"]])[0])
            if idx is not None: 
                self._boxes.pop(idx)
                self._selection = dict()
            self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_obj_path(self):
        try: 
            path = self._get_obj_path(self._data[self._index_list()][0].path)
            if pathlib.Path(path).is_file():
                return path
        except TypeError:
            return

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def resize_event(self, event):
        ev = [event.y, event.x]

        ev[0] = ev[0] if ev[0] >= 0 else 0 
        ev[0] = ev[0] if ev[0] <= self._img_resize.size[1] else self._img_resize.size[1]
        
        ev[1] = ev[1] if ev[1] >= 0 else 0 
        ev[1] = ev[1] if ev[1] <= self._img_resize.size[0] else self._img_resize.size[0]
        
        return ev

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_bbox(self, event):
        ev = self.resize_event(event)
        return [ 
            min([self._point[0], ev[0]]),
            max([self._point[0], ev[0]]),
            min([self._point[1], ev[1]]),
            max([self._point[1], ev[1]])
        ]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def is_mouse_event(self, bbox):
        if not (bbox[1]-bbox[0] > self._mouse_sensitivity and bbox[3]-bbox[2] > self._mouse_sensitivity):
            return False
        return True

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def clear_selection(self):
        self._selection = dict()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_selection(self, bbox, resize=True):
        if resize:
            bbox = self.resize_bbox([bbox], inverted=True)[0]
        self._selection = {"box": bbox, "color": [150,150,150]}

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_boxes(self, bbox, resize=True):
        if resize:
            bbox = self.resize_bbox([bbox], inverted=True)[0]
        self._boxes.append({"box": bbox, "label": self._label})

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def new_popup(self, bbox, histogram=True):
        if bbox:
            img_container = self._img_container.copy()
            img_container.set_bbox(bbox)
            self._new_popup(title="Histogram", dtype="img", value=img_container, histogram=histogram) 

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_button_1_pressed(self, event):
        self.focus_set()
        self.clear_selection()
        ev = self.resize_event(event)
        self._point = [ev[0], ev[1]]
        if self._area_event==1:
            indices=list()
            self._patches_bbox.get_bbox_from_point(ev, indices=indices)
            if len(indices):
                self.set_selection(self._boxes[indices[0]]["box"], resize=False)
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_motion(self, event):
        self.focus_set()
        bbox = self.get_bbox(event)
        self.set_selection(bbox)
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_button_1_released(self, event):
        self.focus_set()
        bbox = self.get_bbox(event)
        if self.is_mouse_event(bbox):
            if self._area_event==0:
                patch = self._patches_bbox.get_patch(bbox=bbox)
                self.set_selection(bbox)
                self.new_popup(self._selection["box"])
            elif self._area_event==1:
                self.set_boxes(bbox)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_double_1_button(self, event):
        self.mouse_button_2_released(event, histogram=False)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_button_2_released(self, event, histogram=True):
        self.focus_set()
        ev = self.resize_event(event)
        if self._area_event==0:
            bbox = self.resize_bbox([self._patches_grid.get_bbox_from_point(ev)], inverted=True)[0]
        elif self._area_event==1:
            boxes = list()
            self._patches_bbox.get_bbox_from_point(ev, boxes=boxes)
            bbox = self.resize_bbox(boxes, inverted=True)[0] if len(boxes) else None
        self.new_popup(bbox, histogram=histogram)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_d(self, event, **kwargs):
        """Display the next image in given list."""
        index = self._index_list.next()
        self.set_container(index=index)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_a(self, event, **kwargs):
        """Display the previous image in given list.""",
        index = self._index_list.last()
        self.set_container(index=index)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_f(self, event=None):
        """Objects On/Off"""
        self.show_objects()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_g(self, event=None):
        "Remove the selected object."
        self.remove_object()