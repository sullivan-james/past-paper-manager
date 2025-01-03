import os,json
import tkinter as tk
import CommonFunctions,shutil


class CourseObject:

    def remove_command(self):
        self.controller.remove_file(self,self.get_valid()[0])

    def is_datatype(self,value,datatype):
        if datatype==bool:
            if value == "True" or value == "False" or value == True or value == False: return True
            else:return False
        try:
            datatype(value)
            return True
        except Exception as e:
            return False

    def convert_list(self,string,separator):
        if string != "":
            try:
                list_string = string.replace("[","").replace("]","").replace('"',"").replace("'","").split(separator)
                return list_string
            except Exception as e:
                self.errors.append("List fail.")
                return []
        else:
            return []

    def convert_dict(self,string):
        if string != "":
            try:
                list_string = json.loads(string.replace("'",'"'))
                return list_string
            except Exception as e:
                self.errors.append("JSON fail.")
                return {}
            
        else:
            return {}

    def read_json(self,dict,key,datatype,master,if_empty=""):
        if key in dict:
            if self.is_datatype(dict[key],datatype):
                if datatype == bool:
                    if dict[key] == "True":return True
                    if dict[key]== "False":return False
                else:
                    return datatype(dict[key])
            else:
                self.errors.append(f"'{master} / {key}' (value: {str(dict[key])}) invalid (required: {str(datatype)}).")
                return if_empty
        else:
            self.errors.append(f"'{master} / {key}' not found in json file.")
            return if_empty

    def is_empty(self,items):
        empty_errors=[]


        for item in items:
            if (item[0] == "" or item[0] == None or item[0] == "None") and not item[1]:
                empty_errors.append(f"'{item[2]}' does not have a value.")
        if len(empty_errors) > 0:
            return True,empty_errors
        return False,[]
    
    def get_terminology_from_string(self,string):
        if string.lower() == "name":
            return self.name
        elif string.lower() == "year":
            return self.year
        elif string.lower() == 'session':
            return self.session
        elif string.lower() == "notes":
            return self.notes
        elif string.lower() == "timezone":
            return self.timezone
        elif string.lower() == "paper":
            return self.paper
        elif string.lower() == "subject":
            return self.subject
        elif string.lower() == "level":
            return self.level

    def get_valid(self):
        if self.critical_error:
            return False,self.errors
    
        is_empty,empty_errors=self.is_empty([
            (self.name,not self.show_name,"Terminology / name"),
            (self.year,not self.show_year,"Terminology / year"),
            (self.session,not self.show_session,"Terminology / session"),
            (self.notes,not self.show_notes,"Terminology / notes"),
            (self.timezone,not self.show_timezone,"Terminology / timezone"),
            (self.paper,not self.show_paper,"Terminology / paper"),
            (self.subject,not self.show_subject,"Terminology / subject"),
            (self.level,not self.show_level,"Terminology / level"),
            (self.acronym_timezone,False,"Terminology / acronym_timezone"),
            (self.acronym_questionpaper,False,"Terminology / acronym_questionpaper"),
            (self.acronym_markscheme,False,"Terminology / acronym_markscheme"),
            (self.gradeboundary,False,"Terminology / gradeboundary"),
            (self.gradeboundaries,False,"Terminology / gradeboundaries"),
            (self.grade,False,"Terminology / grade"),
            (self.grades,False,"Terminology / grades"),
            (self.questionpaper,False,"Terminology / questionpaper"),
            (self.markscheme,False,"Terminology / markscheme"),]
        )


        self.all_errors = self.errors + empty_errors
        if len(self.all_errors) > 0:
            self.course_name="ERROR"
            return False, self.errors + empty_errors
        return True,[]
    
    def get_critical_valid(self):

        if self.course_name != "" and self.course_code != "":
            return True
        return False

    def __init__(self,controller,json_data,path,json_error=""):
        self.path=path
        self.critical_error=False
        self.errors = []


        self.name=""
        self.year=""
        self.session=""
        self.notes=""
        self.timezone=""
        self.paper=""
        self.subject=""
        self.level=""
        self.acronym_timezone=""
        self.acronym_questionpaper=""
        self.acronym_markscheme=""
        self.gradeboundary=""
        self.gradeboundaries=""
        self.grade=""
        self.grades=""
        self.questionpaper=""
        self.markscheme=""

        self.show_name=True
        self.show_year=True
        self.show_session=True
        self.show_notes=True
        self.show_timezone=True
        self.show_paper=True
        self.show_subject=True
        self.show_level=True

        self.find_year="anywhere"
        self.find_session="anywhere"
        self.find_timezone="anywhere"
        self.find_paper="anywhere"
        self.find_subject="anywhere"
        self.find_level="anywhere"

        if json_data == {}:
            self.course_name=path
            self.course_code=""
            self.errors.append(f"CRITICAL ERROR: Invalid JSON file format:\nPlease fix the file format or re-install the JSON file\n\nError message: '{json_error}'.")
            self.critical_error=True
        else:
            self.controller=controller
            self.path=path
            self.json_data=json_data
            self.inject_metadata()
            self.inject_terminology()
            self.inject_flags()
            self.inject_autofills()
            self.inject_regex()
            self.get_valid()

    def set_duplicate_invalid(self):
        self.errors.append(f"DUPLICATE ERROR: Course code '{self.course_code}' configuration already exists")
        self.get_valid()

    def inject_metadata(self):
        if "Metadata" in self.json_data:
            metadata=self.json_data["Metadata"]
            self.course_code=self.read_json(metadata,"course_code",str,"Metadata")
            if self.course_code == "":
                self.course_code = self.path
                self.errors.append(f"CRITICAL ERROR: 'Metadata / course_code' does not have a value.")
                self.course_name=""
            else:
                self.course_name=self.read_json(metadata,"course_name",str,"Metadata")
            
            
            if self.course_name == "":
                self.course_name = "ERROR"
                self.errors.append(f"CRITICAL ERROR: 'Metadata / course_name' does not have a value.")


            self.grade_boundaries_with_defaults=self.convert_dict(self.read_json(metadata,"grade_boundaries",str,"Metadata"))
            
            print(self.grade_boundaries_with_defaults)
            self.grade_boundaries = []
            self.default_grade_boundaries = []
            # generate array of grade boundaries
            for grade_boundary_with_default in self.grade_boundaries_with_defaults:
                self.grade_boundaries.append(grade_boundary_with_default)
                self.default_grade_boundaries.append(self.grade_boundaries_with_defaults[grade_boundary_with_default])



            self.default_grade_boundary_max=self.read_json(metadata,"default_grade_boundary_max",int,"Metadata")


    def inject_terminology(self):
        if "Terminology" in self.json_data:
            terminology=self.json_data["Terminology"]
            self.name=self.read_json(terminology,"name",str,"Terminology")
            self.year=self.read_json(terminology,"year",str,"Terminology")
            self.session=self.read_json(terminology,"session",str,"Terminology")
            self.timezone=self.read_json(terminology,"timezone",str,"Terminology")
            self.paper=self.read_json(terminology,"paper",str,"Terminology")
            self.subject=self.read_json(terminology,"subject",str,"Terminology")
            self.level=self.read_json(terminology,"level",str,"Terminology")
            self.gradeboundary=self.read_json(terminology,"gradeboundary",str,"Terminology")
            self.gradeboundaries=self.read_json(terminology,"gradeboundaries",str,"Terminology")
            self.grade=self.read_json(terminology,"grade",str,"Terminology")
            self.grades=self.read_json(terminology,"grades",str,"Terminology")
            self.questionpaper=self.read_json(terminology,"questionpaper",str,"Terminology")
            self.markscheme=self.read_json(terminology,"markscheme",str,"Terminology")
            self.notes=self.read_json(terminology,"notes",str,"Terminology")
            self.acronym_timezone=self.read_json(terminology,"acronym_timezone",str,"Terminology")
            self.acronym_questionpaper=self.read_json(terminology,"acronym_questionpaper",str,"Terminology")
            self.acronym_markscheme=self.read_json(terminology,"acronym_markscheme",str,"Terminology")
        else:
            self.errors.append("Terminology section does not exist in json file.")

    def inject_flags(self):
        
        if "Flags" in self.json_data:
            flags=self.json_data["Flags"]
            self.show_name=self.read_json(flags,"show_name",bool,"Flags")
            self.show_year=self.read_json(flags,"show_year",bool,"Flags")
            self.show_notes=self.read_json(flags,"show_notes",bool,"Flags")
            self.show_session=self.read_json(flags,"show_session",bool,"Flags")
            self.show_timezone=self.read_json(flags,"show_timezone",bool,"Flags")
            self.show_paper=self.read_json(flags,"show_paper",bool,"Flags")
            self.show_subject=self.read_json(flags,"show_subject",bool,"Flags")
            self.show_level=self.read_json(flags,"show_level",bool,"Flags")
            self.show_gradeboundaries=self.read_json(flags,"show_gradeboundaries",bool,"Flags")
        else:
            self.errors.append("Flags section does not exist in json file.")

    def inject_autofills(self):
        if "Autofills" in self.json_data:
            autofills=self.json_data["Autofills"]
            self.dict_session=self.convert_dict(self.read_json(autofills,"dict_session",str,"Autofills"))
            self.dict_timezone=self.convert_dict(self.read_json(autofills,"dict_timezone",str,"Autofills"))
            self.dict_paper=self.convert_dict(self.read_json(autofills,"dict_paper",str,"Autofills"))
            self.dict_level=self.convert_dict(self.read_json(autofills,"dict_level",str,"Autofills"))
        else:
            self.errors.append("Autofills section does not exist in json file.")


    def inject_regex(self):
        
        if "Regex" in self.json_data:
            regex=self.json_data["Regex"]
            self.regex_year=self.read_json(regex,"regex_year",str,"Regex")
            self.regex_session=self.read_json(regex,"regex_session",str,"Regex")
            self.key_session=self.read_json(regex,"key_session",dict,"Regex")
            self.regex_timezone=self.read_json(regex,"regex_timezone",str,"Regex")
            self.key_timezone=self.read_json(regex,"key_timezone",dict,"Regex")
            self.regex_paper=self.read_json(regex,"regex_paper",str,"Regex")
            self.key_paper=self.read_json(regex,"key_paper",dict,"Regex")
            self.regex_subject=self.read_json(regex,"regex_subject",str,"Regex")
            self.regex_level=self.read_json(regex,"regex_level",str,"Regex")
            self.key_level=self.read_json(regex,"key_level",dict,"Regex")
            self.regex_other=self.read_json(regex,"regex_other",str,"Regex")
            self.identifiers_questionpaper=self.read_json(regex,"identifiers_questionpaper",list,"Regex")
            self.identifiers_markscheme=self.read_json(regex,"identifiers_markscheme",list,"Regex")
            self.identifiers_attachment=self.read_json(regex,"identifiers_attachment",list,"Regex")  
            self.suffix_questionpaper=self.read_json(regex,"suffix_questionpaper",list,"Regex")
            self.suffix_markscheme=self.read_json(regex,"suffix_markscheme",list,"Regex")
            self.suffix_attachment=self.read_json(regex,"suffix_attachment",list,"Regex")
            self.minimum_requirements=self.read_json(regex,"minimum_requirements",list,"Regex")
            self.find_year=self.read_json(regex,"find_year",str,"Regex","anywhere")
            self.find_session=self.read_json(regex,"find_session",str,"Regex","anywhere")
            self.find_timezone=self.read_json(regex,"find_timezone",str,"Regex","anywhere")
            self.find_paper=self.read_json(regex,"find_paper",str,"Regex","anywhere")
            self.find_subject=self.read_json(regex,"find_subject",str,"Regex","anywhere")
            self.find_level=self.read_json(regex,"find_level",str,"Regex","anywhere")
        else:
            self.errors.append("Regex section does not exist in json file.")

    def get_course_code(self):
        return self.course_code



