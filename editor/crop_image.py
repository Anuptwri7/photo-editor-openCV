from PIL import Image
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

def crop_image():
    # Ask user to select an image
    file_path = filedialog.askopenfilename(
        title="Select Image",
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
    )
    if not file_path:
        return

    img = Image.open(file_path)
    print(f"Loaded image: {img.width}x{img.height} pixels")

    # Ask user for crop width and height
    width = simpledialog.askinteger("Crop Width", f"Enter crop WIDTH in pixels (max {img.width}):", minvalue=1, maxvalue=img.width)
    height = simpledialog.askinteger("Crop Height", f"Enter crop HEIGHT in pixels (max {img.height}):", minvalue=1, maxvalue=img.height)

    if not width or not height:
        messagebox.showerror("Error", "Invalid width or height")
        return

    # Crop from top-left corner
    cropped_img = img.crop((0, 0, width, height))

    # Save the cropped image
    save_path = filedialog.asksaveasfilename(
        title="Save Cropped Image",
        defaultextension=".png",
        filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")]
    )
    if save_path:
        cropped_img.save(save_path)
        messagebox.showinfo("Success", f"Image cropped and saved as {save_path}")

# GUI setup
root = tk.Tk()
root.withdraw()  # hide main window

crop_image()
