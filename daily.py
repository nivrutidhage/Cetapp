from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.app import App
import time # <-- Added time import for quiz start time

# KivyMD Imports
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.dialog import MDDialog
import pyrebase
import webbrowser

# --- 1. FIREBASE CONFIGURATION ---
config = {
    
}

try:
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    print("✅ Pyrebase4 initialized successfully.")
except Exception as e:
    print(f"❌ Pyrebase4 initialization failed: {e}")


# --- 2. KIVY LANGUAGE (KV) DESIGN ---
kv = '''
<Daily>:
    name: "daily"
    chapter_name_label: chapter_name_label
    material_container: material_container
    flashcard_container: flashcard_container
    quiz_button: quiz_button
    
    canvas.before:
        Rectangle:
            source: "img/daily.jpg"
            size: self.size
            pos: self.pos
    
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 120/255, 120/255, 120/255, 0

        MDTopAppBar:
            id: header_bar
            title: "Daily Practice"
            md_bg_color: 61/255, 61/255, 61/255, 1
            left_action_items: [["chevron-left", lambda x: root.go_back()]]

        MDScrollView:
            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(15)
                padding: dp(15)
                size_hint_y: None
                md_bg_color :120/255, 120/255, 120/255, 0
                height: self.minimum_height
                
                # Header: Chapter Name
                MDLabel:
                    id: chapter_name_label
                    text: "Loading Today's Focus..."
                    font_style: "H4"
                    bold: True
                    halign: "left"
                    adaptive_height: True
                    theme_text_color: "Custom"
                    text_color: 0, 0, 0, 1

                # --- PHASE 1: LEARNING & REVIEW ---
                MDCard:
                    orientation: "vertical"
                    padding: dp(15)
                    spacing: dp(10)
                    elevation: 0
                    radius: [15]
                    md_bg_color: 120/255, 120/255, 120/255, 0.3
                    size_hint_y: None
                    height: self.minimum_height

                    MDLabel:
                        text: "[b]Phase 1: Learn & Review[/b]"
                        markup: True
                        font_style: "H6"
                        theme_text_color: "Primary"
                        adaptive_height: True

                    MDBoxLayout:
                        id: material_container
                        orientation: "vertical"
                        spacing: dp(8)
                        adaptive_height: True

                # --- PHASE 2: ASSESSMENT (QUIZ) ---
                MDCard:
                    orientation: "vertical"
                    padding: dp(15)
                    spacing: dp(10)
                    elevation: 0
                    radius: [15]
                    md_bg_color: 120/255, 120/255, 120/255, 0.3
                    size_hint_y: None
                    height: self.minimum_height
                    
                    MDLabel:
                        text: "[b]Phase 2: Assessment[/b]"
                        markup: True
                        font_style: "H6"
                        theme_text_color: "Primary"
                        adaptive_height: True

                    MDRaisedButton:
                        id: quiz_button
                        text: "Start Daily Quiz (20 min)"
                        size_hint_x: 1
                        md_bg_color: 1,0.1,0,1
                        on_release: root.start_quiz()
                    
                    MDLabel:
                        text: "Focus: Test your Active Recall on today's chapter."
                        font_style: "Caption"
                        halign: "center"
                        adaptive_height: True

                # --- PHASE 3: ACTIVE RECALL (FLASHCARDS & REVIEW) ---
                MDCard:
                    orientation: "vertical"
                    padding: dp(15)
                    spacing: dp(10)
                    elevation: 0
                    radius: [15]
                    md_bg_color: 120/255, 120/255, 120/255, 0.3
                    size_hint_y: None
                    height: self.minimum_height

                    MDLabel:
                        text: "[b]Phase 3: Deep Recall & Memory[/b]"
                        markup: True
                        font_style: "H6"
                        theme_text_color: "Primary"
                        adaptive_height: True
                    
                    MDLabel:
                        text: "Key Term Resources:"
                        font_style: "Body1"
                        adaptive_height: True

                    MDBoxLayout:
                        id: flashcard_container
                        orientation: "vertical"
                        spacing: dp(5)
                        adaptive_height: True
                        
                    MDRaisedButton:
                        text: "Review Yesterday's Topics (Spaced Repetition)"
                        size_hint_x: 1
                        md_bg_color: get_color_from_hex('#FF8C00')
                        on_release: root.review_yesterday()
'''
Builder.load_string(kv)


# --- 3. HELPER WIDGETS ---