class CoursesHandler:
    """Handle the deserialisation of course input files"""    

    def unpack_json_file(self,path):
        
        # Opening JSON file
        f = open(path)
        
        # returns JSON object as 
        # a dictionary
        error=""
        try:
            data = json.load(f)
        except Exception as e:
            data = {}
            error = str(e)

        course_object=CourseObject(self,data,path,json_error=error)

        if course_object.get_valid()[0]:
            if not self.check_duplicate(course_object):
                self.course_objects[course_object.get_course_code()]=course_object
        self.all_courses_objects.append(course_object)        

        #if course_object.get_critical_valid():
        #    return course_object
        return

    def remove_file(self,course_obj,valid = True):        
        os.remove(course_obj.path)

    def check_duplicate(self,course_obj):

        if course_obj.course_code in self.course_objects:
            course_obj.set_duplicate_invalid()
            return True
        return False

    

    def add_new_course(self,path):


        file_name = os.path.basename(path)
        



        if os.path.exists(self.appdata_courses_directory):
            tk.messagebox.showwarning(title="Override",message=f"File of the name {file_name} already exists in the course configuration folder:\n\n{CommonFunctions.get_cwd_file('courses')}")
        else:
            shutil.copy(path,self.appdata_courses_directory)

            f = open(self.appdata_courses_directory)
            error=""
            try:
                data = json.load(f)
            except Exception as e:
                data = {}
                error=str(e)
                return False
                
            course_object = CourseObject(self,data,self.appdata_courses_directory,json_error=error)

            if course_object.get_valid():
                if not self.check_duplicate(course_object):
                    self.course_objects[course_object.course_code]=course_object
            self.all_courses_objects.append(course_object)

            return True

    def __init__(self,store_courses_directory,appdata_courses_directory):
        """
        Args:
            path (str): the location of all course json resource files
        """        
        
        self.course_objects={} # dict of valid course objects
        self.all_courses_objects=[] # list of all (incl. invalid course objects)
        self.store_courses_directory=store_courses_directory
        self.appdata_courses_directory=appdata_courses_directory
        # Create courses folder in the AppData folder
        if not os.path.exists(appdata_courses_directory):
            os.makedirs(appdata_courses_directory)

        # iterate over all json files in the Store directory (the default courses shipped with the product).
        # These must be copied over into the AppData folder to allow the user to install their own Course files alongside the default shipped files.
        ext = ('.json')
        for file in os.listdir(store_courses_directory):
            if file.endswith(ext):
                if not os.path.exists(os.path.join(appdata_courses_directory,file)):
                    shutil.copy(os.path.join(store_courses_directory,file),os.path.join(appdata_courses_directory,file))


        for file in os.listdir(appdata_courses_directory):
            if file.endswith(ext):
                self.unpack_json_file(os.path.join(appdata_courses_directory,file))


