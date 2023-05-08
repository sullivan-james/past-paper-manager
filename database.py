import datetime
import json
import shutil
import pandas as pd
import tkinter as tk
import numpy as np
import sys, os
import random
import values_and_rules
import customtkinter as ctk
import uuid





class PaperObject():

    def __init__(self, db, mainline):
        
        self.db=db
        self.mainline = mainline
        
      
        self.__id = uuid.uuid4()
        
        
        self.db_index=None
        self.db_row=None
        self.db_row_injected=False
        self.__ignore_update = False
        self.__normal_format = True

        self.__course_type=self.mainline.settings.get_course_type()


        self.__custom_name = ""
        
        self.__year = "" # IB AL

        self.__session = "" # IB AL

        self.__timezone = "" # IB AL
        
        self.__paper = "" # IB AL

        self.__subject = "" # IB AL
        
        self.__level = "" # IB

        # TODO: REMOVE
        self.__questions = ""

        self.__original = []

        self.__markscheme = []

        self.__otherattachments = []

        self.__printed = False

        self.__completed_date = np.datetime64('NaT')

        self.__completed_date_datetime = None

        self.__completed = False

        self.__partial = False

        self.__mark = 0.00

        self.__maximum = 0.00

        self.__percentage=-1

        self.__notes = ""

        self.__original_valid=False

        self.__markscheme_valid=False

        self.__otherattachments_valid=False
        
        
        # define a dictionary with key: grade boundary codes, value: grade boundary value            
        self.__grade_boundaries = {}
        self.__grade_boundaries_percentages = {}

        for grade_boundary in values_and_rules.get_course_grade_boundaries()[self.__course_type]:
            self.__grade_boundaries[grade_boundary]=0
            self.__grade_boundaries_percentages[grade_boundary]=0

        self.__gbmax = 0
        self.__grade = -1


        self.__name = ""

    def set_grade(self):
        pass
        


    def get_grade(self):
        return self.__grade

    def is_float(self,element) -> bool:
        try:
            float(element)
            return True
        except ValueError:
            return False

    def delete_item(self):

        self.db.drop(self.db_index,inplace=True)
        self.db.to_csv('database.csv',index=False)
        self.mainline.db_object.paper_objects[self.db_index] = None
        for index,item in enumerate(self.__original):
            self.delete_path("original",index, ignore_removed_pdf = True)
        for index,item in enumerate(self.__markscheme):
            self.delete_path("markscheme",index, ignore_removed_pdf = True)
        for index,item in enumerate(self.__otherattachments):
            self.delete_path("otherattachments",index, ignore_removed_pdf = True)

        
        self.mainline.clean_dir()

    def set_db_index(self,new_index):
        self.db_index = new_index

    def reformat_integers(self):
        if self.is_float(self.__year): self.__year = str(int(self.__year))
        else: 
            self.__year = ""
        
        if self.is_float(self.__timezone): self.__timezone = str(int(self.__timezone))
        else: 
            self.__timezone = ""

        if self.is_float(self.__paper): 
            self.__paper = str(int(self.__paper))
        else: 
            self.__paper = ""

        if self.is_float(self.__mark): self.__mark = float(self.__mark)
        else: 
            self.__mark = ""

        if self.is_float(self.__maximum): self.__maximum = float(self.__maximum)
        else: 
            self.__maximum = ""

    def assign_db_data(self,db_row, db_index):
        self.db_index = db_index
        self.db_row = db_row
        self.db_row_injected=True

        # reading in all rows from the database
        id = self.db_row["ID"]

        if id != "":

            self.__id = id


        self.__normal_format = self.db_row["NormalFormat"]
        self.__custom_name = self.db_row["CustomName"]            
        self.__course_type = self.db_row["CourseType"]
        self.__session = self.db_row["Session"]
        self.__year = self.db_row["Year"]
        self.__timezone = self.db_row["Timezone"]
        self.__paper = self.db_row["Paper"]

        self.__ignore_update = self.db_row["IgnoreUpdate"]
        
        self.__subject = self.db_row["Subject"]
        self.__level = self.db_row["Level"]
        self.__questions = self.db_row["Questions"]
        
        self.__original = json.loads(str(self.db_row["Original"]))
        self.__markscheme = json.loads(str(self.db_row["Markscheme"]))
        self.__otherattachments = json.loads(str(self.db_row["OtherAttachments"]))

        grade_boundaries=json.loads(str(self.db_row["GradeBoundaries"]) or "{}")
        if grade_boundaries != {}:
            self.__grade_boundaries = grade_boundaries

        self.reformat_integers()


        self.__printed = self.db_row["Printed"]
        
        self.__completed_date = self.db_row["CompletedDate"]
        
        self.__completed = self.db_row["Completed"]
        self.__partial = self.db_row["Partial"]
        self.__mark = self.db_row["Mark"]
        self.__maximum = self.db_row["Maximum"]
        self.__notes = self.db_row["Notes"]


        self.__gbmax=self.db_row["GBMAX"]
        
        self.update_database(clean_dir=False)


    def create_file_name(self, type, unique_identifier = ""):
        if type == "original": prefix = "original"
        if type == "markscheme": prefix = "markscheme"
        if type == "otherattachments": prefix = "attachment"



        new_file_name = prefix+"-"+self.__name
        if unique_identifier != "":
            new_file_name = new_file_name + "-" + unique_identifier
        new_file_name += ".pdf"
        return new_file_name

    def get_ignore_update(self):
        return self.__ignore_update
    def set_ignore_update(self,ignore_update):
        self.__ignore_update = ignore_update



    def set_grade_boundary(self,grade_boundary_code, grade_boundary_value):
        """
        IN:
        - the grade boundary (code) being modified
        - the value to be inserted into that grade boundary
        OUT:
        - void
        """

        self.__grade_boundaries[grade_boundary_code]=grade_boundary_value

    def get_grade_boundary(self,grade_boundary_code):
        return self.__grade_boundaries[grade_boundary_code]

    def get_grade_boudary_percentage(self,grade_boundary_code):
        return self.__grade_boundaries_percentages[grade_boundary_code]




    def set_gbmax(self,gbmax):
        self.__gbmax=gbmax
    def get_gbmax(self):
        return self.__gbmax


    def is_valid_gbmax(self):
        if self.is_float(self.__gbmax):
            if float(self.__gbmax) > 0:
                return True
        return False

    def is_valid_grade_boundaries(self):
        """
        Check if the dictionary of grade boundaries is valid AND calculate percentages. Rules:
        - all GB values must be float
        - all GB values must be 0 or greater
        """

        for grade_boundary in self.__grade_boundaries:
            value = self.__grade_boundaries[grade_boundary]
            if self.is_float(value):
                if float(value) >= 0 and self.is_valid_gbmax():
                    self.__grade_boundaries_percentages[grade_boundary]=float(value)/float(self.__gbmax)

        self.generate_grade()

    def generate_name(self):
        self.__name = self.create_name()


    def update_object(self,copy=False,override_duplicate_warning=False):
        """
        FUNCTION: complete a range of checks and tests on the data fields within this object, including the following:
        - set the field name
        - check path validity of all three paths
        - check the mark and maximum fields, and calculate a percentage score
        """
        
        if pd.isnull(self.__completed_date):self.__completed_date_datetime=None
        else:self.__completed_date_datetime=self.__completed_date.to_pydatetime()

        self.reformat_integers()
        
        if self.__custom_name != "":
            self.__normal_format = False
        else:
            self.__normal_format = True
        

        # check mark and maximum validity, calculate decimal / percentage score
        self.__mark_exists, self.__percentage, self.__mark, self.__maximum = self.check_valid_mark_and_maximum()

        self.is_valid_grade_boundaries()

        # custom fields which are specific to the database
        self.__name = self.create_name()
        # check the given path fields (for the original past paper document, markscheme document and scanned PDF document)
        for index,path_dictionary in enumerate(self.__original):
            path_dictionary["valid"], path_dictionary["path"] = self.check_path_exists(path_dictionary["path"])

            if not path_dictionary["valid"]:
                del self.__original[index]
            else:
                if os.path.join(self.create_path_for_files(),self.create_file_name("original",path_dictionary["identifier"])) != path_dictionary["path"]:
                    if self.is_valid_pdf(path_dictionary["path"]):
                        self.move_file_location("original",os.path.join(os.getcwd(),path_dictionary["path"]),custom_identifier=path_dictionary["identifier"],set_function_index=index,copy=copy,ignore_duplicate=override_duplicate_warning)


        # check the given path fields (for the markscheme past paper document, markscheme document and scanned PDF document)
        for index,path_dictionary in enumerate(self.__markscheme):
            path_dictionary["valid"], path_dictionary["path"] = self.check_path_exists(path_dictionary["path"])
            if not path_dictionary["valid"]:
                del self.__markscheme[index]
            else:
                if os.path.join(self.create_path_for_files(),self.create_file_name("markscheme",path_dictionary["identifier"])) != path_dictionary["path"]:
                    if self.is_valid_pdf(path_dictionary["path"]):
                        self.move_file_location("markscheme",os.path.join(os.getcwd(),path_dictionary["path"]),custom_identifier=path_dictionary["identifier"],set_function_index=index,copy=copy,ignore_duplicate=override_duplicate_warning)
        
        # check the given path fields (for the scanned past paper document, markscheme document and scanned PDF document)
        for index,path_dictionary in enumerate(self.__otherattachments):
            path_dictionary["valid"], path_dictionary["path"] = self.check_path_exists(path_dictionary["path"])
            if not path_dictionary["valid"]:
                del self.__otherattachments[index]
            else:
                if os.path.join(self.create_path_for_files(),self.create_file_name("otherattachments",path_dictionary["identifier"])) != path_dictionary["path"]:
                    if self.is_valid_pdf(path_dictionary["path"]):
                        self.move_file_location("otherattachments",os.path.join(os.getcwd(),path_dictionary["path"]),custom_identifier=path_dictionary["identifier"],set_function_index=index,copy=copy,ignore_duplicate=override_duplicate_warning)



    def is_valid_pdf(self,path):
        if os.path.exists(os.path.join(os.getcwd(),path)) and str(path)[-4:] == ".pdf": 
            return True
        else: return False

    def pretty_level(self):
        if self.__level == "SL": return "Standard Level"
        if self.__level == "HL": return "Higher Level"
        else: return self.__level

    def create_path_for_files(self):

        path = "Papers"
        path += "/" + values_and_rules.get_course_types()[self.__course_type]
        if self.pretty_subject() != "": path += "/" + self.pretty_subject()
        if self.pretty_level() != "": path += "/" + self.pretty_level()
        if self.pretty_year() != "": path += "/" + self.pretty_year()
        if self.pretty_session() != "": path += "/" + self.pretty_session()
        if self.pretty_timezone() != "": path += "/" + self.pretty_timezone()


        return path

    def update_database(self, pdf_files_only = False,clean_dir = True,copy=False,override_duplicate_warning=False):
        """
        FUNCTION: sync the internal object elements from this class with those of the original Pandas database
        WARNING: ALL ELEMENTS WITHIN THIS OBJECT MUST BE A VALID DATATYPE FOR THE PANDAS DATAFRAME. Use the self.update_object() method before calling this one
        """
        self.update_object(copy=copy,override_duplicate_warning=override_duplicate_warning)    
        if self.db_row_injected == False:
            none_array = []
            
            
            for i in list(range(len(self.db.columns))):
                none_array.append(None)

            self.db.loc[self.db.shape[0]] = none_array
            self.db_row_injected=True
            
        if pdf_files_only == False:

            self.db.at[self.db_index, "ID"] = self.__id

            self.db.at[self.db_index, "NormalFormat"] = self.__normal_format
            self.db.at[self.db_index, "CourseType"] = self.__course_type
            self.db.at[self.db_index, "CustomName"] = self.__custom_name
            self.db.at[self.db_index, "Year"] = str(self.__year)
            self.db.at[self.db_index, "Session"] = self.__session
            self.db.at[self.db_index, "Timezone"] = str(self.__timezone)
            self.db.at[self.db_index, "Paper"] = self.__paper
            self.db.at[self.db_index, "Subject"] = self.__subject
            self.db.at[self.db_index, "Level"] = self.__level
            self.db.at[self.db_index, "Questions"] = self.__questions
            self.db.at[self.db_index, "Printed"] = self.__printed
            self.db.at[self.db_index, "CompletedDate"] = self.__completed_date
            self.db.at[self.db_index, "Completed"] = self.__completed
            self.db.at[self.db_index, "Partial"] = self.__partial
            self.db.at[self.db_index, "Mark"] = self.__mark
            self.db.at[self.db_index, "Maximum"] = self.__maximum
            self.db.at[self.db_index, "Notes"] = self.__notes
            self.db.at[self.db_index, "IgnoreUpdate"] = self.__ignore_update
        
            self.db.at[self.db_index, "GradeBoundaries"] = json.dumps(self.__grade_boundaries)

            self.db.at[self.db_index, "GBMAX"] = self.__gbmax
            #print(self.db)
        self.db.at[self.db_index, "Original"] = json.dumps(self.__original)
        self.db.at[self.db_index, "Markscheme"] = json.dumps(self.__markscheme)
        self.db.at[self.db_index, "OtherAttachments"] = json.dumps(self.__otherattachments)
        self.db.to_csv('database.csv',index=False)

        if clean_dir:
            self.mainline.clean_dir()



    def pretty_year(self):
        if len(str(self.__year)) == 2: return "20" + str(self.__year)
        else: return str(self.__year)

    def pretty_session(self):
        if self.__session == "M":return "May"
        elif self.__session == "N":return "November"
        elif self.__session == "TRL":return "Trial"
        else: return self.__session

    def pretty_timezone(self):
        if self.__timezone == "": 
            #print("ENMPTY")
            return ""
        else:
            return "TZ" + str(self.__timezone)

    def pretty_subject(self):
        if self.__subject == "MA": return "Mathematics"
        elif self.__subject == "PH": return "Physics"
        elif self.__subject == "BM": return "Business Management"
        elif self.__subject == "CS": return "Computer Science"
        elif self.__subject == "EN": return "English"
        else: return self.__subject

    def move_file_location(self, type, override_path = None, set_function_index=-1, custom_identifier="",copy=False,ignore_duplicate=False):
        """
        Move a PDF file to a new location
        IN:
        - type (str): original, markscheme or scanned
        - OPTIONAL override_path: the path of the current location of the PDF file needing to be moved
        - OPTIONAL set_function_index (default -1): the index of the directory being modified in the original/markscheme/scanned dictionaries
        - OPTIONAL custom_identifier (str): adds an identifier to the directory being added
        - OPTIONAL copy (default False): sets the copy/replace setting
        - OPTIONAL ignore_duplicate (default False): will override duplicates if set to True
        """
        # get the current working directory
        current_working_directory = os.getcwd()
        #print("INDEX",set_function_index)
        #print("CUSTOM1",custom_identifier)
        # generating the new paths for the selected item
        # TODO make MAC compatible
        
        self.path_dict = {}

        if type == "original":
            #relative_folder_path = self.create_path_for_files()
            #current_path = os.path.join(current_file_path,self.__original)
            set_function = self.set_original_path
            set_function_identifier = self.set_original_identifier
            get_function_identifier = self.get_original_identifier
            self.path_dict = self.__original
            #unique_identifier = self.get_original_identifier(set_function_index)
        elif type == "markscheme":
            #relative_folder_path = self.create_path_for_files()
            #current_path = os.path.join(current_file_path,self.__markscheme)
            set_function = self.set_markscheme_path
            get_function_identifier = self.get_markscheme_identifier
            set_function_identifier = self.set_markscheme_identifier
            self.path_dict = self.__markscheme
            #unique_identifier = self.get_markscheme_identifier(set_function_index)

        elif type == "otherattachments":

            set_function = self.set_otherattachments_path
            set_function_identifier = self.set_otherattachments_identifier
            get_function_identifier = self.get_otherattachments_identifier

            self.path_dict = self.__otherattachments
            #unique_identifier = self.get_scanned_identifier(set_function_index)
        
        relative_folder_path = self.create_path_for_files()
        if override_path != None:
            current_path = override_path

        new_path = os.path.join(current_working_directory,relative_folder_path)
        
        # make the target directory if it does not yet exist
        if not os.path.exists(new_path):
            os.makedirs(new_path)

        # check if the target file already exists
        override = True


        new_file_name = self.create_file_name(type,custom_identifier)


        if os.path.exists(os.path.join(new_path,new_file_name)) and not ignore_duplicate:



            override = tk.messagebox.askyesnocancel(message=f"The file {new_file_name} already exists in {new_path}. Would you like to override it (YES) or create an automatic new custom file name (NO) or cancel (CANCEL)?")
            if override:
                for i,current_paths in enumerate(self.path_dict):
                    print(current_paths)
                    if current_paths["path"] == os.path.join(relative_folder_path,new_file_name):
                        del self.path_dict[i]
                    if current_paths["unique_identifier"] != "":
                        custom_identifier=current_paths["unique_identifier"]
            elif override == None:
                override = False
            else:
                custom_identifier=str(random.randint(100000,999999))
                new_file_name = self.create_file_name(type,custom_identifier)
                override = True
        
        if os.path.exists(os.path.join(new_path,new_file_name)) and ignore_duplicate:
            custom_identifier=custom_identifier+str(random.randint(100000,999999))
            new_file_name = self.create_file_name(type,custom_identifier)
            override = True

        if override == True:
            if copy == True:
                shutil.copy(current_path, os.path.join(new_path,new_file_name))
            else:
                shutil.move(current_path, os.path.join(new_path,new_file_name))
            new_index = set_function(os.path.join(relative_folder_path,new_file_name), index = set_function_index)
            print("IDENTIFIER",get_function_identifier(new_index))
            set_function_identifier(custom_identifier,new_index)




    def delete_path(self,type,index,ignore_removed_pdf=False):
        
        return_msg = ""
        if type == "original":
            return_msg = self.delete_original(index,ignore_removed_pdf=ignore_removed_pdf)
        if type == "markscheme":
            return_msg = self.delete_markscheme(index,ignore_removed_pdf=ignore_removed_pdf)
        if type == "otherattachments":
            return_msg = self.delete_otherattachments(index,ignore_removed_pdf=ignore_removed_pdf)
        return return_msg



    def browse_file_input(self, type,custom_identifier="",set_function_index=-1,completefunction=None):
        """
        Will prompt user for input on either the original, markscheme or original files
        IN:
        - type (str): indicate for which field this function is being used (either 'original', 'markscheme' or 'scanned')
        - set_function_index (int): the index of the path being changed in the original/markscheme/scanned dictionaries
        - OPTIONAL completefunction (default None): a function which is run once the change has been made
        """


        # TODO restrict to only PDF files
        path = tk.filedialog.askopenfilename(initialdir = "Downloads",title = f"Select the {type.title()} file")

        self.update_object()


        #print("CuSTOME",custom_identifier)

        self.move_file_location(type,override_path=path,set_function_index=set_function_index,custom_identifier=custom_identifier, copy=True)

        if completefunction != None:
            completefunction()
        
        #self.mainline.resetwindows("MainPage")

    def set_normal_format(self, normal_format):
        self.__normal_format=normal_format
    def set_custom_name(self, custom_name):
        self.__custom_name=custom_name
    def set_year(self, year):
        self.__year=str(year)
    def set_session(self, session):
        self.__session=session
    def set_timezone(self, timezone):
        self.__timezone=str(timezone)
    def set_paper(self, paper):
        self.__paper=str(paper)
    def set_subject(self, subject):
        self.__subject=subject
    def set_level(self, level):
        self.__level=level
    def set_questions(self, questions):
        self.__questions=questions

    def remove_file(self,path):
        try:
            os.remove(path)
            return True
        except Exception as e:
            return e



    def delete_original(self,index,ignore_removed_pdf=False):
        return_msg = self.remove_file(self.__original[index]["path"])
        if return_msg == True or ignore_removed_pdf==True: return self.__original.pop(index)
        else: return str(return_msg)


    def delete_markscheme(self,index,ignore_removed_pdf=False):
        return_msg = self.remove_file(self.__markscheme[index]["path"])
        if return_msg == True or ignore_removed_pdf==True: return self.__markscheme.pop(index)
        else: return str(return_msg)


    def delete_otherattachments(self,index,ignore_removed_pdf=False):
        return_msg = self.remove_file(self.__otherattachments[index]["path"])
        if return_msg == True or ignore_removed_pdf==True: return self.__otherattachments.pop(index)
        else: return str(return_msg)



    def set_original(self,original,index = -1):
        self.__original[index]["path"]=original

    def set_original_path(self, original, index = -1):
        if index == -1: 
            self.__original.append({"path":original,"valid":True,"identifier":""})
            return_index = len(self.__original)-1
        else:
            self.__original[index]["path"]=original
            return_index = index
        return return_index

    def remove_original_path(self,path):
        for i,path1 in enumerate(self.__original):
            if path1["path"]==path:
                self.__original.pop(i)

    def set_original_valid(self,original,index):

        self.__original[index]["valid"]=original

    def set_original_identifier(self,original,index):

        self.__original[index]["identifier"]=original


    def set_markscheme_path(self, markscheme, index = -1):
        if index == -1: 
            self.__markscheme.append({"path":markscheme,"valid":True,"identifier":""})
            return_index = len(self.__markscheme)-1
        else:
            self.__markscheme[index]["path"]=markscheme
            return_index = index
        return return_index

    def remove_markscheme_path(self,path):
        for i,path1 in enumerate(self.__markscheme):
            if path1["path"]==path:
                self.__markscheme.pop(i)


    def set_markscheme_valid(self,markscheme,index):

        self.__markscheme[index]["valid"]=markscheme

    def set_markscheme_identifier(self,markscheme,index):
        self.__markscheme[index]["identifier"]=markscheme

    def set_otherattachments_path(self, otherattachments, index = -1,unique_identifier=""):
        if index == -1: 
            self.__otherattachments.append({"path":otherattachments,"valid":True,"identifier":unique_identifier})
            return_index = len(self.__otherattachments)-1
        else:
            self.__otherattachments[index]["path"]=otherattachments
            return_index = index
        return return_index

    def remove_otherattachments_path(self,path):
        for i,path1 in enumerate(self.__otherattachments):
            if path1["path"]==path:
                self.__otherattachments.pop(i)

    def set_otherattachments_valid(self,otherattachments,index):

        self.__otherattachments[index]["valid"]=otherattachments

    def set_otherattachments_identifier(self,otherattachments,index):

        self.__otherattachments[index]["identifier"]=otherattachments

    def set_markscheme(self, markscheme, index = -1):
        if index == -1: 
            self.__markscheme.append(markscheme)
        else:
            self.__markscheme[index]=markscheme

    def set_otherattachments(self, otherattachments, index = -1):
        if index == -1: 
            self.__otherattachments.append(otherattachments)
        else:
            self.__otherattachments[index]=otherattachments

    def set_printed(self, printed):
        self.__printed=printed
    def set_completed_date(self, completed_date):

        self.__completed_date=completed_date
        self.__completed_date_datetime=self.__completed_date.to_pydatetime()
        if pd.isnull(self.__completed_date_datetime):self.__completed_date_datetime=None

    def set_completed(self, completed):
        self.__completed=completed
    def set_partial(self, partial):
        self.__partial=partial
    def set_mark(self, mark):
        if mark == "": self.__mark = 0.00
        else: self.__mark=float(mark)
    def set_maximum(self, maximum):
        if maximum == "": self.__maximum = 0.00
        else: self.__maximum=float(maximum)
    def set_notes(self, notes):
        self.__notes=notes
    def set_name(self, name):
        self.__name=name

    def open_file_directory(self):
        cwd = os.getcwd()
        path = self.create_path_for_files()
        if os.path.exists(os.path.join(cwd,path)):
            os.startfile(os.path.join(cwd,path))
        else:
            tk.messagebox.showerror(message=f"Unable to open {str(os.path.join(cwd,path))}. It could be that the path does not exist, or that you do not have the permissions to access it.")

    # getters and setters
    def get_course_type(self):
        return self.__course_type

    def get_normal_format(self):
        return self.__normal_format
    def get_custom_name(self):
        return self.__custom_name
    def get_year(self):
        return self.__year
    def get_session(self):
        return self.__session
    def get_timezone(self):
        return self.__timezone
    def get_paper(self):
        return self.__paper
    def get_subject(self):
        return self.__subject
    def get_level(self):
        return self.__level
    def get_questions(self):
        return self.__questions
    def get_original(self):
        return self.__original

    def get_original_identifier(self, index):

        if len(self.__original) == 0: return ""
        return self.__original[index]["identifier"]
    def get_original_path(self, index):

        if len(self.__original) == 0: return ""
        return self.__original[index]["path"]
    def get_original_valid(self, index):
        if len(self.__original) == 0: return ""
        return self.__original[index]["valid"]


    def get_markscheme_identifier(self, index):
        if len(self.__markscheme) == 0: return ""
        return self.__markscheme[index]["identifier"]
    def get_markscheme_path(self, index):
        if len(self.__markscheme) == 0: return ""
        return self.__markscheme[index]["path"]
    def get_markscheme_valid(self, index):
        if len(self.__markscheme) == 0: return ""
        return self.__markscheme[index]["valid"]


    def get_otherattachments_identifier(self, index):
        if len(self.__otherattachments) == 0: return ""
        return self.__otherattachments[index]["identifier"]
    def get_otherattachments_path(self, index):
        if len(self.__otherattachments) == 0: return ""
        return self.__otherattachments[index]["path"]
    def get_otherattachments_valid(self, index):
        if len(self.__otherattachments) == 0: return ""
        return self.__otherattachments[index]["valid"]

    def pass_setter(self,e):
        pass

    def get_markscheme(self, index = -1):
        return self.__markscheme
    def get_otherattachments(self, index = -1):
        return self.__otherattachments
    def get_printed(self):
        return self.__printed
    def get_completed_date(self):
        return self.__completed_date
    def get_completed_date_pretty(self):
        if self.__completed_date_datetime != None:
            return self.__completed_date_datetime.strftime("%d/%m/%Y")
        else: return "None selected"
    def get_completed_date_datetime(self):
        return self.__completed_date_datetime
    def get_completed(self):
        return self.__completed
    def get_partial(self):
        return self.__partial

    def get_notes(self):
        return self.__notes
    def get_id(self):
        return self.__id
    def get_name(self):
        return self.__name

    def set_percentage(self):
        pass
    def get_percentage(self):
        return self.__percentage
    def get_percentage_pretty(self):
        if self.__percentage != -1 and self.__maximum != 0:
            return str(self.__percentage * 100) + "%"
        else: return "Enter a result above"

    def get_grade_pretty(self):
        if str(self.__grade) != "-1" and self.__maximum != 0:
            return self.__grade
        else: return "Enter a result above"
    def get_mark(self):
        return self.__mark
    def get_maximum(self):
        return self.__maximum

    def generate_grade(self):
        

        if self.is_valid_gbmax():
            for grade_boundary in self.__grade_boundaries:
                
                grade_boundary_value_percentage = self.__grade_boundaries_percentages[grade_boundary]

                if self.__percentage >= grade_boundary_value_percentage:
                    self.__grade = grade_boundary
                    break # break out of loop
                self.__grade = -1 # edge case

    def check_valid_mark_and_maximum(self):
        """
        FUNCTION: check the validity of the mark and maximum, and then calculate a percentage score based on this response
        IN: none
        OUT:
        - mark_exists (bool): indicate whether mark and maximum are valid
        - percentage (float): decimal number to indicate the percentage score (0.00 if mark or maximum invalid)
        - mark (float): number indicating the mark for the paper (0.00 if invalid)
        - maximum (float): number indicating the maximum mark for the paper (0.00 if invalid)
        - 
        """



        mark_exists = True
        percentage = 0.00
        mark = 0.00
        maximum = 0.00

        # check type of mark and maximum
        if self.__mark != '' and self.__mark >= 0 and (isinstance(self.__mark, int) or isinstance(self.__mark, float)):
            mark = float(self.__mark)
        else: 
            mark_exists = False
        
        # note: maximum  MUST be greater than 0 for the percentage division
        if self.__maximum != '' and self.__maximum > 0 and (isinstance(self.__maximum, int) or isinstance(self.__maximum, float)):
            maximum = float(self.__maximum)
        else: 
            mark_exists = False

        # create a decimal percentage score based on mark and maximum
        if mark_exists == True:
            percentage = round(self.__mark / self.__maximum, 3 )
        


        return mark_exists, percentage, mark, maximum

    def check_path_exists(self,path):
        """
        Check whether a given path exists
        IN:
        - path (str): the path of the document being checked
        OUT:
        - valid (bool): indicating whether the given path is valid
        - path (str): the updated path (will be set to an empty string if invalid)
        """

        current_file_path = os.getcwd()

        valid = True
        if path == "":
            valid = False
        
        # TODO check to ensure the file is a PDF
        elif not os.path.exists(os.path.join(current_file_path,path)):
            valid = False
        
        return valid, path

    def create_name(self):
        """
        Creates a name for the object based on the data read from the dataframe. This name will either:
        - follow the conventional naming format for past papers
        - take on the custom name provided by the data if the data row does not adhere to the past paper formatting
        """
        
        
        name = ""
        if self.__normal_format == True:
            name_array = []

            if str(self.__session) != "": name_array.append(str(self.__session))
            if str(self.__year) != "": name_array.append(str(self.pretty_year()))
            if str(self.__timezone) != "": name_array.append("TZ" + str(self.__timezone))
            if str(self.__paper) != "": name_array.append("P" + str(self.__paper))
            if str(self.__subject) != "": name_array.append(str(self.__subject))
            if str(self.__level) != "": name_array.append(str(self.__level))


            #name_array = [str(self.__session), str(self.__year), "TZ"+str(self.__timezone), "P"+str(self.__paper), self.__subject, self.__level]
            if self.__questions != "": name_array.append(self.__questions)
            name = "-".join(str(i) for i in name_array)
        elif self.__normal_format == False:
            name = self.__custom_name


        return name


