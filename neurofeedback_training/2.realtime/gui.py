from logging import WARNING
import tkinter as tk
from tkinter import messagebox
import sys
from tkinter import DISABLED, filedialog
import webbrowser
import time

class GUI():
    def __init__(self):
        print('Building GUI')
        self.root = tk.Tk()
        self.root.title('pyDecNef - A Python Decoding Neurofeedback Framework')
        self.root.geometry("1142x520")
        self.root.resizable(width=False, height=False)

        # CONNECTION 
        self.connection = tk.LabelFrame(self.root, text="Server - Client Connection", padx = 10, pady=10)
        self.connection.grid(row=1, column=0, columnspan = 7, padx = (20, 0), pady = (10, 0), sticky = "NSEW")

        self.server_ip = tk.Label(self.connection, text = "Server IP address:", width = 15, height = 1, borderwidth = 0, relief = tk.GROOVE)
        self.server_ip.grid(row = 0, column = 1)
        self.server_ip_entry = tk.Entry(self.connection, text = "", width = 15)
        self.server_ip_entry.grid(row=0, column=2)

        self.server_port = tk.Label(self.connection, text = "Server PORT:", width = 15, height = 1, borderwidth = 0, relief = tk.GROOVE)
        self.server_port.grid(row = 1, column = 1)
        self.server_port_entry = tk.Entry(self.connection, text = "", width = 15)
        self.server_port_entry.grid(row = 1, column = 2)

        # PARTICIPANT 
        self.participant = tk.LabelFrame(self.root, text="Participant", padx=10, pady=10)
        self.participant.grid(row=0, column=0, columnspan = 7, padx = (20, 0), pady = (10, 0), sticky = "NSEW")

        self.subject = tk.Label(self.participant, text = "Subject:", width = 15, height = 1, borderwidth = 0, relief = tk.GROOVE)
        self.subject.grid(row = 0, column = 1)
        self.subject_entry = tk.Entry(self.participant, text="", width = 15)
        self.subject_entry.grid(row=0, column=2)

        self.session = tk.Label(self.participant, text = "Session:", width = 15, height = 1, borderwidth = 0, relief = tk.GROOVE)
        self.session.grid(row = 1, column = 1)
        self.session_entry = tk.Entry(self.participant, text="", width = 15)
        self.session_entry.grid(row=1, column=2)

        self.run = tk.Label(self.participant, text = "Run:", width = 15, height = 1, borderwidth = 0, relief = tk.GROOVE)
        self.run.grid(row = 2, column = 1)
        self.run_entry = tk.Entry(self.participant, text="", width = 15)
        self.run_entry.grid(row = 2, column=2)
      
        # fMRI PARAMETERS 
        self.fmri_parameters = tk.LabelFrame(self.root, text="fMRI parameters", padx=10, pady=10)
        self.fmri_parameters.grid(row=0, column = 8, padx = (20, 0), pady = (10, 0), columnspan = 7, sticky = "NSEW")

        self.n_heatup_vols = tk.Label(self.fmri_parameters, text = "Num. heatup vols:", width = 15, height = 1, borderwidth = 0, relief = tk.GROOVE)
        self.n_heatup_vols.grid(row = 0, column = 1)
        self.n_heatup_vols_entry = tk.Entry(self.fmri_parameters, text = "", width = 15)
        self.n_heatup_vols_entry.grid(row=0, column=2)

        self.n_baseline_vols = tk.Label(self.fmri_parameters, text = "Num. baseline vols:", width = 15, height = 1, borderwidth = 0, relief = tk.GROOVE)
        self.n_baseline_vols.grid(row = 0, column = 3)
        self.n_baseline_vols_entry = tk.Entry(self.fmri_parameters, text = "", width = 15)
        self.n_baseline_vols_entry.grid(row=0, column=4)

        self.low_HRF_peak = tk.Label(self.fmri_parameters, text = "Low HRF peak threshold:", width = 25, height = 1, borderwidth = 0, relief = tk.GROOVE)
        self.low_HRF_peak.grid(row = 2, column = 1)
        self.low_HRF_peak_entry = tk.Entry(self.fmri_parameters, text = "", width = 15)
        self.low_HRF_peak_entry.grid(row=2, column=2)

        self.high_HRF_peak = tk.Label(self.fmri_parameters, text = "High HRF peak threshold:", width = 25, height = 1, borderwidth = 0, relief = tk.GROOVE)
        self.high_HRF_peak.grid(row = 2, column = 3)
        self.high_HRF_peak_entry = tk.Entry(self.fmri_parameters, text = "", width = 15)
        self.high_HRF_peak_entry.grid(row=2, column=4)

        self.TR = tk.Label(self.fmri_parameters, text = "TR:", width = 25, height = 1, borderwidth = 0, relief = tk.GROOVE)
        self.TR.grid(row = 3, column = 1)
        self.TR_entry = tk.Entry(self.fmri_parameters, text = "", width = 15)
        self.TR_entry.grid(row=3, column=2)

        self.first_vol_idx = tk.Label(self.fmri_parameters, text = "First vol index:", width = 25, height = 1, borderwidth = 0, relief = tk.GROOVE)
        self.first_vol_idx.grid(row = 3, column = 3)
        self.first_vol_idx_entry = tk.Entry(self.fmri_parameters, text = "", width = 15)
        self.first_vol_idx_entry.grid(row=3, column = 4)

        # FOLDERS
        self.folders = tk.LabelFrame(self.root, text="Folders", padx=10, pady=10)
        self.folders.grid(row=1, column = 8, padx = (20, 0), pady = (10, 0), columnspan = 7, sticky = "NSEW")

        self.fmri_folder = tk.Label(self.folders, text = "fMRI raw vols folder:", width = 20, height = 1, borderwidth = 0, relief = tk.GROOVE)
        self.fmri_folder.grid(row = 3, column = 1)
        self.selected_fmri_folder = tk.Entry(self.folders, text = "", width = 50)
        self.selected_fmri_folder.grid(row = 3, column = 3)
        self.select_fmri_folder = tk.Button(self.folders, text = "Browse", command = self.select_fmri_folder_cmd, height = 1)
        self.select_fmri_folder.grid(row=3, column = 4)

        self.outputs_folder = tk.Label(self.folders, text = "Outputs folder:", width = 20, height = 1, borderwidth = 0, relief = tk.GROOVE)
        self.outputs_folder.grid(row = 4, column = 1)
        self.selected_outputs_folder = tk.Entry(self.folders, text = "", width = 50)
        self.selected_outputs_folder.grid(row = 4, column = 3)
        self.select_outputs_folder = tk.Button(self.folders, text = "Browse", command = self.select_outputs_folder_cmd, height = 1)
        self.select_outputs_folder.grid(row=4, column = 4)

        # REQUIRED RESOURCES
        self.required_resources = tk.LabelFrame(self.root, text="Required resources", padx=10, pady=10)
        self.required_resources.grid(row=2, column = 0, padx = (20, 0), pady = (10, 0), columnspan = 16, sticky = "NSEW")

        self.mask = tk.Label(self.required_resources, text = "R.O.I. mask:", width = 20, height = 1, borderwidth = 0, relief = tk.GROOVE)
        self.mask.grid(row = 0, column = 0)
        self.mask_file = tk.Entry(self.required_resources, text = "", width = 85)
        self.mask_file.grid(row = 0, column = 1)
        self.select_mask_file = tk.Button(self.required_resources, text = "Browse", command = self.select_fmri_folder_cmd, height = 1)
        self.select_mask_file.grid(row=0, column = 2)

        self.model = tk.Label(self.required_resources, text = "Model:", width = 20, height = 1, borderwidth = 0, relief = tk.GROOVE)
        self.model.grid(row = 1, column = 0)
        self.model_file = tk.Entry(self.required_resources, text = "", width = 85)
        self.model_file.grid(row = 1, column = 1)
        self.select_model_file = tk.Button(self.required_resources, text = "Browse", command = self.select_fmri_folder_cmd, height = 1)
        self.select_model_file.grid(row=1, column = 2)

        self.reference_volume = tk.Label(self.required_resources, text = "Reference volume:", width = 20, height = 1, borderwidth = 0, relief = tk.GROOVE)
        self.reference_volume.grid(row = 2, column = 0)
        self.reference_volume_file = tk.Entry(self.required_resources, text = "", width = 85)
        self.reference_volume_file.grid(row = 2, column = 1)
        self.select_reference_volume_file = tk.Button(self.required_resources, text = "Browse", command = self.select_fmri_folder_cmd, height = 1)
        self.select_reference_volume_file.grid(row=2, column = 2)

        # STATUS
        self.status = tk.LabelFrame(self.root, text="Status", padx=10, pady=10)
        self.status.grid(row=3, column = 0, padx = (20, 0), pady = (10, 0), columnspan = 16, sticky = "NSEW")
        self.status_label = tk.Label(self.status, text = 'Server disconnected', fg='red')
        self.status_label.grid(row = 0, column = 0, columnspan= 16)

        # BUTTONS 
        self.buttons = tk.Frame(self.root, padx=10, pady=10)
        self.buttons.grid(row = 4, column = 0, padx = (10, 0), pady = (10, 0), columnspan = 13, sticky = "NSEW")        
        self.start_server = tk.Button(self.buttons, text = "Start server", height = 1, width = 10, command = self.do_something)
        self.start_server.grid(row = 0, column = 0)
        self.break_connection = tk.Button(self.buttons, text = "Break connection", height = 1, width = 10, state = DISABLED)
        self.break_connection.grid(row = 0, column = 1)
        self.plot_decoding = tk.Button(self.buttons, text = "Show plot", height = 1, width = 10, state = DISABLED)
        self.plot_decoding.grid(row = 0, column = 2)

        # ABOUT
        self.about = tk.Frame(self.root, padx=10, pady=10)
        self.about.grid(row = 4, column = 14, padx = (10, 0), pady = (10, 0), columnspan = 2, sticky = "NSEW")        
        self.information = tk.Label(self.about, text="About pyDecNef...", fg="blue", cursor="hand2")
        self.information.grid(row = 0, column = 1, columnspan= 2)
        self.information.pack()
        self.information.bind("<Button-1>", lambda e: self.access_url("https://github.com/pedromargolles/fMRI_decoding_neurofeedback"))

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def select_fmri_folder_cmd(self):
        self.fmri_directory = filedialog.askdirectory()
        self.selected_fmri_folder.insert(tk.END, self.fmri_directory)

    def select_outputs_folder_cmd(self):
        self.outputs_directory = filedialog.askdirectory()
        self.selected_outputs_folder.insert(tk.END, self.outputs_directory)

    def do_something(self):
        self.status_label.configure(text="Process Started")
        self.status_label.update()
        time.sleep(5) #some process/script that takes few seconds to execute
        self.status_label.configure(text="Finish")

    def on_closing(self):
        if messagebox.askokcancel(title = 'Save config',
                                  message = "Do you want to save the actual config for next time?",
                                 ):
            self.root.destroy()
            sys.exit()

    def access_url(self, url):
        webbrowser.open_new_tab(url)

gui = GUI()