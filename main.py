from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

# your custom screens
from home import HomePage
from book import BookPage
from crash_course import CrashCourse
from mindmap import MindMap
from handbook import HandBook
from pyqs import PYQs
from reference import ReferenceBook
from test import TestScreen
from analysis import AnalysisScreen
from login import Login
from quiz import QuizScreen,ResultScreen
from daily import Daily
# RGB values scaled to 0-1
Window.clearcolor = 120/255, 120/255, 120/255, 1


class CetTest(MDApp):
    dialog = None   # 👈 define dialog at class level

    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"


        sm = ScreenManager()
        self.homepage = HomePage(name="home")
        self.bookpage = BookPage(name="book")
        self.cc = CrashCourse(name="CC")
        self.mind = MindMap(name="mindm")
        self.hbook = HandBook(name="handbook")
        self.pyqs = PYQs(name="pyqs")
        self.reference = ReferenceBook(name="reference")
        self.test=TestScreen(name="test")
        # Ensure the imported class is named AnalysisScreen if it's not aliased
        self.analysis = AnalysisScreen(name="analysis")

        self.login=Login(name="login")
        self.quiz=QuizScreen(name="quiz")
        self.daily = Daily(name="daily")


        #sm.add_widget(self.login)
        sm.add_widget(self.homepage)
        sm.add_widget(self.bookpage)
        sm.add_widget(self.cc)
        sm.add_widget(self.mind)
        sm.add_widget(self.hbook)
        sm.add_widget(self.pyqs)
        sm.add_widget(self.reference)
        sm.add_widget(self.test)
        sm.add_widget(self.analysis)
        sm.add_widget(self.quiz)
        # FIX: Removed duplicate sm.add_widget(QuizScreen(name="quiz"))
        sm.add_widget(ResultScreen(name="result"))
        sm.add_widget(self.daily )

        return sm

    def show_contact_dialog(self,title,text):
        if not self.dialog:
            self.dialog = MDDialog(
                title=title,
                text=text,

                md_bg_color=(120/255, 120/255, 120/255, 1),
                buttons=[
                    MDFlatButton(
                        text="CLOSE",
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                ],
            )
        self.dialog.open()
        
    def check_auto_login(self):
        """Check if user should be automatically logged in"""
        store = JsonStore('auth_data.json')
        try:
            if store.exists('user'):
                # You could add additional token validation here if needed
                return True
            return False
        except:
            return False


CetTest().run()