class Database():


    def __init__(self, db_path,mainline):

        self.mainline=mainline
        self.db = pd.read_csv(db_path)
        date = datetime.datetime.now()
        # make the target directory if it does not yet exist
        if not os.path.exists("Backups"):
            os.makedirs("Backups")
        current_date = date.strftime("%d_%m_%Y-%H_%M_%S")
        self.db.to_csv(f'Backups/database-{current_date}.csv',index=False)

        self.db.dropna(subset = ["NormalFormat"], inplace=True)
        error = False

        try:
            self.db.astype({'NormalFormat': 'bool','Printed': 'bool','Completed': 'bool','Partial': 'bool','IgnoreUpdate':'bool'},errors='raise')
        except Exception as e:
            error = True
            tk.messagebox.showerror(message="Error when parsing data and converting boolean (True/False) datatypes. As to prevent data from being overriden, the database will not be accessed or manipulated until this is fixed.\n\nPlease ensure the CSV data file has either TRUE or FALSE under the boolean columns")
        self.db = self.db.replace(np.nan, '')
        

        try:
            self.db["CompletedDate"] = pd.to_datetime(self.db['CompletedDate'], dayfirst=True, errors='raise')
        except Exception as e:
            error = True
            tk.messagebox.showerror(message="Error when reading the date fields from the database. As to prevent data from being overriden, the database will not be accessed or manipulated until this is fixed.\n\nPlease ensure the CSV date format has not been corrupted opening it in MS Excel. If so, open the CSV as change the date format to DD/MM/YYYY\n\nError: "+ str(e))
        if not error:

            self.paper_objects = []
            self.db_index = 0
            for self.db_index, row in self.db.iterrows():
                self.paper_objects.append(PaperObject(self.db, self.mainline))
                self.paper_objects[-1].assign_db_data(row,self.db_index)
        else:
            sys.exit()

    def create_new_row(self):
        """
        Will create a new database element, however will NOT save it to the pandas dataframe or an array. This new object must be passed into the save_row() function to do so.
        """
        new_row_object = PaperObject(self.db, self.mainline)
        return new_row_object

    def check_row_exists(self,row_obj):
        """
        Will check if a given row object already exists within the database, if it does, it will return that which already exists
        IN:
        - row_obj: the item being checked
        OUT:
        - exists (bool): True if it does already exist, False if it does not
        - row_obj_new: if the boolean above is true, the existing row_obj will be returned, and vice versa
        """
        #print (self.paper_objects)
        for row in self.paper_objects:
            if row != None:
                row_obj.update_object()
                row.update_object()
                if row.get_name() == row_obj.get_name():
                    return True, row
                else:
                    pass
        return False, row_obj

    def save_row(self, row, copy = True,override_duplicate_warning = True):
        self.db_index += 1
        row.set_db_index(self.db_index)
        self.paper_objects.append(row)
        row.update_database(copy = copy,override_duplicate_warning = override_duplicate_warning)
