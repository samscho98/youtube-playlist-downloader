"""
Playlist Manager Component with Update All Button in Bottom Left
Manages the playlist management interface in the GUI application
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Make sure parent directory is in path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from downloader.youtube import YouTubeDownloader

class PlaylistPanel(ttk.Frame):
    """Panel for managing YouTube playlists"""
    
    def __init__(self, parent, tracker):
        """
        Initialize the playlist panel
        
        Args:
            parent: Parent widget
            tracker: DownloadTracker instance
        """
        super().__init__(parent)
        self.tracker = tracker
        self.downloader = YouTubeDownloader()
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the playlist management widgets"""
        # Create frame for playlist controls
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add playlist entry
        ttk.Label(control_frame, text="Playlist URL:").pack(side=tk.LEFT, padx=5)
        self.playlist_url_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.playlist_url_var, width=40).pack(side=tk.LEFT, padx=5)
        
        # Add playlist name entry
        ttk.Label(control_frame, text="Name:").pack(side=tk.LEFT, padx=5)
        self.playlist_name_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.playlist_name_var, width=20).pack(side=tk.LEFT, padx=5)
        
        # Add interval entry
        ttk.Label(control_frame, text="Check interval (hours):").pack(side=tk.LEFT, padx=5)
        self.interval_var = tk.StringVar(value="24")
        ttk.Entry(control_frame, textvariable=self.interval_var, width=5).pack(side=tk.LEFT, padx=5)
        
        # Add playlist button
        ttk.Button(control_frame, text="Add Playlist", command=self._add_playlist).pack(side=tk.LEFT, padx=5)
        
        # Create frame for playlist list
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add playlist treeview
        self.playlist_tree = ttk.Treeview(
            list_frame, 
            columns=("name", "url", "interval", "last_checked"),
            show="headings"
        )
        
        # Configure columns
        self.playlist_tree.heading("name", text="Name")
        self.playlist_tree.heading("url", text="URL")
        self.playlist_tree.heading("interval", text="Check Interval (hours)")
        self.playlist_tree.heading("last_checked", text="Last Checked")
        
        self.playlist_tree.column("name", width=150)
        self.playlist_tree.column("url", width=300)
        self.playlist_tree.column("interval", width=120)
        self.playlist_tree.column("last_checked", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.playlist_tree.yview)
        self.playlist_tree.configure(yscroll=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.playlist_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add double-click binding for editing
        self.playlist_tree.bind("<Double-1>", self._on_double_click)
        
        # Add button frame below the treeview
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add buttons
        ttk.Button(button_frame, text="Remove Selected", command=self._remove_playlist).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Download Selected Now", command=self._download_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Check for Valid URL", command=self._validate_url).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh List", command=self.refresh_playlists).pack(side=tk.RIGHT, padx=5)
        
        # Status frame with Update All button in bottom left
        status_frame = ttk.Frame(self)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add Update All button to bottom left corner
        update_all_button = ttk.Button(
            status_frame, 
            text="Update All Playlists", 
            command=self._update_all_playlists,
            style="Accent.TButton"  # Special style for emphasis
        )
        update_all_button.pack(side=tk.LEFT, padx=5)
        
        # Create a style for the Update All button to make it stand out
        self.style = ttk.Style()
        if "Accent.TButton" not in self.style.theme_names():
            # Only create the style if it doesn't exist
            self.style.configure("Accent.TButton", font=("", 10, "bold"))
        
        # Status panel on the right side of the status frame
        status_panel = ttk.LabelFrame(status_frame, text="Playlist Status")
        status_panel.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_panel, textvariable=self.status_var)
        status_label.pack(fill=tk.X, padx=5, pady=5)
        
        # Load playlists
        self.refresh_playlists()
    
    def _on_double_click(self, event):
        """Handle double-click event on playlist treeview"""
        # Get the item that was clicked
        item = self.playlist_tree.identify('item', event.x, event.y)
        if item:
            # Call the edit function
            self._edit_playlist()
    
    def _add_playlist(self):
        """Add a playlist to the tracker"""
        url = self.playlist_url_var.get().strip()
        name = self.playlist_name_var.get().strip()
        interval_str = self.interval_var.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a playlist URL")
            return
            
        if not name:
            name = f"Playlist {len(self.tracker.get_playlists()) + 1}"
            
        try:
            interval = int(interval_str) if interval_str else 24
        except ValueError:
            messagebox.showerror("Error", "Check interval must be a number")
            return
            
        # Validate YouTube URL
        if "youtube.com" not in url and "youtu.be" not in url:
            messagebox.showerror("Error", "Invalid YouTube URL")
            return
            
        # Add to tracker
        success = self.tracker.add_playlist(url=url, name=name, check_interval=interval)
        
        if success:
            messagebox.showinfo("Success", f"Added playlist: {name}")
            self.playlist_url_var.set("")
            self.playlist_name_var.set("")
            self.interval_var.set("24")
            self.refresh_playlists()
        else:
            messagebox.showerror("Error", "Failed to add playlist")
            
    def _remove_playlist(self):
        """Remove selected playlist from the tracker"""
        selected = self.playlist_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a playlist to remove")
            return
            
        item = self.playlist_tree.item(selected[0])
        url = item["values"][1]
        name = item["values"][0]
        
        if messagebox.askyesno("Confirm", f"Remove playlist '{name}'?"):
            success = self.tracker.remove_playlist(url)
            
            if success:
                messagebox.showinfo("Success", f"Removed playlist: {name}")
                self.refresh_playlists()
            else:
                messagebox.showerror("Error", "Failed to remove playlist")
                
    def _update_all_playlists(self):
        """Update all tracked playlists"""
        playlists = self.tracker.get_playlists()
        
        if not playlists:
            messagebox.showinfo("Info", "No playlists are being tracked")
            return
            
        # Ask for confirmation
        if not messagebox.askyesno("Confirm", f"Update all {len(playlists)} tracked playlists?\n\nThis will launch the console application."):
            return
            
        # Now we need to find and launch the main application script
        main_script = os.path.join(parent_dir, "main.py")
        
        if not os.path.exists(main_script):
            messagebox.showerror("Error", f"Could not find main script: {main_script}")
            return
            
        try:
            # Construct command to update all playlists
            cmd = [sys.executable, main_script, "--update-all"]
            
            # Execute in a new console window on Windows
            if sys.platform == "win32":
                import subprocess
                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                # For other platforms, just run the command
                import subprocess
                subprocess.Popen(cmd)
                
            self.status_var.set(f"Launched update for all playlists")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch updater: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
    
    def _edit_playlist(self):
        """Edit the selected playlist"""
        selected = self.playlist_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a playlist to edit")
            return
            
        item = self.playlist_tree.item(selected[0])
        current_url = item["values"][1]
        current_name = item["values"][0]
        current_interval = item["values"][2]
        
        # Create edit dialog
        edit_dialog = tk.Toplevel(self)
        edit_dialog.title(f"Edit Playlist: {current_name}")
        edit_dialog.geometry("500x200")
        edit_dialog.resizable(False, False)
        edit_dialog.transient(self)  # Make the dialog modal
        edit_dialog.grab_set()
        
        # Create edit form
        form_frame = ttk.Frame(edit_dialog, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # URL (read-only since it's the ID)
        ttk.Label(form_frame, text="URL (cannot be changed):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        url_entry = ttk.Entry(form_frame, width=50)
        url_entry.insert(0, current_url)
        url_entry.config(state='readonly')
        url_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Name
        ttk.Label(form_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar(value=current_name)
        name_entry = ttk.Entry(form_frame, textvariable=name_var, width=30)
        name_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Check interval
        ttk.Label(form_frame, text="Check interval (hours):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        interval_var = tk.StringVar(value=current_interval)
        interval_entry = ttk.Entry(form_frame, textvariable=interval_var, width=10)
        interval_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
        # Save and Cancel buttons
        ttk.Button(
            button_frame, 
            text="Save Changes",
            command=lambda: self._save_playlist_edits(
                edit_dialog, current_url, name_var.get(), interval_var.get()
            )
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Cancel",
            command=edit_dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        
        # Center the dialog on parent window
        edit_dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - edit_dialog.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - edit_dialog.winfo_height()) // 2
        edit_dialog.geometry(f"+{x}+{y}")
    
    def _save_playlist_edits(self, dialog, url, name, interval_str):
        """Save the edited playlist information"""
        if not name.strip():
            messagebox.showerror("Error", "Name cannot be empty", parent=dialog)
            return
            
        try:
            interval = int(interval_str) if interval_str else 24
            if interval <= 0:
                raise ValueError("Interval must be positive")
        except ValueError:
            messagebox.showerror("Error", "Check interval must be a positive number", parent=dialog)
            return
        
        # Find the playlist in the tracker's playlists
        playlists = self.tracker.get_playlists()
        found = False
        
        for playlist in playlists:
            if playlist["url"] == url:
                # Update the playlist
                playlist["name"] = name.strip()
                playlist["check_interval"] = interval
                found = True
                break
                
        if found:
            # Save the updated playlists
            if self.tracker._save_playlists():
                messagebox.showinfo("Success", f"Updated playlist: {name}", parent=dialog)
                dialog.destroy()
                self.refresh_playlists()
            else:
                messagebox.showerror("Error", "Failed to save changes", parent=dialog)
        else:
            messagebox.showerror("Error", "Playlist not found", parent=dialog)
    
    def _validate_url(self):
        """Validate the playlist URL by fetching video information"""
        url = self.playlist_url_var.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a playlist URL")
            return
            
        if "youtube.com" not in url and "youtu.be" not in url:
            messagebox.showerror("Error", "Invalid YouTube URL")
            return
        
        self.status_var.set("Validating playlist URL...")
        self.update_idletasks()
        
        try:
            # Check if it's a playlist
            is_playlist = "list=" in url
            
            if is_playlist:
                # Get videos in the playlist
                videos = self.downloader.get_playlist_videos(url)
                
                if videos:
                    self.status_var.set(f"Valid playlist with {len(videos)} videos")
                    
                    # Suggest a name based on the first video
                    if not self.playlist_name_var.get() and videos[0].get('uploader'):
                        self.playlist_name_var.set(videos[0].get('uploader'))
                        
                    messagebox.showinfo("Playlist Valid", f"Found {len(videos)} videos in playlist")
                else:
                    self.status_var.set("No videos found in playlist or invalid playlist URL")
                    messagebox.showerror("Error", "No videos found in playlist or invalid playlist URL")
            else:
                # Try getting single video info
                self.status_var.set("URL appears to be a single video, not a playlist")
                messagebox.showinfo("Not a Playlist", "URL appears to be a single video, not a playlist")
                
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Error validating URL: {str(e)}")
            
    def _download_selected(self):
        """Download selected playlist"""
        selected = self.playlist_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a playlist to download")
            return
            
        item = self.playlist_tree.item(selected[0])
        url = item["values"][1]
        name = item["values"][0]
        
        if messagebox.askyesno("Confirm", f"Download playlist '{name}'?\n\nThis will launch the console application."):
            # Now we need to find and launch the main application script
            main_script = os.path.join(parent_dir, "main.py")
            
            if not os.path.exists(main_script):
                messagebox.showerror("Error", f"Could not find main script: {main_script}")
                return
                
            try:
                # Construct command to download the playlist
                cmd = [sys.executable, main_script, "--download", url]
                
                # Execute in a new console window on Windows
                if sys.platform == "win32":
                    import subprocess
                    subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
                else:
                    # For other platforms, just run the command
                    import subprocess
                    subprocess.Popen(cmd)
                    
                self.status_var.set(f"Launched download for: {name}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to launch downloader: {str(e)}")
                self.status_var.set(f"Error: {str(e)}")
    
    def refresh_playlists(self):
        """Refresh the playlist treeview"""
        try:
            # Clear treeview
            for item in self.playlist_tree.get_children():
                self.playlist_tree.delete(item)
                
            # Add playlists
            playlists = self.tracker.get_playlists()
            for playlist in playlists:
                try:
                    name = playlist.get("name", "Unnamed Playlist")
                    url = playlist.get("url", "N/A")
                    interval = playlist.get("check_interval", 24)
                    last_checked = playlist.get("last_checked", "Never")
                    
                    if last_checked != "Never" and last_checked is not None:
                        try:
                            # Handle both string ISO format and datetime objects
                            if isinstance(last_checked, str):
                                last_checked = datetime.fromisoformat(last_checked).strftime("%Y-%m-%d %H:%M:%S")
                            elif hasattr(last_checked, 'strftime'):  # It's already a datetime object
                                last_checked = last_checked.strftime("%Y-%m-%d %H:%M:%S")
                            # If it's neither a string nor a datetime, leave as is
                        except (ValueError, TypeError) as e:
                            print(f"Error formatting date: {e}")
                            # If there's any error parsing the datetime, just display it as is
                            last_checked = str(last_checked)
                    
                    self.playlist_tree.insert("", tk.END, values=(name, url, interval, last_checked))
                except Exception as e:
                    print(f"Error adding playlist to treeview: {e}")
                    import traceback
                    traceback.print_exc()
                    # Try to add it with safe defaults
                    try:
                        self.playlist_tree.insert("", tk.END, values=(
                            playlist.get("name", "Error - Unnamed"),
                            playlist.get("url", "Error - No URL"),
                            str(playlist.get("check_interval", "?")),
                            "Error"
                        ))
                    except:
                        pass  # If it still fails, skip this entry
            
            self.status_var.set(f"Found {len(playlists)} tracked playlists")
        except Exception as e:
            print(f"Error refreshing playlists: {e}")
            import traceback
            traceback.print_exc()
            self.status_var.set(f"Error refreshing playlists: {str(e)}")
            messagebox.showerror("Error", f"Error refreshing playlists: {str(e)}")