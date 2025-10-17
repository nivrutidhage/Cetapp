from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.widget import Widget
from kivymd.uix.card import MDCard
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.button import MDRaisedButton
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
import pyrebase
import json
import os
from datetime import datetime
import time
from kivy import platform


config = {
    "apiKey": "AIzaSyAFdyRcRFrPj9_V3Nr0mafStyfoiR9A2Wk",
    "authDomain": "cetapp-776a7.firebaseapp.com",
    "databaseURL": "https://cetapp-776a7-default-rtdb.asia-southeast1.firebasedatabase.app",
    "storageBucket": "cetapp-776a7.firebasestorage.app"
}
try:
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    print("✅ Pyrebase4 initialized successfully.")
except Exception as e:
    print(f"❌ Pyrebase4 initialization failed in quiz.py: {e}")


def get_storage_path():
    try:
        if platform == 'android':
            from android.storage import primary_external_storage_path
            base_path = primary_external_storage_path()
            storage_dir = os.path.join(base_path, 'Documents', 'cetapp')
            return storage_dir
        else:
            storage_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'cetapp')
            return storage_dir
    except Exception as e:
        print(f"❌ Error getting storage path: {e}")
        return os.path.join(os.path.expanduser('~'), 'Documents', 'cetapp')

def initialize_json_storage():
    try:
        storage_dir = get_storage_path()
        file_path = os.path.join(storage_dir, 'user_performance.json')
        
        print(f"📁 Storage directory: {storage_dir}")
        
        # Create directory
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
            print(f"✅ Created directory: {storage_dir}")
        else:
            print(f"✅ Directory exists: {storage_dir}")
        
        # Initialize with empty structure if file doesn't exist
        if not os.path.exists(file_path):
            initial_data = {
                "practice": [],
                "daily_practice": []
            }
            with open(file_path, 'w') as f:
                json.dump(initial_data, f, indent=4)
            print(f"✅ JSON storage initialized at: {file_path}")
            return True
        else:
            print(f"✅ JSON storage already exists at: {file_path}")
            return True
            
    except Exception as e:
        print(f"❌ Error initializing JSON storage: {e}")
        return False

def save_to_json(data):
    try:
        storage_dir = get_storage_path()
        file_path = os.path.join(storage_dir, 'user_performance.json')
        
        print(f"💾 Saving data to: {file_path}")
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"✅ Data saved to JSON successfully")
        return True
    except Exception as e:
        print(f"❌ Error saving to JSON: {e}")
        return False

def load_from_json():
    """Load data from JSON file"""
    try:
        storage_dir = get_storage_path()
        file_path = os.path.join(storage_dir, 'user_performance.json')
        
        print(f"📖 Loading data from: {file_path}")
        
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
            print(f"✅ Data loaded from JSON successfully")
            return data
        else:
            print("❌ JSON file doesn't exist, creating new one...")
            if initialize_json_storage():
                return {"practice": [], "daily_practice": []}
            else:
                return {"practice": [], "daily_practice": []}
    except Exception as e:
        print(f"❌ Error loading from JSON: {e}")
        return {"practice": [], "daily_practice": []}

