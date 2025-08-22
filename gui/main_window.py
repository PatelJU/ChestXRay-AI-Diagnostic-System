import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import os
import numpy as np
import threading

class MainWindow:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.current_image_path = None
        self.current_report = None
        self.setup_styles()
        self.create_widgets()
        self.setup_layout()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'), foreground='#34495e')
        style.configure('Info.TLabel', font=('Arial', 10), foreground='#7f8c8d')
        style.configure('Primary.TButton', font=('Arial', 11, 'bold'))

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.header_frame = ttk.Frame(self.main_frame)
        self.title_label = ttk.Label(self.header_frame, text="ChestVision AI - Pre-trained Analysis", style='Title.TLabel')
        self.subtitle_label = ttk.Label(self.header_frame, text="Using pre-trained models for chest X-ray disease prediction", style='Subtitle.TLabel')
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_label = ttk.Label(self.status_frame, text="Ready - Load an X-ray image", style='Info.TLabel')
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding="10")
        self.load_button = ttk.Button(self.control_frame, text="📁 Load X-Ray Image", command=self.load_image, style='Primary.TButton')
        self.analyze_button = ttk.Button(self.control_frame, text="🔬 Analyze Image", command=self.analyze_image, state='disabled', style='Primary.TButton')
        self.save_report_button = ttk.Button(self.control_frame, text="💾 Save Report", command=self.save_report, state='disabled')
        self.clear_button = ttk.Button(self.control_frame, text="🗑️ Clear", command=self.clear_analysis)
        self.progress = ttk.Progressbar(self.control_frame, mode='indeterminate')
        self.content_frame = ttk.Frame(self.main_frame)
        self.image_frame = ttk.LabelFrame(self.content_frame, text="X-Ray Image", padding="10")
        self.image_label = ttk.Label(self.image_frame, text="No image loaded")
        self.results_frame = ttk.LabelFrame(self.content_frame, text="Analysis Results", padding="10")
        self.results_notebook = ttk.Notebook(self.results_frame)
        self.summary_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.summary_frame, text="Summary")
        self.summary_text = scrolledtext.ScrolledText(self.summary_frame, height=8, width=50, font=('Consolas', 10), state='disabled')
        self.report_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.report_frame, text="Detailed Report")
        self.report_text = scrolledtext.ScrolledText(self.report_frame, height=20, width=80, font=('Consolas', 9), state='disabled')
        self.prob_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.prob_frame, text="Probabilities")
        self.prob_canvas = tk.Canvas(self.prob_frame, height=300, bg='white')
        self.prob_scrollbar = ttk.Scrollbar(self.prob_frame, orient="vertical", command=self.prob_canvas.yview)
        self.prob_canvas.configure(yscrollcommand=self.prob_scrollbar.set)
        # Heatmap analysis frame
        self.heatmap_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.heatmap_frame, text="Heatmap Analysis")
        
        # Dropdown for selecting heatmap view
        self.heatmap_selector = ttk.Combobox(self.heatmap_frame, state="readonly")
        self.heatmap_selector.grid(row=0, column=0, sticky='ew', pady=5)
        self.heatmap_selector.bind("<<ComboboxSelected>>", self.update_heatmap_display)
        
        # Label for displaying selected heatmap
        self.heatmap_label = ttk.Label(self.heatmap_frame, text="Heatmap will appear here after analysis")
        self.heatmap_label.grid(row=1, column=0, sticky='nsew')
        
        self.heatmap_frame.grid_rowconfigure(1, weight=1)
        self.heatmap_frame.grid_columnconfigure(0, weight=1)

    def setup_layout(self):
        self.main_frame.grid(row=0, column=0, sticky='nsew')
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        self.title_label.grid(row=0, column=0, sticky='w')
        self.subtitle_label.grid(row=1, column=0, sticky='w')
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        self.status_label.grid(row=0, column=0, sticky='w')
        self.control_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        self.load_button.grid(row=0, column=0, padx=(0, 5), pady=5)
        self.analyze_button.grid(row=0, column=1, padx=5, pady=5)
        self.save_report_button.grid(row=0, column=2, padx=5, pady=5)
        self.clear_button.grid(row=0, column=3, padx=(5, 0), pady=5)
        self.progress.grid(row=1, column=0, columnspan=4, sticky='ew', pady=(10, 0))
        self.content_frame.grid(row=3, column=0, columnspan=2, sticky='nsew')
        self.main_frame.grid_rowconfigure(3, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.image_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        self.results_frame.grid(row=0, column=1, sticky='nsew', padx=(5, 0))
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=2)
        self.image_label.grid(row=0, column=0, sticky='nsew')
        self.image_frame.grid_rowconfigure(0, weight=1)
        self.image_frame.grid_columnconfigure(0, weight=1)
        self.results_notebook.grid(row=0, column=0, sticky='nsew')
        self.results_frame.grid_rowconfigure(0, weight=1)
        self.results_frame.grid_columnconfigure(0, weight=1)
        self.summary_text.grid(row=0, column=0, sticky='nsew')
        self.summary_frame.grid_rowconfigure(0, weight=1)
        self.summary_frame.grid_columnconfigure(0, weight=1)
        self.report_text.grid(row=0, column=0, sticky='nsew')
        self.report_frame.grid_rowconfigure(0, weight=1)
        self.report_frame.grid_columnconfigure(0, weight=1)
        self.prob_canvas.grid(row=0, column=0, sticky='nsew')
        self.prob_scrollbar.grid(row=0, column=1, sticky='ns')
        self.prob_frame.grid_rowconfigure(0, weight=1)
        self.prob_frame.grid_columnconfigure(0, weight=1)
        # Heatmap frame layout is handled in the creation section

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
        if file_path:
            self.current_image_path = file_path
            img = Image.open(file_path)
            img = img.resize((400, 400), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            self.image_label.configure(image=self.photo)
            self.status_label.configure(text="Image loaded. Ready for analysis.")
            self.analyze_button.configure(state='normal')

    def analyze_image(self):
        if not self.current_image_path:
            messagebox.showerror("Error", "No image loaded")
            return
        
        # Disable analyze button during processing
        self.analyze_button.configure(state='disabled')
        self.progress.start(10)  # Start with specific speed
        self.status_label.configure(text="Analyzing image...")
        self.root.update_idletasks()  # Force UI update
        
        # Run analysis in a separate thread
        thread = threading.Thread(target=self._analyze_thread, daemon=True)
        thread.start()
    
    def _analyze_thread(self):
        """Run analysis in a separate thread to keep UI responsive"""
        try:
            # Call analyze method and handle both basic and enhanced versions
            result = self.app.analyze(self.current_image_path)
            
            # Schedule UI updates in main thread
            self.root.after(0, self._handle_analysis_result, result)
        except Exception as e:
            self.root.after(0, self._handle_analysis_error, str(e))
    
    def _handle_analysis_result(self, result):
        """Handle analysis result in main thread"""
        if result is None:
            self.progress.stop()
            self.analyze_button.configure(state='normal')
            return
        
        # Handle different result formats
        if isinstance(result, dict):  # Enhanced version
            self.display_results(result)
        else:  # Basic version (tuple)
            predictions, summary, report, overlay = result
            self.current_report = report
            self.current_predictions = predictions
            self.display_summary(summary)
            self.display_report(report)
            self.display_probabilities(predictions)
            self.display_heatmap(overlay)
        
        self.progress.stop()
        self.status_label.configure(text="Analysis complete")
        self.save_report_button.configure(state='normal')
        self.analyze_button.configure(state='normal')
    
    def _handle_analysis_error(self, error_msg):
        """Handle analysis error in main thread"""
        self.progress.stop()
        self.status_label.configure(text="Analysis failed")
        self.analyze_button.configure(state='normal')
        messagebox.showerror("Analysis Error", f"An error occurred during analysis: {error_msg}")

    def save_report(self):
        if not self.current_report:
            messagebox.showerror("Error", "No report to save")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf"), ("Text files", "*.txt")])
        if file_path:
            if file_path.lower().endswith('.pdf'):
                # Use the new professional medical report generator
                try:
                    # Format predictions for the new generator
                    formatted_predictions = []
                    for disease_name, confidence in self.current_predictions.items():
                        formatted_predictions.append({
                            'disease_name': disease_name,
                            'confidence': confidence * 100  # Convert to percentage
                        })
                    
                    # Get heatmaps and original image if available
                    heatmaps = None
                    original_img = None
                    if hasattr(self, 'heatmap_data') and self.heatmap_data:
                        heatmaps = self.heatmap_data.get('heatmaps', None)
                        original_img = self.heatmap_data.get('original_img', None)
                    
                    # Generate professional medical report PDF with heatmap circle overlays
                    output_path = self.app.pdf_generator.generate_report(
                        predictions=formatted_predictions,
                        image_path=self.current_image_path,
                        output_path=file_path,
                        scan_type="Chest X-Ray Analysis",
                        heatmaps=heatmaps,
                        original_img=original_img
                    )
                    
                    if output_path:
                        messagebox.showinfo("Success", "Professional Medical Report saved successfully!")
                    else:
                        messagebox.showerror("Error", "Failed to generate PDF report")
                except Exception as e:
                    messagebox.showerror("PDF Generation Error", f"An error occurred while generating the PDF:\n\n{str(e)}")
            else:
                # Save as text file
                with open(file_path, 'w') as f:
                    f.write(self.current_report)
                messagebox.showinfo("Success", "Text report saved successfully")

    def clear_analysis(self):
        self.current_image_path = None
        self.current_report = None
        self.image_label.configure(image=None, text="No image loaded")
        self.summary_text.configure(state='normal')
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.configure(state='disabled')
        self.report_text.configure(state='normal')
        self.report_text.delete(1.0, tk.END)
        self.report_text.configure(state='disabled')
        self.prob_canvas.delete('all')
        self.heatmap_label.configure(image=None, text="Heatmap will appear here after analysis")
        self.analyze_button.configure(state='disabled')
        self.save_report_button.configure(state='disabled')
        self.status_label.configure(text="Ready - Load an X-ray image")

    def display_summary(self, summary):
        self.summary_text.configure(state='normal')
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, summary)
        self.summary_text.configure(state='disabled')

    def display_report(self, report):
        self.report_text.configure(state='normal')
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, report)
        self.report_text.configure(state='disabled')

    def display_probabilities(self, predictions):
        self.prob_canvas.delete('all')
        sorted_preds = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
        y = 10
        max_width = 300
        for disease, prob in sorted_preds:
            bar_width = int(prob * max_width)
            self.prob_canvas.create_rectangle(10, y, 10 + bar_width, y + 20, fill='blue')
            self.prob_canvas.create_text(20 + bar_width, y + 10, text=f"{disease}: {prob*100:.1f}%", anchor='w')
            y += 30
        self.prob_canvas.configure(scrollregion=self.prob_canvas.bbox('all'))

    def display_heatmap(self, heatmap_data):
        self.heatmap_data = heatmap_data  # Store for use in save_report
        options = ['Combined Average'] + heatmap_data['sorted_diseases']
        self.heatmap_selector['values'] = options
        if options:
            self.heatmap_selector.current(0)
            self.update_heatmap_display(None)

    def update_heatmap_display(self, event=None):
        if not hasattr(self, 'heatmap_data') or not self.heatmap_data:
            return
            
        selection = self.heatmap_selector.get()
        original_img = self.heatmap_data['original_img']
        heatmaps = self.heatmap_data['heatmaps']
        
        try:
            if selection == 'Combined Average':
                # Try enhanced version methods first
                if hasattr(self.app.heatmap_generator, 'create_interactive_overlay'):
                    # Enhanced version - use fusion heatmap or first available
                    if 'gradcam++' in heatmaps:
                        heatmap_to_use = heatmaps['gradcam++']
                    elif 'gradcam' in heatmaps:
                        heatmap_to_use = heatmaps['gradcam']
                    else:
                        heatmap_to_use = list(heatmaps.values())[0] if heatmaps else np.zeros((224, 224))
                    
                    overlay_result = self.app.heatmap_generator.create_interactive_overlay(
                        original_img, heatmap_to_use, colormap='jet'
                    )
                    overlay = overlay_result['overlay']
                elif hasattr(self.app.heatmap_generator, 'create_multi_circle_overlay'):
                    # Basic version
                    overlay = self.app.heatmap_generator.create_multi_circle_overlay(
                        original_img, heatmaps, self.current_predictions
                    )
                else:
                    # Fallback - create simple overlay
                    overlay = original_img.copy()
                title = 'Combined Disease Highlights'
            else:
                # Individual disease heatmap
                if selection in heatmaps:
                    if hasattr(self.app.heatmap_generator, 'create_interactive_overlay'):
                        # Enhanced version
                        overlay_result = self.app.heatmap_generator.create_interactive_overlay(
                            original_img, heatmaps[selection], colormap='jet'
                        )
                        overlay = overlay_result['overlay']
                    elif hasattr(self.app.heatmap_generator, 'get_circle_overlay'):
                        # Basic version
                        overlay = self.app.heatmap_generator.get_circle_overlay(
                            original_img, selection, heatmaps
                        )
                    else:
                        # Fallback
                        overlay = original_img.copy()
                else:
                    overlay = original_img.copy()
                title = f'{selection} Highlight'
            
            # Display the overlay
            img = Image.fromarray(overlay)
            img = img.resize((400, 400), Image.LANCZOS)
            self.heatmap_photo = ImageTk.PhotoImage(img)
            self.heatmap_label.configure(image=self.heatmap_photo)
            self.heatmap_label.bind("<Button-1>", lambda e: self.open_zoom_window(overlay, title))
            
        except Exception as e:
            print(f"Error displaying heatmap: {e}")
            # Show error message in heatmap area
            self.heatmap_label.configure(image=None, text=f"Error displaying heatmap: {e}")

    def open_zoom_window(self, img_array, title):
        zoom_window = tk.Toplevel(self.root)
        zoom_window.title(title)
        zoom_window.geometry("800x600")
        
        # Create canvas with scrollbars
        canvas = tk.Canvas(zoom_window)
        hbar = ttk.Scrollbar(zoom_window, orient=tk.HORIZONTAL, command=canvas.xview)
        vbar = ttk.Scrollbar(zoom_window, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        
        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        # Convert array to PIL Image
        pil_img = Image.fromarray(img_array)
        
        # Initial display
        self.zoom_image = pil_img
        self.zoom_photo = ImageTk.PhotoImage(pil_img)
        canvas.create_image(0, 0, image=self.zoom_photo, anchor="nw")
        canvas.configure(scrollregion=canvas.bbox(tk.ALL))
        
        # Zoom functionality
        self.zoom_level = 1.0
        def zoom(event):
            factor = 1.1 if event.delta > 0 else 0.9
            self.zoom_level *= factor
            new_size = (int(pil_img.width * self.zoom_level), int(pil_img.height * self.zoom_level))
            resized = pil_img.resize(new_size, Image.LANCZOS)
            self.zoom_photo = ImageTk.PhotoImage(resized)
            canvas.create_image(0, 0, image=self.zoom_photo, anchor="nw")
            canvas.configure(scrollregion=canvas.bbox(tk.ALL))
        
        canvas.bind("<MouseWheel>", zoom)

        # Panning functionality
        def on_press(event):
            canvas.scan_mark(event.x, event.y)
        
        def on_move(event):
            canvas.scan_dragto(event.x, event.y, gain=1)
        
        canvas.bind("<Button-3>", on_press)  # Right click
        canvas.bind("<B3-Motion>", on_move)
        
        # Close on minimize (but in Tkinter, we can bind to window close)
        zoom_window.protocol("WM_DELETE_WINDOW", zoom_window.destroy)
    
    def display_results(self, result_dict):
        """Display results from enhanced version (dictionary format)"""
        # Extract data from result dictionary
        predictions = result_dict.get('predictions', {})
        summary = result_dict.get('summary', 'No summary available')
        report = result_dict.get('detailed_report', 'No report available')
        
        # Store for later use
        self.current_report = report
        self.current_predictions = predictions
        
        # Display the results
        self.display_summary(summary)
        self.display_report(report)
        self.display_probabilities(predictions)
        
        # Handle heatmap data - adapt enhanced format to basic format
        overlay_data = result_dict.get('overlay_data', {})
        heatmaps = result_dict.get('heatmaps', {})
        original_img = result_dict.get('original_img')
        
        if original_img is not None and heatmaps:
            # Create compatible heatmap data structure
            sorted_diseases = sorted(predictions.keys(), key=lambda x: predictions[x], reverse=True)[:5]
            
            heatmap_data = {
                'heatmaps': heatmaps,
                'original_img': original_img,
                'sorted_diseases': sorted_diseases
            }
            
            self.display_heatmap(heatmap_data)
