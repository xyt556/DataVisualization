# ===========================================================================
#   topwindow.py -------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from PIL import Image, ImageTk
from tkinter import Toplevel, ttk, Button, Canvas, Label, TOP, X, NW, N, W, S, E

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TopWindow(Toplevel):
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, title="Box", command=None, dtype="msg", value=""):
        Toplevel.__init__(self)
        self.wm_title(title)

        if dtype=="msg":
            self.set_msg(value)
        elif dtype=="img":
            if isinstance(value, list):
                self.set_grid_img(value)
            else: 
                self.set_img(value)

        self.columnconfigure(0, pad=3)
        self.columnconfigure(1, pad=3)
        self.rowconfigure(0, pad=3)
        self.rowconfigure(1, pad=3)

        button = ttk.Button(self, text="OK", 
            command=lambda toplevel=self, title=title: command(toplevel, title)
        )
        button.grid(row=1, column=0, columnspan=2)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_msg(self, msg):
        frame = ttk.Label(self, text=msg)# anchor='w' ttk?
        frame.grid(row=0, column=0, columnspan=2, sticky=N+S+W+E)
        # frame.pack(side=TOP, fill=X, pady=10)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img(self, img):
        self.frame_img = ImageTk.PhotoImage(image=Image.fromarray(img))

        frame = ttk.Label(self, image=self.frame_img)
        frame.grid(row=0, column=0, columnspan=2, sticky=N+S+W+E)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_grid_img(self, img):
        frame = ttk.Frame(self)
        
        self.frame_img = list()

        for index, item in enumerate(img):
            self.frame_img.append(ImageTk.PhotoImage(image=Image.fromarray(item)))

            frame_obj = ttk.Label(self, image=self.frame_img[-1])
            frame_obj.grid(row=0, column=index, sticky=N+S+W+E)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    # def set_canvas(self, img):
    #     canvas = Canvas(self, bg="black")
    #     canvas.create_image(0, 0, image=self.frame_img, anchor=NW)
    #     canvas.grid(row=0, column=0, sticky=N+S+W+E)