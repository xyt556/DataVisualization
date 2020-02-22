# ===========================================================================
#   rsshow.py ---------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.__init__
import rsvis.tools.rsshowui
import rsvis.tools.imagestats
import rsvis.tools.imgcontainer
import rsvis.tools.heightmap
import rsvis.tools.imgtools

import cv2
import numpy as np
from matplotlib import pyplot as plt
import tifffile
import PIL
import pathlib
import shutil

# @todo[change]: msi channels a = [2,1,6], b = [1,2,4], c = [1,5,4]

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def to_list(*args):
    return (x if isinstance(x, list) or x is None else [x] for x in args)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_img_info(img):
    if len(img.shape) != 3: 
        img_new = np.ndarray((*img.shape,1), dtype=img.dtype)
        img_new[:,:,0] = img
        img = img_new
    return (img.shape[0], img.shape[1], img.shape[2], img.shape[0] * img.shape[1], np.min(img), np.max(img))

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_histogram(img, **kwargs):
    img = get_masked_image(img, **kwargs) 

    fig = plt.figure(dpi=256, facecolor='w', edgecolor='k')
    ax = fig.add_subplot(111)

    _ , _ , img_channel, img_pixel, _, _ = get_img_info(img)
    for i in range(img_channel):
        histr = cv2.calcHist([img],[i],None,[256],[0,256]) / img_pixel
        plt.plot(histr)
        
    ax.set_xlim([0,256])
    # ax.legend(loc = 'upper left')
    return get_nparray_from_fig(fig)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_nparray_from_fig(fig):  
    fig.canvas.draw()
    data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    return data

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_stats(img, **kwargs):
    img = get_masked_image(img, **kwargs)

    fig = plt.figure(dpi=256, facecolor='w', edgecolor='k')
    ax = fig.add_subplot(111)

    _ , _ , img_channel, img_pixel, _, _ = get_img_info(img)
    for i in range(img_channel):
        vector = img[:,:,i].flatten()
        hist, _ = np.histogram(vector , 256, [0,256])

        cdf = hist.cumsum()
        cdf_normalized = cdf * hist.max()/ cdf.max() / img_pixel
        
        histr = cv2.calcHist([img],[i],None,[256],[0,256]) / img_pixel
        plt.plot(histr)
        plt.plot(cdf_normalized, color = 'b')
    
    ax.set_xlim([0,256])
    # ax.legend(loc = 'upper left')
    return get_nparray_from_fig(fig)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
# get the area of two points
def get_masked_image(img, ref_point=None):
    if ref_point:
        return img[
            ref_point[0][0]:ref_point[1][0],
            ref_point[0][1]:ref_point[1][1]
        ]
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_label_image(img, label, value=204, equal=True):
    label_list = list()
    img_label = img.copy()
    for c in range(img.shape[-1]):
        if equal:
            mask = np.ma.masked_where(label[...,-1] != value, img[...,c])
        else:
            mask = np.ma.masked_where(label[...,-1] == value, img[...,c])
                    
        np.ma.set_fill_value(mask, 0)
        img_label[:,:,c] = mask.filled()
        #label_list.append(mask.compressed())
    return img_label

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def blubb(img, **kwargs):    
    foo = rsvis.tools.imagestats.ImageStats(
            path="A:\\VirtualEnv\\dev-rsvis\\src\\rsvis\\tmpchlgw4dk.json" 
        )
    dim = img.shape
    img = img.reshape(-1, dim[-1])
    img = np.apply_along_axis(foo.get_probability_c, -1, img)
    img = img.reshape( dim[0], dim[1], 1)
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_image(path, spec, labels=dict(), msi=list(), scale=100):
    
    if path.endswith(".tif"):
        img = tifffile.imread(path)
    else:
        img = np.asarray(PIL.Image.open(path))

    img = rsvis.tools.imgtools.resize_img(img, scale)

    if spec == "label":
        img = rsvis.tools.imgtools.labels_to_image(img, labels)

    if spec in ["label", "height", "msi"]:
        img = rsvis.tools.imgtools.project_data_to_img(img)

    if spec == "msi" and msi:
        img = np.stack((img[:,:,msi[0][0]], img[:,:,msi[0][1]], img[:,:,msi[0][2]]), axis=2)

    img =  rsvis.tools.imgtools.stack_image_dim(img)

    return img

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class PathCreator():

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, dest_dir, dest_basename, regex=".*", group=0):
        self._dest_dir = pathlib.Path(dest_dir)
        self._dest_basename = dest_basename
        self._research = rsvis.utils.regex.ReSearch(regex, group)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __call__(self, path):
        return self._dest_dir / self._dest_basename.format(self._research(pathlib.Path(path).stem))