def store_practice_result(subject, chapter_name, total_questions, correct_questions, incorrect_questions, time_taken_minutes, quiz_type="practice"):
    """
    Store practice quiz results in JSON file
    
    Args:
        subject: Quiz subject (e.g., "Physics", "Math")
        chapter_name: Chapter name (e.g., "Algebra", "Mechanics")
        total_questions: Total number of questions
        correct_questions: Number of correct answers
        incorrect_questions: Number of incorrect answers
        time_taken_minutes: Time taken for quiz in minutes
        quiz_type: "practice" for test.py or "daily_practice" for daily.py
    """
    try:
        # Get current date and day
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_day = datetime.now().strftime("%A")
        
        # Create result entry
        result_entry = {
            "subject": subject,
            "chapter_name": chapter_name,
            "total_questions": total_questions,
            "correct_questions": correct_questions,
            "incorrect_questions": incorrect_questions,
            "time_taken": time_taken_minutes,
            "date": current_date,
            "day": current_day
        }
        
        print(f"📝 Storing {quiz_type} result:")
        print(f"   Subject: {subject}")
        print(f"   Chapter: {chapter_name}") 
        print(f"   Score: {correct_questions}/{total_questions}")
        print(f"   Time: {time_taken_minutes} min")
        
       
        data = load_from_json()
        
        
        if quiz_type == "practice":
            data["practice"].append(result_entry)
            print(f"✅ Added to practice: {len(data['practice'])} sessions")
        elif quiz_type == "daily_practice":
            data["daily_practice"].append(result_entry)
            print(f"✅ Added to daily_practice: {len(data['daily_practice'])} sessions")
        
        # Save updated data
        if save_to_json(data):
            print(f"✅ {quiz_type} result stored successfully")
            return True
        else:
            print(f"❌ Failed to store {quiz_type} result")
            return False
            
    except Exception as e:
        print(f"❌ Error storing {quiz_type} result: {e}")
        return False

def get_user_performance_data():
    try:
        data = load_from_json()
        if data:
            print(f"📊 Loaded data: {len(data['practice'])} practice, {len(data['daily_practice'])} daily sessions")
            return data
        else:
            return {"practice": [], "daily_practice": []}
    except Exception as e:
        print(f"❌ Error getting user performance data: {e}")
        return {"practice": [], "daily_practice": []}


