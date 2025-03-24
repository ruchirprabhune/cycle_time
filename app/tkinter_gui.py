import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import multiprocessing

class ROISelectionApp:
    def __init__(self, root, video_path, result_queue):
        self.root = root
        self.video_path = video_path
        self.result_queue = result_queue
        self.roi_count = 0  # To track ROI selection
        self.points = []
        self.rois = []  # List to store ROIs
        self.shaded_polygons = []
        self.colors = ["blue", "green"]  # Different colors for two ROIs

        # Load video frame
        self.cap = cv2.VideoCapture(video_path)
        ret, self.frame = self.cap.read()
        if not ret:
            messagebox.showerror("Error", "Could not read the first frame.")
            root.quit()
            return

        self.frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        self.frame_image = ImageTk.PhotoImage(image=Image.fromarray(self.frame_rgb))

        # Canvas setup
        self.canvas = tk.Canvas(root, width=self.frame.shape[1], height=self.frame.shape[0])
        self.canvas.pack()
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.frame_image)

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_click)

        # Add buttons
        self.save_button = tk.Button(root, text="Save ROIs", command=self.save_rois)
        self.save_button.pack()

        self.clear_button = tk.Button(root, text="Clear", command=self.clear_roi)
        self.clear_button.pack()

    def on_click(self, event):
        if len(self.points) < 4:
            self.points.append((event.x, event.y))
            self.canvas.create_oval(event.x - 2, event.y - 2, event.x + 2, event.y + 2, fill="red")

        if len(self.points) == 4:
            color = self.colors[self.roi_count % 2]  # Alternate between blue and green
            polygon = self.canvas.create_polygon(
                self.points, fill=color, stipple="gray50", outline="red"
            )
            self.shaded_polygons.append(polygon)
            self.rois.append(self.points.copy())  # Store ROI
            self.points = []  # Reset for next ROI
            self.roi_count += 1
            
            if self.roi_count == 2:
                messagebox.showinfo("ROIs Selected", f"Both ROIs Selected: {self.rois}")

    def clear_roi(self):
        self.points = []
        for polygon in self.shaded_polygons:
            self.canvas.delete(polygon)
        self.shaded_polygons = []
        self.rois = []
        self.roi_count = 0

    def save_rois(self):
        if len(self.rois) >= 1:
            self.result_queue.put(self.rois)
            self.root.destroy()
        else:
            messagebox.showwarning("Incomplete ROIs", "Please select at least 1 region before saving.")


def run_tkinter(video_path, result_queue):
    root = tk.Tk()
    root.title("ROI Selector")
    ROISelectionApp(root, video_path, result_queue)
    root.mainloop()



def run_tkinter(video_path, result_queue):
    root = tk.Tk()
    root.title("ROI Selector")
    ROISelectionApp(root, video_path, result_queue)
    root.mainloop()   
