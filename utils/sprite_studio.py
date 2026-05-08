# utils/sprite_studio.py
# A desktop GUI utility to preview animations from extracted sprite frames.
# This tool helps in defining animation ranges for the Pocket Pet game.

import os
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk

class SpriteStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("Pocket Pi - Sprite Studio")
        self.root.geometry("400x550")
        self.root.configure(bg="#2c3e50")

        self.frames = []
        self.current_frame = 0
        self.is_playing = False
        self.anim_speed = 100 # ms
        
        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", background="#2c3e50", foreground="white", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=5)

        # Title
        title_label = tk.Label(self.root, text="SPRITE STUDIO", font=("Segoe UI", 18, "bold"), bg="#2c3e50", fg="#3498db")
        title_label.pack(pady=10)

        # Preview Area
        self.preview_canvas = tk.Canvas(self.root, width=256, height=256, bg="#34495e", highlightthickness=0)
        self.preview_canvas.pack(pady=10)
        self.preview_image = None

        # Folder Selection
        folder_frame = tk.Frame(self.root, bg="#2c3e50")
        folder_frame.pack(fill="x", padx=20, pady=5)
        
        self.path_var = tk.StringVar(value="assets/extracted_pokemon")
        ttk.Label(folder_frame, text="Folder:").pack(side="left")
        ttk.Entry(folder_frame, textvariable=self.path_var).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(folder_frame, text="...", width=3, command=self.browse_folder).pack(side="left")

        # Range Inputs
        range_frame = tk.Frame(self.root, bg="#2c3e50")
        range_frame.pack(fill="x", padx=20, pady=5)

        ttk.Label(range_frame, text="Start:").pack(side="left")
        self.start_var = tk.IntVar(value=0)
        ttk.Entry(range_frame, textvariable=self.start_var, width=5).pack(side="left", padx=5)

        ttk.Label(range_frame, text="End:").pack(side="left")
        self.end_var = tk.IntVar(value=10)
        ttk.Entry(range_frame, textvariable=self.end_var, width=5).pack(side="left", padx=5)

        # Speed Input
        ttk.Label(range_frame, text="FPS:").pack(side="left", padx=(10, 0))
        self.fps_var = tk.IntVar(value=10)
        ttk.Entry(range_frame, textvariable=self.fps_var, width=5).pack(side="left", padx=5)

        # Controls
        ctrl_frame = tk.Frame(self.root, bg="#2c3e50")
        ctrl_frame.pack(pady=20)

        self.play_btn = ttk.Button(ctrl_frame, text="▶ PLAY", command=self.toggle_play)
        self.play_btn.pack(side="left", padx=5)
        
        ttk.Button(ctrl_frame, text="⏹ STOP", command=self.stop_anim).pack(side="left", padx=5)
        ttk.Button(ctrl_frame, text="🔄 LOAD", command=self.load_range).pack(side="left", padx=5)
        ttk.Button(ctrl_frame, text="💾 EXPORT", command=self.export_animation).pack(side="left", padx=5)

        # Status
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(self.root, textvariable=self.status_var, bg="#2c3e50", fg="#bdc3c7", font=("Segoe UI", 9)).pack(side="bottom", pady=5)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)

    def load_range(self):
        self.stop_anim()
        path = self.path_var.get()
        start = self.start_var.get()
        end = self.end_var.get()
        
        self.frames = []
        try:
            for i in range(start, end + 1):
                fpath = os.path.join(path, f"{i}.png")
                if os.path.exists(fpath):
                    img = Image.open(fpath).convert("RGBA")
                    # Upscale for preview
                    img = img.resize((256, 256), Image.NEAREST)
                    self.frames.append(ImageTk.PhotoImage(img))
            
            if self.frames:
                self.current_frame = 0
                self.show_frame(0)
                self.status_var.set(f"Loaded {len(self.frames)} frames.")
            else:
                self.status_var.set("Error: No frames found in range.")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")

    def show_frame(self, idx):
        if self.frames:
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(128, 128, image=self.frames[idx])

    def toggle_play(self):
        if not self.frames:
            self.load_range()
            if not self.frames: return

        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_btn.config(text="⏸ PAUSE")
            self.animate()
        else:
            self.play_btn.config(text="▶ PLAY")

    def animate(self):
        if self.is_playing and self.frames:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.show_frame(self.current_frame)
            fps = self.fps_var.get()
            delay = int(1000 / max(1, fps))
            self.root.after(delay, self.animate)

    def export_animation(self):
        if not self.frames:
            self.status_var.set("Error: Nothing to export. Load frames first.")
            return
            
        path = self.path_var.get()
        start = self.start_var.get()
        end = self.end_var.get()
        
        # Collect original images
        images = []
        try:
            for i in range(start, end + 1):
                fpath = os.path.join(path, f"{i}.png")
                if os.path.exists(fpath):
                    images.append(Image.open(fpath).convert("RGBA"))
            
            if not images: return
            
            # Stitch horizontally
            w, h = images[0].size
            total_w = w * len(images)
            new_img = Image.new("RGBA", (total_w, h))
            
            for i, img in enumerate(images):
                new_img.paste(img, (i * w, 0))
            
            save_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")],
                initialfile=f"anim_{start}_{end}.png",
                title="Save Animation Strip"
            )
            
            if save_path:
                new_img.save(save_path)
                self.status_var.set(f"Exported to {os.path.basename(save_path)}")
                
        except Exception as e:
            self.status_var.set(f"Export Error: {str(e)}")

    def stop_anim(self):
        self.is_playing = False
        self.play_btn.config(text="▶ PLAY")
        self.current_frame = 0
        if self.frames:
            self.show_frame(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = SpriteStudio(root)
    root.mainloop()
