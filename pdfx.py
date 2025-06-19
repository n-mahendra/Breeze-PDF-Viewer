import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import fitz # PyMuPDF
from PIL import Image, ImageTk
import os
import CTkMessagebox # Assuming CTkMessagebox is installed (pip install CTkMessagebox)

class PDFViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Breeze PDF Viewer")
        self.root.geometry("1200x800")
        
        # --- Set Application Window Icon ---
        # IMPORTANT: You need an 'app_icon.ico' file in the same directory as your script,
        # or provide a full path to it. .ico is the preferred format for Windows.
        try:
            self.root.iconbitmap("app_icon.ico")
        except tk.TclError:
            print("Warning: Could not load 'app_icon.ico'. Ensure it's a valid .ico file and exists in the script's directory.")
            print("The application will run without a custom icon.")
        # --- End Icon Setup ---

        ctk.set_appearance_mode("System") # System, Dark, Light
        ctk.set_default_color_theme("blue") # blue, dark-blue, green

        # PDF-related variables
        self.pdf_document = None
        self.current_page = 0
        self.zoom_factor = 1.0
        self.rotation_angle = 0
        self.current_photo = None 

        # Function to load icons for toolbar buttons
        def load_icon(name):
            # Paths for light and dark mode icons. 
            # These should be in an 'icons' subdirectory relative to your script.
            light_path = os.path.join("icons", f"{name}_light.png")
            dark_path = os.path.join("icons", f"{name}_dark.png")
            
            if os.path.exists(light_path) and os.path.exists(dark_path):
                return ctk.CTkImage(
                    light_image=Image.open(light_path).resize((32, 32)),
                    dark_image=Image.open(dark_path).resize((32, 32)),
                    size=(32, 32)
                )
            elif os.path.exists(light_path):
                # Fallback to using the light icon for both if dark one is missing
                return ctk.CTkImage(
                    light_image=Image.open(light_path).resize((32, 32)),
                    dark_image=Image.open(light_path).resize((32, 32)), 
                    size=(32, 32)
                )
            else:
                print(f"Warning: Icon file not found for {name}. Searched in: {light_path}, {dark_path}")
                return None 

        # Main container frame
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.main_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

        # Toolbar frame
        self.toolbar = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.toolbar.pack(side=ctk.TOP, fill=ctk.X, pady=(0, 10), padx=5)

        # Toolbar buttons data (icon name and command function)
        buttons_data = [
            ("open_pdf", self.open_pdf),
            ("zoom_in", self.zoom_in),
            ("zoom_out", self.zoom_out),
            ("rotate", self.rotate_page),
            ("print", self.print_pdf),
            ("prev_page", self.prev_page),
            ("next_page", self.next_page),
            ("about_us", self.show_about)
        ]
        
        self.button_icons = {} # Store CTkImage objects to prevent garbage collection

        for icon_name, command in buttons_data:
            icon_image = load_icon(icon_name)
            
            # Define button colors for light and dark modes
            # ("light_mode_color", "dark_mode_color")
            button_fg_color = ("#E0E0E0", "#4A4A4A") # Light gray for light, dark gray for dark
            button_hover_color = ("#C0C0C0", "#5A5A5A") # Slightly darker for hover
            button_text_color = ("black", "white") # Black text on light button, white text on dark button

            if icon_image:
                self.button_icons[icon_name] = icon_image # Keep reference
                btn = ctk.CTkButton(self.toolbar, 
                                    text="", 
                                    image=icon_image,
                                    command=command, 
                                    width=40, 
                                    height=40,
                                    corner_radius=8,
                                    fg_color=button_fg_color,
                                    hover_color=button_hover_color,
                                    text_color=button_text_color) 
                btn.pack(side=ctk.LEFT, padx=5, pady=5)
            else:
                # Fallback to text button if icon not found
                btn = ctk.CTkButton(self.toolbar, 
                                    text=icon_name.replace("_", " ").title(), 
                                    command=command, 
                                    corner_radius=8,
                                    fg_color=button_fg_color,
                                    hover_color=button_hover_color,
                                    text_color=button_text_color)
                btn.pack(side=ctk.LEFT, padx=5, pady=5)

        # Page number input entry
        self.page_entry = ctk.CTkEntry(self.toolbar, width=60, placeholder_text="Page #", corner_radius=8)
        self.page_entry.pack(side=ctk.LEFT, padx=5, pady=5)
        self.page_entry.bind('<Return>', self.goto_page)

        # Page number label
        self.page_label = ctk.CTkLabel(self.toolbar, text="Page: 0/0", font=ctk.CTkFont(size=12, weight="bold"))
        self.page_label.pack(side=ctk.LEFT, padx=10, pady=5)

        # Theme switch (Dark Mode toggle)
        self.theme_switch = ctk.CTkSwitch(self.toolbar, text="Dark Mode", command=self.toggle_theme)
        self.theme_switch.pack(side=ctk.RIGHT, padx=10, pady=5)

        # Scrollable canvas for PDF display
        self.canvas_frame = ctk.CTkFrame(self.main_frame, corner_radius=10, fg_color="transparent")
        self.canvas_frame.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

        self.scroll_y = ctk.CTkScrollbar(self.canvas_frame, orientation=ctk.VERTICAL)
        self.scroll_y.pack(side=ctk.RIGHT, fill=ctk.Y)
        self.scroll_x = ctk.CTkScrollbar(self.canvas_frame, orientation=ctk.HORIZONTAL)
        self.scroll_x.pack(side=ctk.BOTTOM, fill=ctk.X)

        self.canvas = tk.Canvas(self.canvas_frame,
                                bg="#D3D3D3", # Light gray background for canvas
                                highlightthickness=0, # No border around canvas
                                xscrollcommand=self.scroll_x.set,
                                yscrollcommand=self.scroll_y.set)
        self.canvas.pack(fill=ctk.BOTH, expand=True) 

        self.scroll_x.configure(command=self.canvas.xview)
        self.scroll_y.configure(command=self.canvas.yview)

        # Bind mouse wheel for vertical scrolling across platforms
        self.canvas.bind("<MouseWheel>", self.on_mousewheel) # Windows
        self.canvas.bind("<Button-4>", self.on_mousewheel)  # Linux (scroll up)
        self.canvas.bind("<Button-5>", self.on_mousewheel) # Linux (scroll down)

        # Status bar at the bottom
        self.status_var = ctk.StringVar(value="Ready")
        self.status_bar = ctk.CTkLabel(self.main_frame,
                                       textvariable=self.status_var,
                                       fg_color=("gray85", "gray25"), # Background color for status bar
                                       text_color=("black", "white"), # Text color for status bar
                                       corner_radius=8,
                                       font=ctk.CTkFont(size=10),
                                       padx=10, pady=5,
                                       anchor=ctk.W) # Align text to the left
        self.status_bar.pack(side=ctk.BOTTOM, fill=ctk.X, pady=(10, 0), padx=5)

        # Bind window resize event to redraw page
        self.canvas.bind('<Configure>', self.on_resize)
        # Bind keyboard shortcuts
        self.bind_keys()
        
        # Initialize theme switch state based on current appearance mode
        if ctk.get_appearance_mode() == "Dark":
            self.theme_switch.select()
        else:
            self.theme_switch.deselect()

    def toggle_theme(self):
        """Toggles between light and dark appearance modes."""
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")
    
    def bind_keys(self):
        """Binds keyboard shortcuts for common actions."""
        self.root.bind('<Control-o>', lambda e: self.open_pdf())
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Left>', lambda e: self.prev_page())
        self.root.bind('<Right>', lambda e: self.next_page())
        self.root.bind('<Prior>', lambda e: self.prev_page()) # Page Up key
        self.root.bind('<Next>', lambda e: self.next_page()) # Page Down key

    def on_mousewheel(self, event):
        """Handles mouse wheel scrolling for the canvas, including page turning."""
        if not self.pdf_document:
            return

        # Determine scroll direction based on OS
        if event.num == 4: # Linux scroll up
            delta = 120
        elif event.num == 5: # Linux scroll down
            delta = -120
        else: # Windows
            delta = event.delta

        scroll_amount = -1 * (delta / 120) # Normalize delta to typical scroll units

        canvas_height = self.canvas.winfo_height()
        scroll_y = self.canvas.yview()
        scroll_y_pos = scroll_y[0] # Current top visible fraction
        scroll_y_end = scroll_y[1] # Current bottom visible fraction

        # Logic to change page if at the top/bottom and scrolling further
        if scroll_amount > 0 and scroll_y_end >= 0.95 and self.current_page < self.pdf_document.page_count - 1:
            self.next_page()
            self.canvas.yview_moveto(0.0) # Move to top of new page
            return
        elif scroll_amount < 0 and scroll_y_pos <= 0.05 and self.current_page > 0:
            self.prev_page()
            self.canvas.yview_moveto(1.0) # Move to bottom of new page
            return

        # Perform regular canvas scrolling
        self.canvas.yview_scroll(int(scroll_amount), "units")

    def open_pdf(self):
        """Opens a PDF file selected by the user."""
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            try:
                # Close previously opened document if any
                if self.pdf_document:
                    self.pdf_document.close()
                self.pdf_document = fitz.open(file_path)
                self.current_page = 0
                self.zoom_factor = 1.0
                self.rotation_angle = 0
                self.page_entry.delete(0, ctk.END)
                self.page_entry.insert(0, "1")
                self.display_page()
                self.status_var.set(f"Opened: {os.path.basename(file_path)}")
            except Exception as e:
                CTkMessagebox.CTkMessagebox(title="Error", message=f"Failed to open PDF: {str(e)}", icon="cancel")
                self.status_var.set("Error opening PDF")

    def display_page(self):
        """Displays the current page of the PDF document on the canvas."""
        if not self.pdf_document:
            self.canvas.delete("all")
            self.current_photo = None
            self.page_label.configure(text="Page: 0/0")
            self.page_entry.delete(0, ctk.END)
            self.status_var.set("No PDF loaded")
            return

        try:
            page = self.pdf_document[self.current_page]
            
            # Create a transformation matrix for zooming and rotation
            matrix = fitz.Matrix(self.zoom_factor, self.zoom_factor).prerotate(self.rotation_angle)
            
            # Get the page as a pixmap (image)
            pix = page.get_pixmap(matrix=matrix)
            
            # Convert pixmap to Pillow Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Convert Pillow Image to PhotoImage for Tkinter/CustomTkinter
            self.current_photo = ImageTk.PhotoImage(img) 

            self.canvas.delete("all") # Clear previous image
            
            # Calculate canvas dimensions and scroll region
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Set scroll region to accommodate the entire image, or canvas size if image is smaller
            scroll_width = max(pix.width, canvas_width)
            scroll_height = max(pix.height, canvas_height)
            self.canvas.config(scrollregion=(0, 0, scroll_width, scroll_height))
            
            # Center the image on the canvas if it's smaller than the canvas
            x_pos = max(0, (canvas_width - pix.width) // 2)
            y_pos = max(0, (canvas_height - pix.height) // 2)

            self.canvas.create_image(x_pos, y_pos, image=self.current_photo, anchor="nw")

            # Update page number label and entry
            self.page_label.configure(text=f"Page: {self.current_page + 1}/{self.pdf_document.page_count}")
            self.page_entry.delete(0, ctk.END)
            self.page_entry.insert(0, str(self.current_page + 1))
            self.status_var.set(f"Page {self.current_page + 1} displayed | Zoom: {self.zoom_factor:.1f}x | Rotation: {self.rotation_angle}°")
        except Exception as e:
            CTkMessagebox.CTkMessagebox(title="Error", message=f"Failed to display page: {str(e)}", icon="cancel")
            self.status_var.set("Error displaying page")

    def zoom_in(self):
        """Increases the zoom level of the current page."""
        if self.pdf_document:
            self.zoom_factor *= 1.2
            self.display_page()

    def zoom_out(self):
        """Decreases the zoom level of the current page."""
        if self.pdf_document:
            self.zoom_factor /= 1.2
            if self.zoom_factor < 0.1: # Prevent zooming out too much
                self.zoom_factor = 0.1
            self.display_page()

    def rotate_page(self):
        """Rotates the current page by 90 degrees clockwise."""
        if self.pdf_document:
            self.rotation_angle = (self.rotation_angle + 90) % 360
            self.display_page()

    def print_pdf(self):
        """Prints the current page of the PDF."""
        if not self.pdf_document:
            CTkMessagebox.CTkMessagebox(title="Warning", message="No PDF loaded to print!", icon="warning")
            self.status_var.set("No PDF loaded")
            return

        try:
            # Create a temporary PDF document containing only the current page for printing
            temp_pdf = fitz.open()
            temp_pdf.insert_pdf(self.pdf_document, from_page=self.current_page, to_page=self.current_page)
            
            temp_file = "temp_print_page.pdf" # Temporary file name
            temp_pdf.save(temp_file)
            temp_pdf.close()

            # Use OS-specific commands to print the PDF
            if os.name == "nt":  # For Windows
                os.startfile(temp_file, "print")
            else:  # For Linux/macOS (requires 'lpr' command-line tool)
                os.system(f"lpr {temp_file}")
            
            os.remove(temp_file) # Clean up the temporary file
            CTkMessagebox.CTkMessagebox(title="Success", message="Current page sent to printer!", icon="check")
            self.status_var.set("PDF sent to printer")
        except Exception as e:
            CTkMessagebox.CTkMessagebox(title="Error", message=f"Failed to print: {str(e)}\nEnsure you have a default PDF viewer/printer configured.", icon="cancel")
            self.status_var.set("Error printing PDF")

    def prev_page(self):
        """Navigates to the previous page if available."""
        if self.pdf_document and self.current_page > 0:
            self.current_page -= 1
            self.display_page()
            self.canvas.yview_moveto(0.0) # Reset scroll to top on page change

    def next_page(self):
        """Navigates to the next page if available."""
        if self.pdf_document and self.current_page < self.pdf_document.page_count - 1:
            self.current_page += 1
            self.display_page()
            self.canvas.yview_moveto(0.0) # Reset scroll to top on page change

    def goto_page(self, event=None):
        """Navigates to a specific page number entered by the user."""
        if not self.pdf_document:
            CTkMessagebox.CTkMessagebox(title="Warning", message="No PDF loaded!", icon="warning")
            self.status_var.set("No PDF loaded")
            return

        try:
            page_num_str = self.page_entry.get()
            if not page_num_str:
                CTkMessagebox.CTkMessagebox(title="Warning", message="Please enter a page number.", icon="warning")
                self.status_var.set("No page number entered")
                return

            page_num = int(page_num_str) - 1 # Convert to 0-indexed page number
            if 0 <= page_num < self.pdf_document.page_count:
                self.current_page = page_num
                self.display_page()
            else:
                CTkMessagebox.CTkMessagebox(title="Warning", message=f"Invalid page number. Please enter a number between 1 and {self.pdf_document.page_count}.", icon="warning")
                self.status_var.set("Invalid page number")
        except ValueError:
            CTkMessagebox.CTkMessagebox(title="Warning", message="Please enter a valid number for the page.", icon="warning")
            self.status_var.set("Invalid page number format")

    def on_resize(self, event):
        """Handles window resize events by redrawing the current page to fit."""
        if self.pdf_document:
            self.display_page()

    def show_about(self):
        """Displays an 'About Us' message box."""
        about_text = (
            "Breeze PDF Viewer\n\n"
            "Version: 1.0\n"
            "This application allows you to view, zoom, rotate, and print PDF files with a modern UI. "
            "Built with Python, PyMuPDF, Pillow, and CustomTkinter for a seamless user experience.\n\n"
            "© 2025 mahendra.uk. All rights reserved."
        )
        CTkMessagebox.CTkMessagebox(title="About Us", message=about_text, icon="info", option_1="OK")
        self.status_var.set("Displayed About Us information")


if __name__ == "__main__":
    app_root = ctk.CTk() # Create the CustomTkinter root window
    app = PDFViewer(app_root) # Initialize the PDFViewer application
    app_root.mainloop() # Start the Tkinter event loop
