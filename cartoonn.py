import cv2
import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, Button, filedialog, Label, Frame, messagebox, StringVar, OptionMenu, Toplevel
from PIL import Image, ImageTk

# ==========================
#  ENHANCEMENT UTILITIES
# ==========================

def enhance_colors(image, gamma=1.2, vibrancy=25):
    invGamma = 1.0 / gamma
    table = np.array([(i / 255.0) ** invGamma * 255 for i in np.arange(256)]).astype("uint8")
    adjusted = cv2.LUT(image, table)
    hsv = cv2.cvtColor(adjusted, cv2.COLOR_RGB2HSV)
    hsv[..., 1] = cv2.add(hsv[..., 1], vibrancy)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

def bilateral_smooth(image, passes=2, sigma=150):
    for _ in range(passes):
        image = cv2.bilateralFilter(image, d=9, sigmaColor=sigma, sigmaSpace=sigma)
    return image

def sharpen_image(image):
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    return cv2.filter2D(image, -1, kernel)

# ==========================
#  IMPROVED STYLE FUNCTIONS
# ==========================

def watercolor_style(img):
    """Upgraded watercolor with texture and color wash simulation."""
    # Smooth + brighten
    smoothed = bilateral_smooth(img, passes=4, sigma=150)
    base = cv2.edgePreservingFilter(smoothed, flags=2, sigma_s=100, sigma_r=0.4)
    
    # Apply a gentle pastel tone mapping
    pastel = cv2.cvtColor(base, cv2.COLOR_RGB2LAB)
    pastel[..., 0] = cv2.equalizeHist(pastel[..., 0])
    pastel = cv2.cvtColor(pastel, cv2.COLOR_LAB2RGB)
    
    # Light texture overlay (simulate watercolor paper)
    noise = np.random.normal(0, 8, pastel.shape).astype(np.uint8)
    textured = cv2.addWeighted(pastel, 0.95, noise, 0.05, 0)
    
    # Soft sketchy outlines
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 40, 120)
    edges = cv2.GaussianBlur(edges, (3, 3), 0)
    edges = cv2.bitwise_not(edges)
    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    
    watercolor = cv2.bitwise_and(textured, edges)
    watercolor = enhance_colors(watercolor, gamma=1.25, vibrancy=15)
    
    return watercolor

def realistic_painting(img):
    """Enhanced realistic painting with depth, glow, and brush effect."""
    # Soft smoothing and detail enhancement
    base = cv2.edgePreservingFilter(img, flags=2, sigma_s=60, sigma_r=0.4)
    details = cv2.detailEnhance(base, sigma_s=120, sigma_r=0.15)
    
    # Add subtle glow for realistic tone
    blur = cv2.GaussianBlur(details, (21, 21), 0)
    glow = cv2.addWeighted(details, 1.1, blur, -0.1, 0)
    
    # Tone compression and warm shift
    lab = cv2.cvtColor(glow, cv2.COLOR_RGB2LAB)
    lab[..., 0] = cv2.equalizeHist(lab[..., 0])
    tone = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    
    # Optional light brush texture
    brush_texture = cv2.GaussianBlur(tone, (5, 5), 0)
    final = cv2.addWeighted(tone, 0.9, brush_texture, 0.1, 2)
    
    # Slight sharpen for clarity
    final = sharpen_image(final)
    final = enhance_colors(final, gamma=1.1, vibrancy=20)
    
    return final

def anime_style(img):
    smoothed = bilateral_smooth(img, passes=1, sigma=90)
    gray = cv2.cvtColor(smoothed, cv2.COLOR_RGB2GRAY)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 9, 2)
    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    blended = cv2.bitwise_and(smoothed, edges)
    return enhance_colors(blended, gamma=1.1, vibrancy=40)

def comic_effect(img):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    edges = cv2.Laplacian(gray, cv2.CV_8U, ksize=5)
    edges = cv2.bitwise_not(edges)
    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    smoothed = bilateral_smooth(img, passes=1, sigma=120)
    comic = cv2.bitwise_and(smoothed, edges)
    comic = sharpen_image(comic)
    return enhance_colors(comic, gamma=1.0, vibrancy=35)

