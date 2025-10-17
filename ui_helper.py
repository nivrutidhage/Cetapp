import json
import webbrowser
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

# ---------------- Clickable Card ----------------
class ClickableCard(MDCard):
    """
    MDCard that is clickable and opens a link.
    Uses on_touch_up instead of ButtonBehavior to avoid MRO issues.
    """
    def __init__(self, title, description, link, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(10)
        self.size_hint_y = None
        self.height = dp(120)
        self.elevation = 6
        self.radius = [10]

        self.link = link

        # Title label
        self.add_widget(
            MDLabel(
                text=title,
                font_style="H6",
                size_hint_y=None,
                height=dp(30),
                halign="center"
            )
        )

        # Description label
        self.add_widget(
            MDLabel(
                text=description,
                font_style="Body1",
                size_hint_y=None,
                height=dp(60),
                halign="center"
            )
        )

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if self.link:
                webbrowser.open(self.link)
            return True
        return super().on_touch_up(touch)


# ---------------- Card Manager ----------------
class CardManager(BoxLayout):
    """
    Loads clickable cards from a JSON file and displays them in a scrollable layout.
    """
    def __init__(self, json_file, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        # ScrollView to allow scrolling for many cards
        scroll = ScrollView()
        self.card_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(15),
            padding=dp(15),
            size_hint_y=None
        )
        self.card_layout.bind(minimum_height=self.card_layout.setter("height"))
        scroll.add_widget(self.card_layout)
        self.add_widget(scroll)

        # Load cards from JSON
        self.load_cards(json_file)

    def load_cards(self, json_file):
        """
        Load JSON file and create ClickableCard for each item.
        JSON should be a list of dicts with keys: title, description, link
        """
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            data = []

        for item in data:
            card = ClickableCard(
                title=item.get("title", "No Title"),
                description=item.get("description", ""),
                link=item.get("link", "")
            )
            self.card_layout.add_widget(card)