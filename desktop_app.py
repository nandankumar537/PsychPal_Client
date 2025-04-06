import sys
import os
import subprocess
import threading
import json
import time
import requests
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import webbrowser

# Server process
server_process = None
server_thread = None
server_ready = False
API_URL = "http://localhost:5000"

class PsychPalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PsychPal - Mental Health Chatbot")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Color Palette - Therapeutic colors for mental well-being
        self.colors = {
            'primary': '#5B9AA0',        # Soothing teal
            'secondary': '#B8E0D2',      # Soft mint
            'background': '#F6F6F6',     # Light gray background
            'sidebar_bg': '#ADD8E6',     # Light blue sidebar
            'accent': '#D8A7B1',         # Soft pink
            'text_dark': '#2D4356',      # Deep blue-gray
            'text_medium': '#5C7B93',    # Medium blue-gray
            'text_light': '#90AFC5',     # Light blue-gray
            'button_hover': '#6DAEBC',   # Darker teal
            'user_msg': '#E3F2FD',       # Light blue bubble
            'bot_msg': '#F0F9E8',        # Light green bubble
            'divider': '#E0E0E0',        # Light gray
            'online': '#88D498',         # Soft green
            'offline': '#F88379'         # Soft red
        }
        
        # Set window background
        self.root.configure(bg=self.colors['background'])
        
        # Configure Styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Frame Styles
        self.style.configure('TFrame', background=self.colors['background'])
        self.style.configure('Sidebar.TFrame', background=self.colors['sidebar_bg'])
        self.style.configure('Content.TFrame', background=self.colors['background'])
        
        # Button Styles
        self.style.configure('Primary.TButton',
                            background=self.colors['primary'],
                            foreground=self.colors['text_dark'],
                            font=('Inter', 10, 'bold'),
                            padding=10,
                            relief='flat')
        self.style.map('Primary.TButton',
                    background=[('active', self.colors['button_hover']),
                               ('pressed', self.colors['button_hover']),
                               ('disabled', '#546E7A')])
        
        # Sidebar Button
        self.style.configure('SidebarButton.TButton',
                          background=self.colors['sidebar_bg'],
                          foreground=self.colors['text_dark'],
                          font=('Inter', 11),
                          padding=12,
                          width=15,
                          relief='flat')
        self.style.map('SidebarButton.TButton',
                    background=[('active', self.colors['secondary']),
                               ('pressed', self.colors['secondary'])])
        
        # Entry Styles
        self.style.configure('TEntry',
                            fieldbackground=self.colors['secondary'],
                            foreground=self.colors['text_dark'],
                            padding=10,
                            font=('Inter', 11))
        
        # Scrollbar Styles
        self.style.configure('Vertical.TScrollbar',
                            background=self.colors['background'],
                            arrowcolor=self.colors['text_medium'],
                            bordercolor=self.colors['background'])
        
        # Label Styles
        self.style.configure('TLabel', 
                          background=self.colors['background'],
                          foreground=self.colors['text_dark'],
                          font=('Inter', 11))
        
        self.style.configure('Title.TLabel',
                          background=self.colors['background'],
                          foreground=self.colors['primary'],
                          font=('Inter', 18, 'bold'))
        
        self.style.configure('Sidebar.TLabel',
                          background=self.colors['sidebar_bg'],
                          foreground=self.colors['text_dark'])
        
        # LabelFrame Style
        self.style.configure('TLabelframe', 
                          background=self.colors['background'],
                          foreground=self.colors['text_dark'],
                          padding=15,
                          borderwidth=0)
        self.style.configure('TLabelframe.Label', 
                          background=self.colors['sidebar_bg'],
                          foreground=self.colors['text_dark'],
                          font=('Inter', 12, 'bold'))
        
        # Checkbutton Style
        self.style.configure('TCheckbutton',
                          background=self.colors['background'],
                          foreground=self.colors['text_dark'],
                          font=('Inter', 11))
        
        # Progressbar Style
        self.style.configure('Horizontal.TProgressbar',
                          background=self.colors['primary'],
                          troughcolor=self.colors['secondary'])
        
        # Model status
        self.model_loaded = False
        self.current_conversation_id = None
        
        # Initialize missing attributes
        self.server_status_var = tk.StringVar(value="Server: Starting...")
        self.model_status_var = tk.StringVar(value="Model: Not Loaded")
        self.model_var = tk.StringVar()  # For model selection in the combobox
        
        # Main layout
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Sidebar
        self.sidebar = ttk.Frame(self.main_frame, width=250, style='Sidebar.TFrame')
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        
        # Make sidebar a fixed width
        self.sidebar.pack_propagate(False)
        
        # App logo and title
        logo_frame = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
        logo_frame.pack(fill=tk.X, pady=(30, 20))
        
        ttk.Label(logo_frame, text="PsychPal", 
                 font=("Inter", 22, "bold"), foreground=self.colors['primary'], 
                 background=self.colors['sidebar_bg']).pack()
        
        ttk.Label(logo_frame, text="Mental Health Assistant", 
                 font=("Inter", 11), foreground=self.colors['text_medium'], 
                 background=self.colors['sidebar_bg']).pack(pady=(0, 10))
        
        # Add a divider
        ttk.Separator(self.sidebar, orient='horizontal').pack(fill=tk.X, padx=20, pady=10)
        
        # Sidebar buttons with icons (represented as text)
        button_frame = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.chat_btn = ttk.Button(button_frame, text="💬  Chat", command=self.show_chat, 
                                   style='SidebarButton.TButton')
        self.chat_btn.pack(fill=tk.X, pady=5)
        
        self.models_btn = ttk.Button(button_frame, text="🧠  Models", command=self.show_models,
                                    style='SidebarButton.TButton')
        self.models_btn.pack(fill=tk.X, pady=5)
        
        self.settings_btn = ttk.Button(button_frame, text="⚙️  Settings", command=self.show_settings,
                                      style='SidebarButton.TButton')
        self.settings_btn.pack(fill=tk.X, pady=5)
        
        # Status indicators
        status_frame = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20, padx=20)
        
        self.server_status_var = tk.StringVar(value="Server: Starting...")
        self.model_status_var = tk.StringVar(value="Model: Not Loaded")
        
        # Add status indicator circles
        server_frame = ttk.Frame(status_frame, style='Sidebar.TFrame')
        server_frame.pack(fill=tk.X, pady=2)
        
        self.server_indicator = tk.Canvas(server_frame, width=12, height=12, bg=self.colors['sidebar_bg'], 
                                         highlightthickness=0)
        self.server_indicator.pack(side=tk.LEFT, padx=(0, 8))
        self.server_indicator.create_oval(2, 2, 10, 10, fill=self.colors['offline'], outline="")
        
        ttk.Label(server_frame, textvariable=self.server_status_var, 
                foreground=self.colors['text_medium'], background=self.colors['sidebar_bg'],
                font=('Inter', 10)).pack(side=tk.LEFT)
        
        model_frame = ttk.Frame(status_frame, style='Sidebar.TFrame')
        model_frame.pack(fill=tk.X, pady=2)
        
        self.model_indicator = tk.Canvas(model_frame, width=12, height=12, bg=self.colors['sidebar_bg'], 
                                        highlightthickness=0)
        self.model_indicator.pack(side=tk.LEFT, padx=(0, 8))
        self.model_indicator.create_oval(2, 2, 10, 10, fill=self.colors['offline'], outline="")
        
        ttk.Label(model_frame, textvariable=self.model_status_var, 
                foreground=self.colors['text_medium'], background=self.colors['sidebar_bg'],
                font=('Inter', 10)).pack(side=tk.LEFT)
        
        # Content area
        self.content = ttk.Frame(self.main_frame, style='Content.TFrame')
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Initialize frames for different sections
        self.chat_frame = ttk.Frame(self.content, style='Content.TFrame')
        self.models_frame = ttk.Frame(self.content, style='Content.TFrame')
        self.settings_frame = ttk.Frame(self.content, style='Content.TFrame')
        
        # Initialize UI components
        self.setup_chat_ui()
        self.setup_models_ui()
        self.setup_settings_ui()
        
        # Show chat by default
        self.show_chat()
        
        # Start server check
        self.check_server_status()
    
    def setup_chat_ui(self):
        # Chat header
        header_frame = ttk.Frame(self.chat_frame, style='Content.TFrame')
        header_frame.pack(fill=tk.X, padx=30, pady=(25, 5))
        
        ttk.Label(header_frame, text="Chat with PsychPal", 
                 font=("Inter", 18, "bold"), foreground=self.colors['primary'],
                 background=self.colors['background']).pack(anchor='w')
        
        ttk.Label(header_frame, text="Your personal mental health assistant", 
                 font=("Inter", 12), foreground=self.colors['text_medium'],
                 background=self.colors['background']).pack(anchor='w', pady=(0, 10))
        
        # Chat container with border and rounded corners (simulated)
        chat_container = ttk.Frame(self.chat_frame, style='TFrame')
        chat_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=(5, 20))
        
        # Chat history with custom styling
        self.chat_history = scrolledtext.ScrolledText(
            chat_container, 
            wrap=tk.WORD, 
            font=("Inter", 11),
            bg=self.colors['background'],
            fg=self.colors['text_dark'],
            padx=25,
            pady=25,
            relief='flat',
            highlightthickness=0,
            borderwidth=0
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags with improved styling
        self.chat_history.tag_configure("user_msg_header", 
                                    foreground=self.colors['text_light'],
                                    font=("Inter", 10, "bold"))
        
        self.chat_history.tag_configure("bot_msg_header", 
                                    foreground=self.colors['text_light'],
                                    font=("Inter", 10, "bold"))
        
        self.chat_history.tag_configure("user_msg", 
                                    foreground=self.colors['text_dark'],
                                    background=self.colors['user_msg'],
                                    font=("Inter", 11),
                                    lmargin1=20,
                                    lmargin2=20,
                                    rmargin=20,
                                    spacing1=10,
                                    spacing3=10)
        
        self.chat_history.tag_configure("bot_msg", 
                                    foreground=self.colors['text_dark'],
                                    background=self.colors['bot_msg'],
                                    font=("Inter", 11),
                                    lmargin1=20,
                                    lmargin2=20,
                                    rmargin=20,
                                    spacing1=10,
                                    spacing3=10)
        
        # Input area with rounded appearance
        input_frame = ttk.Frame(self.chat_frame, style='TFrame')
        input_frame.pack(fill=tk.X, padx=30, pady=(0, 30))
        
        input_container = ttk.Frame(input_frame, style='TFrame')
        input_container.pack(fill=tk.X)
        
        self.message_input = ttk.Entry(
            input_container, 
            font=("Inter", 12),
            style='TEntry'
        )
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Bind Enter key to send message
        self.message_input.bind("<Return>", self.send_message)
        
        self.send_btn = ttk.Button(
            input_container, 
            text="Send", 
            style='Primary.TButton',
            command=self.send_message
        )
        self.send_btn.pack(side=tk.RIGHT)
        
        # Welcome message with more friendly formatting
        self.welcome_text = """Welcome to PsychPal! 😊

I'm here to listen and support your mental well-being. Feel free to share your thoughts, feelings, or concerns with me in a private, judgment-free space.

To get started:
• Go to the Models tab and download a model
• Return here to start chatting
• Remember, all conversations stay on your device

I'm designed to provide empathetic responses and gentle guidance, but I'm not a replacement for professional help. If you're experiencing a crisis, please contact a mental health professional or emergency services.

How are you feeling today?"""

        # Set initial welcome message
        self.chat_history.config(state='normal')
        self.chat_history.delete(1.0, tk.END)
        self.chat_history.insert(tk.END, "PsychPal: ", "bot_msg_header")
        self.chat_history.insert(tk.END, self.welcome_text + "\n\n", "bot_msg")
        self.chat_history.config(state='disabled')
    
    def setup_models_ui(self):
        # Title with more padding
        header_frame = ttk.Frame(self.models_frame, style='Content.TFrame')
        header_frame.pack(fill=tk.X, padx=30, pady=(25, 5))
        
        ttk.Label(header_frame, text="Model Management", 
                font=("Inter", 18, "bold"), foreground=self.colors['primary'],
                background=self.colors['background']).pack(anchor='w')
        
        ttk.Label(header_frame, text="Download and manage conversation models", 
                font=("Inter", 12), foreground=self.colors['text_medium'],
                background=self.colors['background']).pack(anchor='w', pady=(0, 10))
        
        # Model status frame with better spacing
        status_frame = ttk.LabelFrame(
            self.models_frame, 
            text="Current Model Status",
            style='TLabelframe',
            padding=20
        )
        status_frame.pack(fill=tk.X, padx=30, pady=15)
        
        self.model_detail_var = tk.StringVar(value="No model loaded")
        ttk.Label(status_frame, 
                textvariable=self.model_detail_var,
                font=("Inter", 11),
                foreground=self.colors['text_medium']
                ).pack(anchor='w')
        
        # Available models frame
        models_frame = ttk.LabelFrame(
            self.models_frame,
            text="Download Model",
            style='TLabelframe',
            padding=20
        )
        models_frame.pack(fill=tk.X, padx=30, pady=15)
        
        # Model selection
        ttk.Label(models_frame, 
                text="Select a model to download:",
                font=("Inter", 11),
                foreground=self.colors['text_dark']
                ).pack(anchor='w', pady=(0, 10))
        
        self.models_combo = ttk.Combobox(
            models_frame, 
            textvariable=self.model_var, 
            state='readonly',
            font=("Inter", 11),
            height=15
        )
        self.models_combo.pack(fill=tk.X, pady=(0, 15))
        
        # Progress bar
        self.download_progress = ttk.Progressbar(
            models_frame, 
            orient=tk.HORIZONTAL, 
            length=100, 
            mode='determinate',
            style='Horizontal.TProgressbar'
        )
        self.download_progress.pack(fill=tk.X, pady=(0, 15))
        
        # Download button
        self.download_btn = ttk.Button(
            models_frame, 
            text="Download Model", 
            style='Primary.TButton',
            command=self.download_model
        )
        self.download_btn.pack(fill=tk.X)
        
        # Info box with improved styling
        info_frame = ttk.LabelFrame(self.models_frame, text="Model Information", style='TLabelframe', padding=20)
        info_frame.pack(fill=tk.X, padx=30, pady=15)
        
        info_text = """PsychPal uses local language models for complete privacy and offline capability.
        
• Smaller models are faster but may provide simpler responses
• Larger models offer more nuanced conversations but require more resources
• All processing happens on your device - your conversations never leave your computer

Models are designed to provide empathetic and supportive responses about mental health topics."""
        
        ttk.Label(info_frame, text=info_text, 
                wraplength=700, 
                justify=tk.LEFT,
                font=("Inter", 11),
                foreground=self.colors['text_medium']).pack()
    
    def setup_settings_ui(self):
        # Title with more padding
        header_frame = ttk.Frame(self.settings_frame, style='Content.TFrame')
        header_frame.pack(fill=tk.X, padx=30, pady=(25, 5))
        
        ttk.Label(header_frame, text="Settings", 
                font=("Inter", 18, "bold"), foreground=self.colors['primary'],
                background=self.colors['background']).pack(anchor='w')
        
        ttk.Label(header_frame, text="Configure your PsychPal experience", 
                font=("Inter", 12), foreground=self.colors['text_medium'],
                background=self.colors['background']).pack(anchor='w', pady=(0, 10))
        
        # Training settings with improved spacing
        training_frame = ttk.LabelFrame(
            self.settings_frame, 
            text="Local Model Training",
            style='TLabelframe',
            padding=20
        )
        training_frame.pack(fill=tk.X, padx=30, pady=15)
        
        # Use local data checkbox
        self.use_local_data = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            training_frame, 
            text="Use local conversation data for training", 
            variable=self.use_local_data,
            style='TCheckbutton'
        ).pack(anchor='w', pady=(0, 15))
        
        # Training parameters
        params_frame = ttk.Frame(training_frame)
        params_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Epochs
        ttk.Label(params_frame, 
                text="Epochs:",
                font=("Inter", 11),
                foreground=self.colors['text_medium']
                ).grid(row=0, column=0, padx=(0, 10), pady=5, sticky='w')
        self.epochs_var = tk.StringVar(value="1")
        ttk.Spinbox(params_frame, 
                    from_=1, to=10, 
                    textvariable=self.epochs_var,
                    font=("Inter", 11),
                    width=5).grid(row=0, column=1, padx=(0, 20), pady=5)
        
        # Batch size
        ttk.Label(params_frame, 
                text="Batch Size:",
                font=("Inter", 11),
                foreground=self.colors['text_medium']
                ).grid(row=0, column=2, padx=(0, 10), pady=5, sticky='w')
        self.batch_size_var = tk.StringVar(value="4")
        ttk.Spinbox(params_frame, 
                   from_=1, to=16, 
                   textvariable=self.batch_size_var,
                   font=("Inter", 11),
                   width=5).grid(row=0, column=3, padx=(0, 20), pady=5)
        
        # Learning rate
        ttk.Label(params_frame, 
                text="Learning Rate:",
                font=("Inter", 11),
                foreground=self.colors['text_medium']
                ).grid(row=0, column=4, padx=(0, 10), pady=5, sticky='w')
        self.learning_rate_var = tk.StringVar(value="0.0001")
        ttk.Entry(params_frame, 
                 textvariable=self.learning_rate_var,
                 font=("Inter", 11),
                 width=8).grid(row=0, column=5, padx=0, pady=5)
        
        # Training progress and button
        self.training_progress = ttk.Progressbar(
                training_frame, 
                orient=tk.HORIZONTAL, 
                length=100, 
                mode='determinate',
                style='Horizontal.TProgressbar'
            )
        self.training_progress.pack(fill=tk.X, pady=(0, 15))
        
        self.train_btn = ttk.Button(
            training_frame,
            text="Start Training",
            style='Primary.TButton',
            command=self.start_training
        )
        self.train_btn.pack(fill=tk.X)

        # Privacy settings
        privacy_frame = ttk.LabelFrame(
            self.settings_frame, 
            text="Privacy Settings",
            style='TLabelframe',
            padding=20
        )
        privacy_frame.pack(fill=tk.X, padx=30, pady=15)

        # Privacy parameters
        privacy_params_frame = ttk.Frame(privacy_frame)
        privacy_params_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Epsilon
        ttk.Label(privacy_params_frame, 
                text="Privacy Epsilon:",
                font=("Inter", 11),
                foreground=self.colors['text_medium']
                ).grid(row=0, column=0, padx=(0, 10), pady=5, sticky='w')
        self.epsilon_var = tk.StringVar(value="2.0")
        ttk.Entry(privacy_params_frame, 
                 textvariable=self.epsilon_var,
                 font=("Inter", 11),
                 width=8).grid(row=0, column=1, padx=(0, 20), pady=5)
        
        # Delta
        ttk.Label(privacy_params_frame, 
                text="Privacy Delta:",
                font=("Inter", 11),
                foreground=self.colors['text_medium']
                ).grid(row=0, column=2, padx=(0, 10), pady=5, sticky='w')
        self.delta_var = tk.StringVar(value="1e-5")
        ttk.Entry(privacy_params_frame, 
                 textvariable=self.delta_var,
                 font=("Inter", 11),
                 width=8).grid(row=0, column=3, padx=(0, 20), pady=5)
        
        # Sync frequency
        ttk.Label(privacy_params_frame, 
                text="Sync Frequency:",
                font=("Inter", 11),
                foreground=self.colors['text_medium']
                ).grid(row=0, column=4, padx=(0, 10), pady=5, sticky='w')
        self.sync_freq_var = tk.StringVar(value="manual")
        ttk.Combobox(privacy_params_frame, 
                    textvariable=self.sync_freq_var,
                    font=("Inter", 11),
                    width=10,
                    values=["manual", "daily", "weekly"], 
                    state='readonly').grid(row=0, column=5, padx=0, pady=5)
        
        # Sync progress and button
        self.sync_progress = ttk.Progressbar(
            privacy_frame, 
            orient=tk.HORIZONTAL, 
            length=100, 
            mode='determinate',
            style='Horizontal.TProgressbar'
        )
        self.sync_progress.pack(fill=tk.X, pady=(0, 15))
        
        self.sync_progress_label = ttk.Label(
            privacy_frame,
            text="Sync Progress: 0%",
            font=("Inter", 11),
            foreground=self.colors['text_medium']
        )
        self.sync_progress_label.pack(pady=(0, 15))
        
        self.sync_btn = ttk.Button(
            privacy_frame, 
            text="Sync with Server", 
            style='Primary.TButton',
            command=self.sync_with_server
        )
        self.sync_btn.pack(fill=tk.X)
        
        # Privacy note with improved styling
        ttk.Label(privacy_frame, 
                text="Privacy Note: When you sync with the server, only differential privacy protected model updates are shared, not your conversation data.",
                wraplength=700,
                font=("Inter", 10, "italic"),
                foreground=self.colors['text_medium']).pack(pady=(15, 0))
        
        # About section
        about_frame = ttk.LabelFrame(
            self.settings_frame, 
            text="About PsychPal",
            style='TLabelframe',
            padding=20
        )
        about_frame.pack(fill=tk.X, padx=30, pady=15)
        
        about_text = """PsychPal v1.0.0
        
A privacy-focused mental health chatbot that runs completely on your device.
Your conversations are stored only on your computer and are never shared with external servers.

PsychPal is designed to provide a supportive space for mental health conversations while respecting your privacy and data sovereignty.

Built with Python, Tkinter, Flask, and HuggingFace Transformer models."""
        
        ttk.Label(about_frame, 
                text=about_text,
                wraplength=700,
                font=("Inter", 11),
                foreground=self.colors['text_medium']).pack()
        
        # Github link
        link_frame = ttk.Frame(about_frame)
        link_frame.pack(pady=(15, 0))
        
        github_link = ttk.Label(link_frame, 
                             text="View Source on GitHub",
                             font=("Inter", 11, "underline"),
                             foreground=self.colors['primary'],
                             cursor="hand2")
        github_link.pack()
        github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/nandaankumar537/PsychPal_Client"))
    
    def show_frame(self, frame):
        # Hide all frames
        self.chat_frame.pack_forget()
        self.models_frame.pack_forget()
        self.settings_frame.pack_forget()
        
        # Show selected frame
        frame.pack(fill=tk.BOTH, expand=True)
    
    def show_chat(self):
        self.show_frame(self.chat_frame)
        # Reset chat if needed
        if not self.current_conversation_id:
            self.chat_history.config(state='normal')
            self.chat_history.delete(1.0, tk.END)
            self.chat_history.insert(tk.END, "PsychPal: ", "bot_msg_header")
            self.chat_history.insert(tk.END, self.welcome_text + "\n\n", "bot_msg")
            self.chat_history.config(state='disabled')
            self.current_conversation_id = str(int(time.time()))
        
        # Check model status
        if not self.model_loaded:
            self.send_btn.config(state='disabled')
            messagebox.showinfo("Model Required", "Please download a model from the Models tab before chatting.")
        else:
            self.send_btn.config(state='normal')
    
    def show_models(self):
        self.show_frame(self.models_frame)
        # Fetch available models
        try:
            self.fetch_available_models()
            self.update_model_status()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch models: {str(e)}")
    
    def show_settings(self):
        self.show_frame(self.settings_frame)
        # Disable training/sync if model not loaded
        if not self.model_loaded:
            self.train_btn.config(state='disabled')
            self.sync_btn.config(state='disabled')
            messagebox.showinfo("Model Required", "Please download a model from the Models tab first.")
        else:
            self.train_btn.config(state='normal')
            self.sync_btn.config(state='normal')
    
    def fetch_available_models(self):
        try:
            response = requests.get(f"{API_URL}/api/model/available")
            if response.status_code == 200:
                models = response.json()
                model_options = [f"{m['name']} ({m['size']} MB)" for m in models]
                self.models_combo['values'] = model_options
                if model_options:
                    self.models_combo.current(0)
        except Exception as e:
            print(f"Error fetching models: {str(e)}")
    
    def update_model_status(self):
        try:
            response = requests.get(f"{API_URL}/api/model/status")
            if response.status_code == 200:
                status = response.json()
                self.model_loaded = status.get('is_loaded', False)
                
                if self.model_loaded:
                    self.model_status_var.set("Model: Loaded")
                    self.model_indicator.delete("all")
                    self.model_indicator.create_oval(2, 2, 10, 10, fill=self.colors['online'], outline="")
                    
                    # Get detailed model info
                    info_response = requests.get(f"{API_URL}/api/model/info")
                    if info_response.status_code == 200:
                        info = info_response.json()
                        self.model_detail_var.set(
                            f"Model: {info.get('name', 'Unknown')}\n"
                            f"Size: {info.get('size', 'Unknown')} MB\n"
                            f"Last Updated: {time.strftime('%Y-%m-%d %H:%M', time.localtime(info.get('lastUpdated', 0)))}"
                        )
                else:
                    self.model_status_var.set("Model: Not Loaded")
                    self.model_indicator.delete("all")
                    self.model_indicator.create_oval(2, 2, 10, 10, fill=self.colors['offline'], outline="")
                    self.model_detail_var.set("No model loaded")
        except Exception as e:
            self.model_status_var.set("Model: Error")
            self.model_indicator.delete("all")
            self.model_indicator.create_oval(2, 2, 10, 10, fill=self.colors['offline'], outline="")
            print(f"Error updating model status: {str(e)}")
    
    def send_message(self, event=None):
        message = self.message_input.get().strip()
        if not message:
            return
        
        # Clear input
        self.message_input.delete(0, tk.END)
        
        # Add user message to chat with improved formatting
        self.chat_history.config(state='normal')
        self.chat_history.insert(tk.END, "\nYou: ", "user_msg_header")
        self.chat_history.insert(tk.END, f"{message}\n\n", "user_msg")
        self.chat_history.config(state='disabled')
        self.chat_history.see(tk.END)
        
        # Send to server
        try:
            response = requests.post(
                f"{API_URL}/api/chat",
                json={"message": message, "conversation_id": self.current_conversation_id}
            )
            
            if response.status_code == 200:
                bot_reply = response.json().get("response", "Sorry, I couldn't generate a response.")
                
                # Add bot response to chat with improved formatting
                self.chat_history.config(state='normal')
                self.chat_history.insert(tk.END, "PsychPal: ", "bot_msg_header")
                self.chat_history.insert(tk.END, f"{bot_reply}\n\n", "bot_msg")
                self.chat_history.config(state='disabled')
                self.chat_history.see(tk.END)
            else:
                messagebox.showerror("Error", "Failed to get response from the server.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to communicate with the server: {str(e)}")
    
    def download_model(self):
        if not self.models_combo.get():
            messagebox.showinfo("Select Model", "Please select a model to download")
            return
        
        # Get model ID from selection (first model = index 0)
        model_idx = self.models_combo.current()
        
        try:
            # Get available models to find the ID
            response = requests.get(f"{API_URL}/api/model/available")
            if response.status_code == 200:
                models = response.json()
                if 0 <= model_idx < len(models):
                    model_id = models[model_idx]['id']
                    
                    # Start download
                    download_response = requests.post(
                        f"{API_URL}/api/model/download",
                        json={"model_id": model_id}
                    )
                    
                    if download_response.status_code == 200:
                        download_data = download_response.json()
                        download_id = download_data.get("download_id")
                        
                        if download_id:
                            self.download_btn.config(state='disabled')
                            self.track_download_progress(download_id)
                        else:
                            messagebox.showerror("Error", "Failed to start download: No download ID returned")
                    else:
                        messagebox.showerror("Error", "Failed to start download")
                else:
                    messagebox.showerror("Error", "Invalid model selection")
            else:
                messagebox.showerror("Error", "Failed to get available models")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download model: {str(e)}")
    
    def track_download_progress(self, download_id):
        def update_progress():
            try:
                response = requests.get(f"{API_URL}/api/model/download/{download_id}/progress")
                if response.status_code == 200:
                    progress_data = response.json()
                    progress = progress_data.get("progress", 0)
                    status = progress_data.get("status", "")
                    
                    self.download_progress['value'] = progress
                    
                    if status == "completed":
                        messagebox.showinfo("Success", "Model downloaded and loaded successfully!")
                        self.download_btn.config(state='normal')
                        self.update_model_status()
                        self.model_loaded = True
                        self.send_btn.config(state='normal')
                        self.train_btn.config(state='normal')
                        self.sync_btn.config(state='normal')
                        return
                    elif status == "failed":
                        messagebox.showerror("Error", f"Download failed: {progress_data.get('error', 'Unknown error')}")
                        self.download_btn.config(state='normal')
                        return
                    
                    # Continue checking
                    self.root.after(500, update_progress)
                else:
                    messagebox.showerror("Error", "Failed to check download progress")
                    self.download_btn.config(state='normal')
            except Exception as e:
                messagebox.showerror("Error", f"Error tracking download: {str(e)}")
                self.download_btn.config(state='normal')
        
        # Start tracking
        update_progress()
    
    def start_training(self):
        # Validate inputs
        try:
            epochs = int(self.epochs_var.get())
            batch_size = int(self.batch_size_var.get())
            learning_rate = float(self.learning_rate_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for training parameters")
            return
        
        # Start training
        try:
            response = requests.post(
                f"{API_URL}/api/train",
                json={
                    "settings": {
                        "num_epochs": epochs,
                        "batch_size": batch_size,
                        "learning_rate": learning_rate,
                        "use_local_data": self.use_local_data.get()
                    }
                }
            )
            
            if response.status_code == 200:
                training_data = response.json()
                training_id = training_data.get("training_id")
                
                if training_id:
                    self.train_btn.config(state='disabled')
                    self.track_training_progress(training_id)
                else:
                    messagebox.showerror("Error", "Failed to start training: No training ID returned")
            else:
                messagebox.showerror("Error", "Failed to start training")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start training: {str(e)}")
    
    def track_training_progress(self, training_id):
        def update_progress():
            try:
                response = requests.get(f"{API_URL}/api/train/{training_id}/progress")
                if response.status_code == 200:
                    progress_data = response.json()
                    progress = progress_data.get("progress", 0)
                    status = progress_data.get("status", "")
                    
                    self.training_progress['value'] = progress
                    
                    if status == "completed":
                        messagebox.showinfo("Success", "Training completed successfully!")
                        self.train_btn.config(state='normal')
                        return
                    elif status == "failed":
                        messagebox.showerror("Error", f"Training failed: {progress_data.get('error', 'Unknown error')}")
                        self.train_btn.config(state='normal')
                        return
                    
                    # Continue checking
                    self.root.after(500, update_progress)
                else:
                    messagebox.showerror("Error", "Failed to check training progress")
                    self.train_btn.config(state='normal')
            except Exception as e:
                messagebox.showerror("Error", f"Error tracking training: {str(e)}")
                self.train_btn.config(state='normal')
        
        # Start tracking
        update_progress()
    
    def sync_with_server(self):
        # Validate inputs
        try:
            epsilon = float(self.epsilon_var.get())
            delta = float(self.delta_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for privacy parameters")
            return
        
        # Start sync
        try:
            response = requests.post(
                f"{API_URL}/api/sync",
                json={
                    "privacy_settings": {
                        "epsilon": epsilon,
                        "delta": delta
                    },
                    "sync_frequency": self.sync_freq_var.get()
                }
            )
            
            if response.status_code == 200:
                sync_data = response.json()
                sync_id = sync_data.get("sync_id")
                
                if sync_id:
                    self.sync_btn.config(state='disabled')
                    self.track_sync_progress(sync_id)
                else:
                    messagebox.showerror("Error", "Failed to start sync: No sync ID returned")
            else:
                messagebox.showerror("Error", "Failed to start sync")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start sync: {str(e)}")
    
    def track_sync_progress(self, sync_id):
        def update_progress():
            try:
                response = requests.get(f"{API_URL}/api/sync/{sync_id}/progress")
                if response.status_code == 200:
                    progress_data = response.json()
                    progress = progress_data.get("progress", 0)
                    status = progress_data.get("status", "")
                    
                    self.sync_progress['value'] = progress
                    self.sync_progress_label.config(text=f"Sync Progress: {progress}%")
                    
                    if status == "completed":
                        messagebox.showinfo("Success", "Sync completed successfully!")
                        self.sync_btn.config(state='normal')
                        return
                    elif status == "failed":
                        messagebox.showerror("Error", f"Sync failed: {progress_data.get('error', 'Unknown error')}")
                        self.sync_btn.config(state='normal')
                        return
                    
                    # Continue checking
                    self.root.after(500, update_progress)
                else:
                    messagebox.showerror("Error", "Failed to check sync progress")
                    self.sync_btn.config(state='normal')
            except Exception as e:
                messagebox.showerror("Error", f"Error tracking sync: {str(e)}")
                self.sync_btn.config(state='normal')
        
        # Start tracking
        update_progress()
    
    def check_server_status(self):
        def update_status():
            try:
                response = requests.get(f"{API_URL}")
                if response.status_code == 200:
                    self.server_status_var.set("Server: Online")
                    # Update indicator with glow effect
                    self.server_indicator.delete("all")
                    self.server_indicator.create_oval(2, 2, 12, 12, fill=self.colors['online'], outline="", tags="indicator")
                    self.server_indicator.create_oval(0, 0, 14, 14, fill="", outline=self.colors['online'], width=2, tags="glow")
                    
                    # Check model status too
                    self.update_model_status()
                else:
                    self.server_status_var.set("Server: Error")
                    self.server_indicator.delete("all")
                    self.server_indicator.create_oval(2, 2, 12, 12, fill=self.colors['offline'], outline="", tags="indicator")
                    self.server_indicator.create_oval(0, 0, 14, 14, fill="", outline=self.colors['offline'], width=2, tags="glow")
            except Exception:
                self.server_status_var.set("Server: Offline")
                self.server_indicator.delete("all")
                self.server_indicator.create_oval(2, 2, 12, 12, fill=self.colors['offline'], outline="", tags="indicator")
                self.server_indicator.create_oval(0, 0, 14, 14, fill="", outline=self.colors['offline'], width=2, tags="glow")
            
            # Check again in 5 seconds
            self.root.after(5000, update_status)
        
        # Start checking
        self.root.after(1000, update_status)
    
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to exit PsychPal?"):
            # Cleanup
            global server_process
            if server_process:
                try:
                    server_process.terminate()
                except:
                    pass
            self.root.destroy()

def start_server():
    global server_process, server_ready
    
    # Determine the path to the server script
    server_script = os.path.join(os.getcwd(), "server", "simplified_app.py")
    
    # Check if the script exists
    if not os.path.exists(server_script):
        messagebox.showerror("Error", f"Server script not found at {server_script}")
        return False
    
    try:
        # Start the server process
        server_process = subprocess.Popen(
            [sys.executable, server_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(server_script)
        )
        
        # Wait for the server to start
        for _ in range(50):  # 5 seconds timeout
            try:
                response = requests.get("http://localhost:5000/")
                if response.status_code == 200:
                    server_ready = True
                    print("Server started successfully")
                    return True
            except:
                time.sleep(0.1)
        
        # Server didn't start in time
        print("Server failed to start in time")
        return False
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        return False

def main():
    # Start server in a separate thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for server to initialize
    time.sleep(2)
    
    # Start GUI
    root = tk.Tk()
    app = PsychPalApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
