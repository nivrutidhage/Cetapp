# test.py (Revised for Chapter Selection - Filtered Subjects)

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import ObjectProperty
from kivymd.uix.card import MDCard
from kivy.clock import Clock
import pyrebase
from kivy.metrics import dp

# Your Firebase configuration details
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
    print(f"❌ Pyrebase4 initialization failed: {e}")

kv = '''
<TestScreen>:
    name: "test"
    main_layout: main_layout

    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 120/255, 120/255, 120/255, 1
        
        MDTopAppBar:
            title: "Quiz test"
            md_bg_color: 61/255, 61/255, 61/255, 1 
            left_action_items: [["chevron-left", lambda x: setattr(app.root, "current", "home") ]]

        ScrollView:
            MDBoxLayout:
                id: main_layout
                orientation: "vertical"
                padding: "20dp"
                spacing: "20dp"
                size_hint_y: None
                height: self.minimum_height
                
'''
Builder.load_string(kv)

class TestScreen(Screen):
    main_layout = ObjectProperty(None)

    def on_enter(self, *args):
        # Clear previous widgets to avoid duplicates
        self.main_layout.clear_widgets()
        # Display loading message
        self.main_layout.add_widget(MDLabel(text="Loading data...", halign="center"))
        # Fetch data in a separate thread to avoid UI freeze
        Clock.schedule_once(lambda dt: self.fetch_and_display_data(), 0.1)

    def fetch_and_display_data(self):
        try:
            # Define the allowed subjects
            allowed_subjects = ["chemistry", "physics", "maths", "biology"]
            
            # Fetch the entire 'Main' node from the database
            data = db.child("Main").get().val()
            
            # Clear loading message
            self.main_layout.clear_widgets()

            if not data:
                self.main_layout.add_widget(MDLabel(text="No subjects found.", halign="center"))
                return
            
            # Iterate through subjects and chapters to create the UI
            for subject, chapters in data.items():
                # Only process allowed subjects
                if subject.lower() in allowed_subjects:
                    # Add a subject label
                    self.main_layout.add_widget(MDLabel(
                        text=f"[b]{subject.capitalize()}[/b]",
                        markup=True,
                        font_style="H5",
                        halign="left",
                        size_hint_y=None,
                        height="40dp",
                    ))

                    # Add buttons for each chapter
                    if chapters:
                        for chapter in chapters:
                            # Create a button for each chapter
                            chapter_button = MDCard(
                                md_bg_color=(143/255,143/255,143/255,1),
                                radius=[15],
                                size_hint=(1,None),
                                height=dp(33),
                                on_release=lambda btn, s=subject, c=chapter: self.start_quiz(s, c) 
                            )
                            label=MDLabel(
                                text=f"Chapter {chapter}",
                                size_hint_x=0.8,
                                halign="center",
                                bold=True,
                                pos_hint={'center_x': 0.5},
                            )
                            chapter_button.add_widget(label)
                            self.main_layout.add_widget(chapter_button)

        except Exception as e:
            self.main_layout.clear_widgets()
            self.main_layout.add_widget(MDLabel(text=f"❌ Error fetching data: {e}", halign="center"))
            print(f"Error fetching data in test.py: {e}")

    def start_quiz(self, subject, chapter):
        # Get the quiz screen and pass the selected subject and chapter
        quiz_screen = self.manager.get_screen("quiz")
        
        # UPDATED: Added "practice" as quiz_type parameter
        quiz_screen.fetch_quiz_data(subject, chapter, "practice")
        
        self.manager.current = "quiz"