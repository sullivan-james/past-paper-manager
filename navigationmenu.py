import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

class NavigationMenu(ctk.CTkFrame):


    class NavigationButton(ctk.CTkButton):

        def clicked_handler(self):
            self.controller.reset_buttons_text()

            self.configure(text="> " + self.button_details["text"] + " <")


        def click_event(self):
            self.button_details["command"](self.button_details["param"])
            
        def reset_text(self):
            self.configure(text=self.button_details["text"])

        def __init__(self,parent,controller,button_details,corner_radius=0,height=40,border_spacing=20,fg_color="transparent",text_color=("gray10", "gray90"),hover_color=("#325882", "#14375e")):
            self.clicked = False
            self.controller=controller
            self.button_details=button_details
            self.parent=parent
            super().__init__(parent, corner_radius=corner_radius, height=height, 
                             border_spacing=border_spacing, text=button_details["text"],
                            fg_color=fg_color, text_color=text_color,
                            anchor="ew",command=self.click_event)

    def reset_buttons_text(self):
        for button in self.buttons:
            button["object"].reset_text()

    def page_selected(self,selected):
        for button in self.buttons:
            if button["code"]==selected:

                button["object"].clicked_handler()


    def expand(self,event=None):
        self.navigation_frame.grid(row=1,column=0,sticky="new",columnspan=3)
        self.navigation_label.grid(row=0,column=0,sticky="nw",padx=(self.border_spacing,0),pady=(0,0))

        if self.collapse_button_flag:
            try:
                self.expand_button.grid_forget()
            except Exception as e:
                pass
            self.collapse_button.grid(row=0,column=1,sticky="nsw")


    def collapse(self,event=None):
        self.navigation_frame.grid_forget()
        self.navigation_label.grid_forget()

        if self.collapse_button_flag:
            try:
                self.collapse_button.grid_forget()
            except Exception as e:
                pass
            self.expand_button.grid(row=0,column=0,sticky="nw")


    def __init__(self,frame,mainline,buttons,text="Navigation",corner_radius=0,height=40,border_spacing=20,fg_color="transparent",text_color=("gray10", "gray90"),hover_color=("#325882", "#14375e"),heading_font=("Arial", 21),collapse_button=False):
        super().__init__(frame,corner_radius=corner_radius,fg_color=mainline.colors.bubble_background)
        self.collapse_button_flag=collapse_button
        if self.collapse_button_flag:
            self.expand_button = ctk.CTkButton(self,text="≡",command=self.expand,border_spacing=0,width=30,font=(None,34),fg_color="transparent",bg_color="transparent",hover_color="gray50",text_color="black")
            self.collapse_button = ctk.CTkButton(self,text="✕",command=self.collapse,border_spacing=0,width=30,font=(None,27),fg_color="transparent",bg_color="transparent",hover_color="gray50",text_color="black")
        

        self.height=height
        self.border_spacing=border_spacing
        self.fg_color=fg_color
        self.text_color=text_color
        self.hover_color=hover_color

        self.buttons=buttons

        self.grid_rowconfigure(1,weight=1)

        self.navigation_frame=ctk.CTkFrame(self,fg_color="transparent")



        self.navigation_label = ctk.CTkLabel(self,text_color=self.text_color,anchor="w",height=40,text=text,font=heading_font)


        self.expand()
        
        
        row = 0


        separator = ttk.Separator(self.navigation_frame,orient='horizontal')
        separator.grid(row=row,column=0,padx=0,sticky="ew",pady=(0,10))

        row += 1

        for i,button in enumerate(self.buttons):
            button_obj = self.NavigationButton(self.navigation_frame,self,button,corner_radius=0, height=self.height, border_spacing=self.border_spacing,fg_color=self.fg_color, text_color=self.text_color)

            #button_obj = ctk.CTkButton(self, corner_radius=self.corner_radius, height=self.height, border_spacing=self.border_spacing, text=button["text"],
            #                                    fg_color=self.fg_color, text_color=self.text_color,
            #                                    anchor="w",command=lambda: button["command"](button["param"]))
            
            if i == len(self.buttons)-1: pady=(0,15)
            else: pady=0
            
            if button["position"]=="bottom":
                self.navigation_frame.grid_rowconfigure(row-1, weight=1)

                button_obj.grid(row=row, column=0, sticky="sew",pady=pady)
            
            if button["position"]=="top":
                button_obj.grid(row=row, column=0, sticky="new",pady=pady)

            button["object"]=button_obj

            row += 1
            