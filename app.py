import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk, ImageEnhance
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ImageManipulatorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Image Manipulator")
        self.master.geometry("1200x800")

        self.image_path = None
        self.original_image = None
        self.current_image = None
        self.photo = None
        self.zoom_factor = 1.0

        self.create_widgets()

    def create_widgets(self):
        # Left frame for image display
        self.left_frame = ttk.Frame(self.master, padding="10")
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        self.canvas = tk.Canvas(self.left_frame, width=600, height=400)
        self.canvas.pack(expand=True, fill="both")
        self.canvas.bind("<Configure>", self.resize_image)

        # Right frame for sliders
        self.right_frame = ttk.Frame(self.master, padding="10")
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # Sliders
        self.brightness_slider = self.create_slider(self.right_frame, "Brightness", 0, 2, 1, self.update_image)
        self.contrast_slider = self.create_slider(self.right_frame, "Contrast", 0, 2, 1, self.update_image)
        self.saturation_slider = self.create_slider(self.right_frame, "Saturation", 0, 2, 1, self.update_image)
        self.edge_slider = self.create_slider(self.right_frame, "Edge Detection", 0, 10, 0, self.update_image)

        # Zoom buttons
        zoom_frame = ttk.Frame(self.right_frame)
        zoom_frame.pack(pady=10)
        ttk.Button(zoom_frame, text="Zoom In", command=self.zoom_in).pack(side="left", padx=5)
        ttk.Button(zoom_frame, text="Zoom Out", command=self.zoom_out).pack(side="left", padx=5)

        # Bottom frame for statistics and graphs
        self.bottom_frame = ttk.Frame(self.master, padding="10")
        self.bottom_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

        # Upload and Save buttons
        button_frame = ttk.Frame(self.master, padding="10")
        button_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        ttk.Button(button_frame, text="Upload Image", command=self.upload_image).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Save Image", command=self.save_image).pack(side="left", padx=5)

        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=1)
        self.master.rowconfigure(0, weight=3)
        self.master.rowconfigure(1, weight=1)

    def create_slider(self, parent, label, from_, to, default, command):
        frame = ttk.Frame(parent)
        frame.pack(pady=5, fill="x")
        ttk.Label(frame, text=label).pack(side="left")
        slider = ttk.Scale(frame, from_=from_, to=to, orient="horizontal", command=command)
        slider.set(default)
        slider.pack(side="right", expand=True, fill="x")
        return slider

    def upload_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if self.image_path:
            self.original_image = Image.open(self.image_path)
            self.current_image = self.original_image.copy()
            self.update_image()
            self.show_statistics()

    def update_image(self, *args):
        if self.original_image:
            # Apply color adjustments
            img = ImageEnhance.Brightness(self.original_image).enhance(self.brightness_slider.get())
            img = ImageEnhance.Contrast(img).enhance(self.contrast_slider.get())
            img = ImageEnhance.Color(img).enhance(self.saturation_slider.get())

            # Apply edge detection
            if self.edge_slider.get() > 0:
                img_array = np.array(img)
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                edges = cv2.Canny(gray, 100, 200)
                edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
                img_array = cv2.addWeighted(img_array, 1, edges, self.edge_slider.get() / 10, 0)
                img = Image.fromarray(img_array)

            self.current_image = img
            self.display_image()

    def display_image(self):
        if self.current_image:
            self.resize_image()

    def resize_image(self, event=None):
        if self.current_image:
            # Get canvas size
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Resize image to fit canvas while maintaining aspect ratio
            img_width, img_height = self.current_image.size
            scale = min(canvas_width / img_width, canvas_height / img_height)
            new_width = int(img_width * scale * self.zoom_factor)
            new_height = int(img_height * scale * self.zoom_factor)

            img = self.current_image.copy()
            img = img.resize((new_width, new_height), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)

            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(canvas_width // 2, canvas_height // 2, anchor="center", image=self.photo)

    def zoom_in(self):
        self.zoom_factor *= 1.2
        self.resize_image()

    def zoom_out(self):
        self.zoom_factor /= 1.2
        self.resize_image()

    def show_statistics(self):
        if self.original_image:
            for widget in self.bottom_frame.winfo_children():
                widget.destroy()

            # Color statistics
            img_array = np.array(self.original_image)
            r, g, b = img_array[:,:,0], img_array[:,:,1], img_array[:,:,2]
            avg_color = f"Average Color: R:{r.mean():.2f}, G:{g.mean():.2f}, B:{b.mean():.2f}"
            ttk.Label(self.bottom_frame, text=avg_color).pack()

            # Histogram
            fig, ax = plt.subplots(figsize=(8, 3))
            ax.hist(r.flatten(), bins=256, color='red', alpha=0.5)
            ax.hist(g.flatten(), bins=256, color='green', alpha=0.5)
            ax.hist(b.flatten(), bins=256, color='blue', alpha=0.5)
            ax.set_xlabel("Pixel Intensity")
            ax.set_ylabel("Count")
            ax.set_title("Color Histogram")

            canvas = FigureCanvasTkAgg(fig, master=self.bottom_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

    def save_image(self):
        if self.current_image:
            save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"),
                                                                ("JPEG files", "*.jpg"),
                                                                ("All files", "*.*")])
            if save_path:
                self.current_image.save(save_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageManipulatorApp(root)
    root.mainloop()