def pop_art(img):
    Z = np.float32(img.reshape((-1, 3)))
    _, labels, centers = cv2.kmeans(Z, 5, None, 
        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0),
        10, cv2.KMEANS_RANDOM_CENTERS)
    centers = np.uint8(centers)
    quantized = centers[labels.flatten()].reshape(img.shape)
    edges = cv2.Canny(cv2.cvtColor(img, cv2.COLOR_RGB2GRAY), 100, 200)
    edges = cv2.bitwise_not(edges)
    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    pop = cv2.bitwise_and(quantized, edges)
    return enhance_colors(pop, gamma=0.9, vibrancy=50)

# ==========================
#  MAIN CARTOONIFY FUNCTION
# ==========================

def cartoonify(image_path, style):
    original = cv2.imread(image_path)
    if original is None:
        messagebox.showerror("Error", "❌ Could not open image. Please choose a valid file.")
        return None

    img = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (800, 800))

    if style == "Anime":
        cartoon = anime_style(img)
    elif style == "Watercolor":
        cartoon = watercolor_style(img)
    elif style == "Realistic Painting":
        cartoon = realistic_painting(img)
    elif style == "Comic Effect":
        cartoon = comic_effect(img)
    elif style == "Pop Art":
        cartoon = pop_art(img)
    else:
        cartoon = enhance_colors(img)

    return cartoon

def show_popup(title, message):
    popup = Toplevel()
    popup.title(title)
    popup.geometry("350x200")
    popup.config(bg="#2C2C54")
    popup.resizable(False, False)
    Label(popup, text=title, font=("Comic Sans MS", 18, "bold"), fg="#FDA7DF", bg="#2C2C54").pack(pady=15)
    Label(popup, text=message, font=("Arial", 11), fg="white", bg="#2C2C54", wraplength=300, justify="center").pack(pady=10)
    Button(popup, text="OK", command=popup.destroy, bg="#706FD3", fg="white", font=("Arial", 11, "bold"),
           padx=20, pady=6, relief="flat", activebackground="#5758BB").pack(pady=10)

# ==========================
#  DISPLAY AND SAVE
# ==========================

def show_and_save(image_path, cartoon_image, style):
    plt.figure(figsize=(8, 6))
    plt.imshow(cartoon_image)
    plt.axis('off')
    plt.title(f"✨ {style} Cartoonified ✨")
    plt.show()

    save_path = image_path.split('.')[0] + f"_cartoonified_{style.lower()}.jpg"
    cv2.imwrite(save_path, cv2.cvtColor(cartoon_image, cv2.COLOR_RGB2BGR))
    show_popup("Image Saved!", f"✅ {style} style saved successfully!\n\nSaved at:\n{save_path}")

# ==========================
#  TKINTER GUI
# ==========================

def choose_image():
    file_path = filedialog.askopenfilename(
        title="Select an image to cartoonify",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.gif")]
    )
    if not file_path:
        show_popup("No File", "⚠️ Please choose an image file first.")
        return

    style = selected_style.get()
    cartoon = cartoonify(file_path, style)
    if cartoon is not None:
        show_and_save(file_path, cartoon, style)

def main():
    root = Tk()
    root.title("🎨 Ultimate Cartoonify Studio 🎨")
    root.geometry("520x400")
    root.configure(bg="#1B1464")

    # Frame with rounded feel
    frame = Frame(root, bg="#3B3B98", padx=20, pady=30, relief="ridge", borderwidth=4)
    frame.pack(pady=50)

    Label(frame, text="🖌️ Cartoonify Your Image", font=("Comic Sans MS", 20, "bold"),
          fg="#FDA7DF", bg="#3B3B98").pack(pady=10)

    global selected_style
    selected_style = StringVar()
    selected_style.set("Anime")

    styles = ["Anime", "Watercolor", "Realistic Painting", "Comic Effect", "Pop Art"]

    Label(frame, text="Choose Style:", font=("Arial", 12, "bold"), fg="white", bg="#3B3B98").pack(pady=5)
    OptionMenu(frame, selected_style, *styles).pack(pady=5)

    Button(frame, text="Choose Image & Cartoonify", command=choose_image,
           bg="#9B59B6", fg="white", font=("Arial", 13, "bold"),
           padx=25, pady=10, relief="flat", activebackground="#8E44AD", borderwidth=0).pack(pady=20)

    Label(frame, text="✨ Powered by OpenCV + K-Means ✨",
          font=("Arial", 9, "italic"), fg="#D1CCC0", bg="#3B3B98").pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
