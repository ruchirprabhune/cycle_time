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
        self.points = []
        self.shaded_polygon = None

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
        self.save_button = tk.Button(root, text="Save ROI", command=self.save_roi)
        self.save_button.pack()

        self.clear_button = tk.Button(root, text="Clear", command=self.clear_roi)
        self.clear_button.pack()

    def on_click(self, event):
        if len(self.points) < 4:
            self.points.append((event.x, event.y))
            self.canvas.create_oval(event.x - 2, event.y - 2, event.x + 2, event.y + 2, fill="red")

        if len(self.points) == 4:
            self.shaded_polygon = self.canvas.create_polygon(
                self.points, fill="blue", stipple="gray50", outline="red"
            )
            messagebox.showinfo("ROI Selected", f"Points: {self.points}")

    def clear_roi(self):
        self.points = []
        self.canvas.delete(self.shaded_polygon)
        self.shaded_polygon = None

    def save_roi(self):
        if len(self.points) == 4:
            self.result_queue.put(self.points)
            self.root.destroy()
        else:
            messagebox.showwarning("Incomplete ROI", "Please select 4 points before saving.")


def run_tkinter(video_path, result_queue):
    root = tk.Tk()
    root.title("ROI Selector")
    ROISelectionApp(root, video_path, result_queue)
    root.mainloop()   