class ClickableMDLabel(ButtonBehavior, MDLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

KV = """
<QuizScreen>:
    name:"quiz"
    question_label: question_label
    options_layout: options_layout
    hint_container: hint_container
    solution_label: solution_label
    main_card: main_card
    question_counter: question_counter
    canvas.before:
        Rectangle:
            source: "img/login.jpg"
            size: self.size
            pos: self.pos
    MDBoxLayout:
        orientation:"vertical"
        md_bg_color:0,0,1,0
        pos_hint:{"center_x": 0.5,"center_y": 0.5}
        Widget:
            size_hint_y: 0.1
            
        MDCard:
            id: main_card
            md_bg_color: 1, 1, 1, 1
            radius:[20]
            orientation:"vertical"
            padding:20
            size_hint:0.9, None
            height:dp(500)
            pos_hint:{"center_x": 0.5,"center_y": 0.5}
            ScrollView:
                do_scroll_x: False
                do_scroll_y: True
                BoxLayout:
                    orientation:"vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    MDBoxLayout:
                        orientation:"horizontal"
                        size_hint_y:None 
                        height:dp(44)
                        MDIconButton:
                            icon:'chevron-left'
                            on_release: app.root.current="test"
                        
                        MDLabel:
                            id: question_counter
                            text: "Question 4 of 10"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 0, 0, 0, 1
                            font_style: "Subtitle1"
                            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                            size_hint_y: None
                            height: self.texture_size[1]
                            padding: 5
                            underline: True
                            bold: True     
                            italic: True   
                    Widget:
                        size_hint_y:None 
                        height:dp(20)
                              
                    MDLabel:
                        id: question_label
                        text: "What is Newton's first law of motion commonly known as?"
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 0, 0, 0, 1
                        font_style: "H6"
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                        size_hint_y: None
                        height: self.texture_size[1]
                        padding: 10
                        
                    Widget:
                    
                    MDBoxLayout:
                        id: options_layout
                        orientation: "vertical"
                        spacing: "10dp"
                        size_hint_y: None
                        height: self.minimum_height
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                
                    MDLabel:
                        id: solution_label
                        text: ""
                        theme_text_color: "Custom"
                        text_color: 0, 0.5, 0.5, 1
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                        halign: "center"
                        size_hint_y: None
                        height: self.texture_size[1]
                        
                    Widget:
                        size_hint_y: None 
                        height: dp(15)
        
                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: "48dp"
                        spacing: "10dp"
                        
                        MDBoxLayout:
                            id: hint_container
                            orientation: "horizontal"
                            size_hint_x: 0.5
                            spacing: "5dp"
                            MDTextButton:
                                text: "Show hint"
                                on_release: root.toggle_hint()
                            MDIconButton:
                                icon: "chevron-down"
                                on_release: root.toggle_hint()
                        
                        MDBoxLayout:
                            orientation: "horizontal"
                            size_hint_x: 0.5
                            spacing: "15dp"
                            halign: "right"
                            pos_hint: {'right': 1}
                            MDRaisedButton:
                                text: "Back"
                                size_hint: None, None
                                size: "100dp", "48dp"
                                on_release: root.back_question()
                            MDRaisedButton:
                                text: "Next"
                                size_hint: None, None
                                size: "100dp", "48dp"
                                on_release: root.next_question()
               
        Widget:
            size_hint_y: 0.1

<ResultScreen>:
    name: "result"
    correct_label: correct_label
    incorrect_label: incorrect_label
    total_label: total_label
    canvas.before:
        Rectangle:
            source: "img/login.jpg"
            size: self.size
            pos: self.pos
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0, 0, 1, 0
        spacing: "20dp"
        padding: "20dp"
        pos_hint: {"center_x": 0.5, "center_y": 0.5}

        MDLabel:
            text: "Quiz Finished!"
            halign: "center"
            font_style: "H4"
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            pos_hint: {"center_x": 0.5}

        MDCard:
            md_bg_color: 1, 1, 1, 0.3
            radius: [20]
            orientation: "vertical"
            padding: "20dp"
            size_hint: 0.8, None
            height: "250dp"
            pos_hint: {"center_x": 0.5}

            MDLabel:
                text: "Your Results"
                halign: "center"
                font_style: "H6"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                bold: True

            MDLabel:
                id: total_label
                text: "Total Questions: 0"
                theme_text_color: "Custom"
                text_color: 0, 0, 1, 1
                font_style: "Subtitle1"
                halign: "center"
            
            MDLabel:
                id: correct_label
                text: "Correct Answers: 0"
                theme_text_color: "Custom"
                text_color: 0, 1, 0, 1
                font_style: "Subtitle1"
                halign: "center"
            
            MDLabel:
                id: incorrect_label
                text: "Incorrect Answers: 0"
                theme_text_color: "Custom"
                text_color: 1, 0, 0, 1
                font_style: "Subtitle1"
                halign: "center"
        
        Widget:
            size_hint_y: 0.1
            
        MDRaisedButton:
            text: "Restart Quiz"
            size_hint: 0.5, None
            height: "48dp"
            pos_hint: {"center_x": 0.5}
            on_release: app.root.get_screen("quiz").reset_quiz(); app.root.current = "quiz"
        
        MDRaisedButton:
            text: "Back to Test Page"
            size_hint: 0.5, None
            height: "48dp"
            pos_hint: {"center_x": 0.5}
            on_release: app.root.current="test"
            
        Widget:
            size_hint_y: 0.1
"""
Builder.load_string(KV)


class QuizScreen(Screen):
    question_label = ObjectProperty(None)
    options_layout = ObjectProperty(None)
    hint_container = ObjectProperty(None)
    solution_label = ObjectProperty(None)
    main_card = ObjectProperty(None)
    question_counter = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.quiz_data = []
        self.total_questions = 0
        self.current_question_index = 0
        self.hint_label = None
        self.answer_selected = False
        self.option_widgets = []  
        self.quiz_start_time = None
        self.current_subject = None
        self.current_chapter = None
        self.quiz_type = "practice"  

    def on_pre_enter(self):
        if hasattr(self, 'question_label') and self.question_label:
            self.question_label.text = "Select a subject and chapter to start quiz"

    def fetch_quiz_data(self, subject, chapter, quiz_type="practice"):
        if self.question_label:
            self.question_label.text = "Loading quiz..."
        if self.options_layout:
            self.options_layout.clear_widgets()
        if self.solution_label:
            self.solution_label.text = ""
        
        self.current_subject = subject
        self.current_chapter = chapter
        self.quiz_type = quiz_type
        
        Clock.schedule_once(lambda dt: self._fetch_data_from_firebase(subject, chapter), 0.1)

    def _fetch_data_from_firebase(self, subject, chapter):
        try:
            quiz_data = db.child("Main").child(subject).child(chapter).get().val()
            
            if not quiz_data:
                if self.question_label:
                    self.question_label.text = "No quiz data found!"
                return
            
            if isinstance(quiz_data, dict):
                self.quiz_data = list(quiz_data.values())
            else:
                self.quiz_data = quiz_data
            
            self.total_questions = len(self.quiz_data)
            self.reset_quiz()

        except Exception as e:
            if self.question_label:
                self.question_label.text = f"Error fetching data: {e}"
            print(f"Error fetching data: {e}")

    def reset_quiz(self):
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.current_question_index = 0
        self.answer_selected = False
        self.quiz_start_time = time.time()  
        self.display_question()

    def display_question(self):
        if hasattr(self, 'hint_label') and self.hint_label and self.hint_label in self.main_card.children:
            self.main_card.remove_widget(self.hint_label)
            self.hint_label = None
            
        
        if self.current_question_index >= len(self.quiz_data):
            self.show_results()
            return
            
        if self.current_question_index < len(self.quiz_data) and self.quiz_data:
            self.answer_selected = False
            q_data = self.quiz_data[self.current_question_index]
            
            # Update question counter
            if self.question_counter:
                self.question_counter.text = f"Question {self.current_question_index + 1} of {self.total_questions}"
            
            if self.question_label:
                self.question_label.text = q_data.get("question", "Question not available")
            
            if self.solution_label:
                self.solution_label.text = ""
            
            if self.options_layout:
                self.options_layout.clear_widgets()
                self.option_widgets = []

                options = q_data.get("options", [])
                for option in options:
                    # Create a centered container for each option
                    option_container = MDBoxLayout(
                        orientation="horizontal",
                        size_hint_y=None,
                        height="48dp",
                        padding="10dp",
                        spacing="10dp",
                        pos_hint={'center_x': 0.5}
                    )
                    
                    # Create checkbox
                    checkbox = MDCheckbox(
                        group=f"q{self.current_question_index}", 
                        size_hint_x=None, 
                        width="48dp",
                        valign="center",
                        halign="center",
                        pos_hint={'center_y': 0.5}
                    )
                    checkbox.bind(active=self.on_checkbox_active)
                    
                    # Create clickable label
                    label = ClickableMDLabel(
                        text=option,
                        theme_text_color="Custom",
                        text_color=(0, 0, 0, 1),
                        valign="center",
                        halign="left",
                        size_hint_x=1,
                        pos_hint={'center_y': 0.5}
                    )
                    # Bind label click to toggle checkbox
                    label.bind(on_release=lambda instance, cb=checkbox: self.on_label_click(cb))
                    
                    option_container.add_widget(checkbox)
                    option_container.add_widget(label)
                    self.options_layout.add_widget(option_container)
                    self.option_widgets.append((checkbox, label, option_container))

    def on_label_click(self, checkbox):
        if not self.answer_selected and not checkbox.active:
            checkbox.active = True

    def on_checkbox_active(self, checkbox, value):
        if value and not self.answer_selected: 
            self.check_answer(checkbox)

    def check_answer(self, checkbox):
        if self.answer_selected or self.current_question_index >= len(self.quiz_data):
            return

        self.answer_selected = True
        q_data = self.quiz_data[self.current_question_index]

        
        selected_option = ""
        for cb, label, container in self.option_widgets:
            if cb == checkbox:
                selected_option = label.text
                break

        correct_answer = q_data.get("answer", "")
        
        if self.solution_label:
            if selected_option == correct_answer:
                self.correct_answers += 1
                self.solution_label.text = "Correct! ✅"
                self.solution_label.text_color = (0, 1, 0, 1)
            else:
                self.incorrect_answers += 1
                self.solution_label.text = "Incorrect ❌"
                self.solution_label.text_color = (1, 0, 0, 1)

        # Highlight answers and disable all checkboxes
        for cb, label, container in self.option_widgets:
            cb.disabled = True  # Disable all checkboxes
            if label.text == correct_answer:
                label.text_color = (0, 0.6, 0, 1)  # Green for correct
            elif label.text == selected_option and selected_option != correct_answer:
                label.text_color = (1, 0, 0, 1)  # Red for incorrect selection

    def toggle_hint(self):
        if (self.current_question_index < len(self.quiz_data) and 
            hasattr(self, 'main_card') and self.main_card):
            
            q_data = self.quiz_data[self.current_question_index]
            hint_text = q_data.get("hint", "No hint available.")
            
            if not hasattr(self, 'hint_label') or not self.hint_label:
                self.hint_label = MDLabel(
                    text=hint_text,
                    halign="center",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height="40dp",
                    text_color=(0, 0, 0, 1)
                )
                # Find the index to insert the hint (before the button layout)
                main_layout = self.main_card.children[0].children[0]  # ScrollView -> BoxLayout
                hint_index = len(main_layout.children) - 1  # Insert before buttons
                main_layout.add_widget(self.hint_label, index=hint_index)
            else:
                if self.hint_label in self.main_card.children[0].children[0].children:
                    self.main_card.children[0].children[0].remove_widget(self.hint_label)
                self.hint_label = None

    def next_question(self):
        # Clear hint
        if hasattr(self, 'hint_label') and self.hint_label:
            if self.hint_label in self.main_card.children[0].children[0].children:
                self.main_card.children[0].children[0].remove_widget(self.hint_label)
            self.hint_label = None

        # Check if we've reached the last question
        if self.current_question_index >= len(self.quiz_data) - 1:
            # This is the last question, show results
            self.show_results()
        else:
            self.current_question_index += 1
            self.display_question()

    def back_question(self):
        # Clear hint
        if hasattr(self, 'hint_label') and self.hint_label:
            if self.hint_label in self.main_card.children[0].children[0].children:
                self.main_card.children[0].children[0].remove_widget(self.hint_label)
            self.hint_label = None

        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.display_question()

    def show_results(self):
        try:
            # Calculate time taken in minutes
            time_taken_minutes = 0
            if self.quiz_start_time:
                time_taken_seconds = time.time() - self.quiz_start_time
                time_taken_minutes = round(time_taken_seconds / 60, 2)  # Convert to minutes
            
            print(f"📊 Quiz completed! Correct: {self.correct_answers}, Incorrect: {self.incorrect_answers}, Total: {self.total_questions}, Time: {time_taken_minutes} min")
            
            # Store results in JSON
            if self.current_subject and self.current_chapter:
                success = store_practice_result(
                    subject=self.current_subject,
                    chapter_name=self.current_chapter,
                    total_questions=self.total_questions,
                    correct_questions=self.correct_answers,
                    incorrect_questions=self.incorrect_answers,
                    time_taken_minutes=time_taken_minutes,
                    quiz_type=self.quiz_type
                )
                if success:
                    print("✅ Results stored in JSON successfully!")
                else:
                    print("❌ Failed to store results in JSON")
            
            # Update the result screen
            result_screen = self.manager.get_screen("result")
            result_screen.update_results(self.total_questions, self.correct_answers, self.incorrect_answers, time_taken_minutes)
            
            # Navigate to result screen
            self.manager.current = "result"
            
        except Exception as e:
            print(f"Error showing results: {e}")
            # Fallback: show alert or message
            if self.question_label:
                self.question_label.text = f"Quiz Completed! Correct: {self.correct_answers}/{self.total_questions}"


class ResultScreen(Screen):
    correct_label = ObjectProperty(None)
    incorrect_label = ObjectProperty(None)
    total_label = ObjectProperty(None)
    
    def update_results(self, total_q, correct_q, incorrect_q, time_taken=0):
        if self.total_label:
            self.total_label.text = f"Total Questions: {total_q}"
        if self.correct_label:
            self.correct_label.text = f"Correct Answers: {correct_q}"
        if self.incorrect_label:
            self.incorrect_label.text = f"Incorrect Answers: {incorrect_q}"

# Initialize JSON storage when module is imported
print("🚀 Initializing quiz module...")
initialize_json_storage()