# inheritance index ?
class ObjIndex(object):

    def __init__(self, obj):
        self._obj = obj

        try:
            self._index = rsvis.tools.index.Index(len(obj))
        except AttributeError:
            print("Object does not have a iterator.")
            raise

    def __call__(self):
        index = self._index()
        self._index.next()
        return self._obj[index]

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def save_image(dest,  img):
    rsvis.__init__._logger.debug("Save img to '{}'".format(dest))
    tifffile.imwrite(dest, img)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def copy_image(path,  dest):
    rsvis.__init__._logger.debug("Save img to '{}'".format(dest))
    shutil.copy2(path, dest)    

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def rsshow(files, specs, dest_dir, dest_basename, io, labels=dict(), msi=list(), resize=100):
    
    load = lambda path, spec: get_image(path, spec, labels=labels, msi=msi, scale=resize)

    get_path = PathCreator(dest_dir, dest_basename, *io)
    save = lambda path, img: save_image(get_path(path), img)
    copy = lambda path: copy_image(path, get_path(path))

    import rsvis.tools.imgcontainer
    img_set = list()
    for f_set in files:
        img = rsvis.tools.imgcontainer.ImgListContainer(load=load)
        for f, s  in zip(f_set, specs):
            live = False if s == "label" else True
            img.append(path = f, spec=s, live=live)
        img_set.append(img)

    label_index = ObjIndex(rsvis.tools.imgtools.project_dict_to_img(labels.copy())) 
   
    keys = {
        "key_e" : lambda obj: obj.set_img(
            obj.get_img(),
            show=True
        ),
        "key_n" : lambda obj: obj.set_img(
            rsvis.tools.imgtools.raise_contrast( np.array(obj.get_window_img())), 
            show=True
        ),
        "key_c": lambda obj: rsvis.tools.heightmap.main(
            np.array(obj.get_window_img()), 
            obj.get_img_from_spec("height"),
            normals=True,
            mesh=True
        ),       
        "key_v": lambda obj: rsvis.tools.heightmap.main(
            np.array(obj.get_window_img()),
            obj.get_img_from_spec("height"), 
            obj.get_img_from_spec("label"),
            normals=True,
            mesh=True,
            ccviewer=False
        ),
        "key_b": lambda obj: obj.set_img(
            rsvis.tools.heightmap.get_normal_image(
                np.array(obj.get_window_img()), 
                obj.get_img_from_spec("height")
            ),
            show=True
        ), 
        "key_l": lambda obj: obj.set_img(
            rsvis.tools.rsshow.get_label_image(
                obj.get_img(), 
                obj.get_img_from_spec("label"), 
                value=label_index(),
                equal=True),                 
            show=True
        ),
        "key_p": lambda obj: save(obj.get_img(path=True), np.array(obj.get_window_img())
        ),
        "key_o": lambda obj: copy(obj.get_img(path=True))
    }

    ui = rsvis.tools.rsshowui.RSShowUI(img_set, keys=keys)
    ui.imshow(wait=True)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def test_code(files, types):

    print("Test to_list():")
    a, b, c = to_list("hallo", None, ["hallo", "du"])
    print(a, b, c)

    import rsvis.tools.objcontainer    
    a = rsvis.tools.objcontainer.ObjContainer(np.ones((2,3)))
    print(a)

    b = rsvis.tools.objcontainer.ObjContainer(None)
    print(b)

    b.obj = np.ones((2,3))
    print(b)

    import rsvis.tools.imgcontainer
    c = rsvis.tools.imgcontainer.ImgContainer( path="A:\\Datasets\\Data-Fusion-Contest-2019\\Train-Track1-RGB\\Track1-RGB\\JAX_004_006_RGB.tif")
    print(c.load())
    print(c)

    import rsvis.tools.imgcontainer
    d= list()
    for f_set in files:
        e = rsvis.tools.imgcontainer.ImgListContainer()
        for f,t  in zip(f_set,types):
            e.append(path = f, spec=t)
        d.append(e)

    import rsvis.tools.index
    f = rsvis.tools.index.Index(7,3)
    print(f)
    f += 1
    f -= 1
    f = f + 2
    print(f)