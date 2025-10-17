import json
import webbrowser
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen

kv = '''
<MindMap>:
    name:"mindm"
    MDBoxLayout:
        orientation:"vertical"
        md_bg_color:120/255, 120/255, 120/255, 1
        MDTopAppBar:
            title:"Mind Maps"
            md_bg_color:61/255,61/255,61/255, 1 
            left_action_items: [["chevron-left", lambda x: setattr(app.root, "current", "home") ]]
            
        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                md_bg_color:120/255, 120/255, 120/255, 1
                padding: dp(15)
                size_hint_y: None
                height: self.minimum_height
                
                MDGridLayout:
                    cols: 1
                    spacing: dp(15)
                    adaptive_height: True
                    id: list_books
'''

Builder.load_string(kv)

class MindMap(MDScreen):
    def on_kv_post(self, base_widget):
        # Load JSON file
        with open("mindmap.json", "r") as f:
            books = json.load(f)

        # Add MDCard for each book
        for book in books:
            card = MDCard(
                size_hint_y=None,
                height=dp(200),
                padding=dp(10),
                md_bg_color=(61/255,61/255,61/255,1),             
                orientation=("vertical"))
            
            card.bind(on_release=lambda x , link=book["link"]:webbrowser.open(link))
            
            # Add book name label
            label = MDLabel(
                text=book["name"],
                halign="center",
                valign="middle"
            )
            card.add_widget(label)

            # Bind click to open link
            card.bind(on_release=lambda x, link=book["link"]: webbrowser.open(link))
            
            # Add card to grid
            self.ids.list_books.add_widget(card)