class MaterialButton(MDCard):
    """Custom widget for a link to study material."""
    link = StringProperty()
    
    def __init__(self, icon_name, title, link, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(48)
        self.padding = [dp(10), 0, dp(10), 0]
        self.spacing = dp(10)
        self.md_bg_color = get_color_from_hex('#E0E0E0')
        self.radius = [dp(10)]
        self.link = link
        self.elevation = 2
        self.bind(on_release=lambda x: self.open_link())
        
        # Icon
        self.add_widget(MDIconButton(
            icon=icon_name,
            icon_color=get_color_from_hex('#008088'),
            size_hint_x=None,
            width=dp(40)
        ))
        
        # Label
        self.add_widget(MDLabel(
            text=title,
            font_style="Body1",
            size_hint_x=1,
            theme_text_color="Primary"
        ))
        
        # Open Link Icon
        self.add_widget(MDIconButton(
            icon='open-in-new',
            disabled=True,
            icon_color=get_color_from_hex('#008088')
        ))
    
    def open_link(self):
        """Open the link in a web browser"""
        link_to_open = self.link.strip()
        if link_to_open:
            try:
                if not link_to_open.lower().startswith(('http://', 'https://')):
                    print(f"Link is not a valid URL (missing http/https): {link_to_open}")
                    return
                    
                webbrowser.open(link_to_open)
                print(f"Opened link successfully: {link_to_open}")
            except Exception as e:
                print(f"Error opening link: {e}")
        else:
            print("No link defined for this material.")


# --- 4. DAILY SCREEN CLASS ---

class Daily(Screen):
    chapter_name_label = ObjectProperty(None)
    material_container = ObjectProperty(None)
    flashcard_container = ObjectProperty(None)
    quiz_button = ObjectProperty(None)
    
    # Store fetched data
    daily_data = None 

    def go_back(self):
        """Navigate back to home screen"""
        print("Go back function triggered.")
        if self.manager.has_screen("test"):
            self.manager.current = "test"
        else:
            self.dialog = MDDialog(
                title="Navigation",
                text="Would navigate back to the 'test' screen here.",
                buttons=[
                    MDRaisedButton(text="OK", on_release=lambda x: self.dialog.dismiss())
                ]
            )
            self.dialog.open()

    def on_enter(self, *args):
        """Called when screen becomes active"""
        self.chapter_name_label.text = "Loading Today's Focus..."
        self.material_container.clear_widgets()
        self.flashcard_container.clear_widgets()
        self.quiz_button.text = "Start Daily Quiz (Loading...)"
        self.quiz_button.disabled = True
        Clock.schedule_once(lambda dt: self.fetch_daily_data(), 0.1)

    def fetch_daily_data(self):
        """Fetch daily practice data from Firebase"""
        try:
            # CORRECT PATH: Daily_practice is directly under Main
            self.daily_data = db.child("Main").child("Daily_practice").get().val()
            
            print("🔍 Fetching data from: Main/Daily_practice")
            print(f"📦 Data received: {self.daily_data}")
            
            if not self.daily_data:
                self.chapter_name_label.text = "No Daily Practice content available today."
                self.add_load_error_widgets("No content available in Main/Daily_practice.")
                return
            
            self.update_ui_with_data()
            
        except Exception as e:
            self.chapter_name_label.text = "Error connecting to database."
            self.add_load_error_widgets(f"Failed to load data: {str(e)}")
            print(f"❌ Error fetching daily data: {e}")

    def add_load_error_widgets(self, message):
        """Helper to display error and retry button."""
        self.material_container.clear_widgets()
        error_label = MDLabel(
            text=message,
            theme_text_color="Error",
            halign="center",
            adaptive_height=True
        )
        retry_button = MDRaisedButton(
            text="Retry Loading",
            on_release=lambda x: self.fetch_daily_data(),
            size_hint_x=1,
            md_bg_color=get_color_from_hex('#FF5733')
        )
        self.material_container.add_widget(error_label)
        self.material_container.add_widget(retry_button)

    def update_ui_with_data(self):
        """Update the UI with fetched data"""
        if not self.daily_data:
            return
            
        print("🎨 Updating UI with fetched data...")
        
        # 1. Update Header
        chapter = self.daily_data.get('chapter_name', 'Chapter Title Missing')
        subject = self.daily_data.get('subject', 'N/A')
        
        self.chapter_name_label.text = f"{chapter.title()} ({subject})"
        
        # 2. Populate Phase 1: Review Materials
        materials = {
            'Video Lecture': ('youtube', self.daily_data.get('video_link')),
            'Notes': ('file-document-outline', self.daily_data.get('notes_link')),
            'Formula Sheet': ('sigma', self.daily_data.get('formula_sheet_link')),
            'Mind Map': ('palm-tree', self.daily_data.get('mindmap_link')),
            'Solved Questions': ('book-open-outline', self.daily_data.get('solved_questions_link')),
        }
        
        self.material_container.clear_widgets()
        materials_added = False

        for title, (icon, link) in materials.items():
            if link and isinstance(link, str) and link.strip():
                print(f"➕ Adding material: {title} -> {link}")
                self.material_container.add_widget(
                    MaterialButton(icon, title, link)
                )
                materials_added = True
        
        if not materials_added:
            self.material_container.add_widget(
                MDLabel(
                    text="No study materials available for this chapter.",
                    font_style="Caption",
                    theme_text_color="Secondary",
                    halign="center"
                )
            )
            
        # 3. Populate Phase 3: Flashcards
        self.flashcard_container.clear_widgets()
        
        # Check for flashcards array in the data
        flashcards = self.daily_data.get('flashcards', [])
        
        if flashcards and isinstance(flashcards, list):
            print(f"📚 Found {len(flashcards)} flashcards")
            
            # Add a label for flashcards section
            self.flashcard_container.add_widget(MDLabel(
                text="Flashcards for this chapter:",
                font_style="Subtitle1",
                adaptive_height=True
            ))
            
            # Display each flashcard
            for i, flashcard in enumerate(flashcards):
                if isinstance(flashcard, dict):
                    term = flashcard.get('term', f'Term {i+1}')
                    definition = flashcard.get('definition', 'Definition not available')
                    
                    # Create a card for each flashcard
                    flashcard_card = MDCard(
                        orientation="vertical",
                        padding=dp(10),
                        spacing=dp(5),
                        elevation=2,
                        size_hint_y=None,
                        height=dp(100),
                        md_bg_color=get_color_from_hex('#F8F9FA')
                    )
                    
                    flashcard_card.add_widget(MDLabel(
                        text=f"[b]{term}[/b]",
                        markup=True,
                        font_style="Subtitle1",
                        adaptive_height=True
                    ))
                    
                    flashcard_card.add_widget(MDLabel(
                        text=definition,
                        font_style="Body2",
                        adaptive_height=True
                    ))
                    
                    self.flashcard_container.add_widget(flashcard_card)
        else:
            # Fallback to flashcard link if no flashcards array
            flashcard_link = self.daily_data.get('flashcards_link')
            if flashcard_link and isinstance(flashcard_link, str) and flashcard_link.strip():
                print(f"🔗 Using flashcard link: {flashcard_link}")
                self.flashcard_container.add_widget(
                    MaterialButton(
                        'cards-playing-outline', 
                        'Open Flashcard Deck (External)', 
                        flashcard_link
                    )
                )
            else:
                self.flashcard_container.add_widget(
                    MDLabel(
                        text="No flashcards provided for this chapter.", 
                        font_style="Caption",
                        theme_text_color="Secondary",
                        halign="center"
                    )
                )
            
        # 4. Update Quiz Button Text (Phase 2)
        quiz_data = self.daily_data.get('quiz', [])
        print(f"📝 Quiz data: {quiz_data}")

        if isinstance(quiz_data, list) and len(quiz_data) > 0:
            # Handle quiz as array (from your database structure)
            total_questions = len(quiz_data)
            self.quiz_button.text = f"Start Daily Quiz ({total_questions} Questions)"
            self.quiz_button.disabled = False
            print(f"✅ Quiz enabled with {total_questions} questions")
        else:
            self.quiz_button.text = "Quiz Not Configured"
            self.quiz_button.disabled = True
            print("❌ Quiz disabled - no quiz data")

    def start_quiz(self):
        """Logic to switch to the quiz screen and pass the quiz data."""
        if not self.daily_data:
            return
            
        quiz_data = self.daily_data.get('quiz', [])
        subject = self.daily_data.get('subject', 'Physics')
        chapter = self.daily_data.get('chapter_name', 'Wave Optics')
    
        if isinstance(quiz_data, list) and len(quiz_data) > 0:
            
            quiz_screen = self.manager.get_screen("quiz")
            
            # --- START OF FIX: PASS DATA VIA APP PROPERTY ---
            # This is the workaround since we cannot edit quiz.py to fetch data correctly.
            # 1. Store the already fetched daily quiz data in a temporary app property.
            app = MDApp.get_running_app()
            app.daily_practice_quiz_data = {
                "questions": quiz_data,
                "subject": subject,
                "chapter": chapter
            }

            # 2. Call quiz.py's fetch_quiz_data. This call will FAIL its internal 
            # Firebase fetch (due to the wrong path), but it correctly sets the 
            # `quiz_type` to "daily_practice" and triggers the screen.
            quiz_screen.fetch_quiz_data(subject, "Daily Practice", "daily_practice")
            
            # 3. Navigate to quiz screen
            self.manager.current = "quiz"
            
            # 4. Schedule the function that reads the data from the app property 
            # to run right after the screen transition completes.
            Clock.schedule_once(lambda dt: self._load_daily_quiz_after_navigation(), 0.1)
            # --- END OF FIX ---

            print(f"🎯 Starting daily quiz with {len(quiz_data)} questions")
        else:
            self.dialog = MDDialog(
                title="No Quiz Available",
                text="No quiz questions are available for today's practice.",
                buttons=[
                    MDRaisedButton(text="OK", on_release=lambda x: self.dialog.dismiss())
                ]
            )
            self.dialog.open()
            print("❌ No quiz data available.")

    def _load_daily_quiz_after_navigation(self):
        """
        Loads the daily quiz data from the stored app property into the quiz screen.
        This function runs after the navigation to bypass the failed Firebase fetch in quiz.py.
        """
        try:
            quiz_screen = self.manager.get_screen("quiz")
            app = MDApp.get_running_app()
            
            # Check if we have daily practice data stored
            if hasattr(app, 'daily_practice_quiz_data'):
                # Manually set the quiz data and state variables in the quiz screen
                quiz_screen.quiz_data = app.daily_practice_quiz_data["questions"]
                quiz_screen.total_questions = len(quiz_screen.quiz_data)
                quiz_screen.current_question_index = 0
                quiz_screen.correct_answers = 0
                quiz_screen.incorrect_answers = 0
                quiz_screen.answer_selected = False
                
                # Update the metadata needed for storing results
                quiz_screen.current_subject = app.daily_practice_quiz_data["subject"]
                quiz_screen.current_chapter = app.daily_practice_quiz_data["chapter"]
                quiz_screen.quiz_type = "daily_practice" 
                
                # Display the first question and START THE TIMER
                quiz_screen.quiz_start_time = time.time() 
                quiz_screen.display_question()
                
                print(f"✅ Daily quiz loaded successfully with {quiz_screen.total_questions} questions")
                
                # Clear the stored data
                del app.daily_practice_quiz_data
        except Exception as e:
            print(f"❌ Error loading daily quiz: {e}")

    def review_yesterday(self):
        """Logic for Spaced Repetition"""
        self.dialog = MDDialog(
            title="Spaced Repetition",
            text="Feature not yet implemented: This would fetch a historical chapter to reinforce learning.",
            buttons=[
                MDRaisedButton(text="OK", on_release=lambda x: self.dialog.dismiss())
            ]
        )
        self.dialog.open()


# --- 5. TEST APP TO RUN THE SCREEN ---
class TestApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        
        # Create a simple screen manager for testing
        sm = ScreenManager()
        sm.add_widget(Daily(name="daily"))
        
        # Add quiz screen for testing
        # NOTE: Assumes quiz.py and its classes (QuizScreen, ResultScreen) 
        # are available for import in the running environment.
        try:
            from quiz import QuizScreen, ResultScreen
            sm.add_widget(QuizScreen(name="quiz"))
            sm.add_widget(ResultScreen(name="result"))
        except ImportError:
            print("WARNING: Could not import QuizScreen/ResultScreen from quiz.py. Quiz functionality will not work.")
            
        # Add a test screen for navigation
        from kivymd.uix.button import MDRaisedButton
        test_screen = Screen(name="test")
        test_layout = MDBoxLayout(orientation="vertical")
        test_layout.add_widget(MDLabel(
            text="Test Screen - Click button to go to Daily Practice",
            halign="center"
        ))
        test_button = MDRaisedButton(
            text="Go to Daily Practice",
            on_release=lambda x: setattr(sm, 'current', 'daily'),
            size_hint=(0.5, None),
            pos_hint={"center_x": 0.5}
        )
        test_layout.add_widget(test_button)
        test_screen.add_widget(test_layout)
        sm.add_widget(test_screen)
        
        return sm

if __name__ == '__main__':
    TestApp().run()
