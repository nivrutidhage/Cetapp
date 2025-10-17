from kivy.uix.screenmanager import Screen 
from kivy.lang import Builder 
import pyrebase
from kivy.app import App
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock

kv='''
<Login>:
    name: "login"

    canvas.before:
        Rectangle:
            source: "img/login.jpg"
            size: self.size
            pos: self.pos
            
    MDBoxLayout:
        orientation:"vertical"
        md_bg_color:0,0,0,0
        
        MDLabel:
            text:"Login"
            halign:"center"
            bold:True
            italic:True
            font_size:dp(55)
            theme_text_color:"Custom"
            text_color:1,1,1,1
            
        MDCard:
            radius:[20]
            orientation:"vertical"
            md_bg_color: 120/255, 120/255, 120/255, 0.2
            size_hint:None, None 
            height:dp(400)
            width:dp(700)
            padding:20
            spacing:30
            pos_hint:{"center_x": 0.5,"center_y": 0.5}
            
            MDBoxLayout:
                orientation:"vertical"
                size_hint_y:None 
                height:dp(100)
                MDLabel:
                    text:"Enter Email:"
                    font_size:dp(20)
                    theme_text_color:"Custom"
                    text_color:1,1,1,1
                    
                MDTextField:
                    id: username
                    mode: "rectangle"
                    hint_text: "Enter your email"
                    size_hint_x: 0.8
                    pos_hint:{"center_x": 0.5,"center_y": 0.5}
                    line_color_normal: 0.2, 0.6, 0.9, 1
                    line_color_focus: 1, 0, 0, 1
                    text_color_normal: 1, 1, 1, 1
                    hint_text_color_normal: 0.7, 0.7, 0.7, 1
                    radius: [12,]
                
            MDBoxLayout:
                orientation:"vertical" 
                size_hint_y:None 
                height:dp(100)
                MDLabel:
                    text:"Enter Password:"
                    font_size:dp(20)
                    theme_text_color:"Custom"
                    text_color:1,1,1,1
                    
                MDTextField:
                    id: password
                    mode: "rectangle"
                    hint_text: "Enter your password"
                    password: True
                    size_hint_x: 0.8
                    pos_hint:{"center_x": 0.5,"center_y": 0.5}
                    line_color_normal: 0.2, 0.6, 0.9, 1
                    line_color_focus: 1, 0, 0, 1
                    text_color_normal: 1, 1, 1, 1
                    hint_text_color_normal: 0.7, 0.7, 0.7, 1
                    radius: [12,]
            
            MDBoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: dp(50)
                spacing: dp(10)
                padding: [dp(20), 0, 0, 0]
                
                MDCheckbox:
                    id: remember_me
                    size_hint: None, None
                    size: dp(30), dp(30)
                    active: True
                    
                MDLabel:
                    text: "Remember Me"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    halign: "left"
                    valign: "center"
                
            MDRaisedButton:
                text: "Login"
                md_bg_color: 0, 0, 1, 1
                text_color: 1, 1, 1, 1
                halign:"center"
                pos_hint:{"center_x": 0.5,"center_y": 0.5}
                on_release:
                    root.login()
                    
        Widget:
'''                                
Builder.load_string(kv)                               

class Login(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # JsonStore automatically creates file in app's local storage
        self.store = JsonStore('auth_data.json')
        self.firebase_config = {
            'apiKey': "AIzaSyAFdyRcRFrPj9_V3Nr0mafStyfoiR9A2Wk",
            'authDomain': "cetapp-776a7.firebaseapp.com",
            'projectId': "cetapp-776a7",
            'storageBucket': "cetapp-776a7.firebasestorage.app",
            'messagingSenderId': "246813247708",
            'appId': "1:246813247708:web:19fb9dac0aeb344c0f8c19",
            'measurementId': "G-Q38LP6VWMQ",
            'databaseURL': "https://trialauth-7eeal.firebaseio.com"       
        }
        self.firebase = pyrebase.initialize_app(self.firebase_config)
        self.auth = self.firebase.auth()
        self.auto_login_checked = False
        
    def on_enter(self):
        if not self.auto_login_checked:
            Clock.schedule_once(self.check_auto_login, 0.1)
    
    def check_auto_login(self, dt):
        self.auto_login_checked = True
        if self.check_existing_login():
            print("Auto-login successful, redirecting to home...")
            app = App.get_running_app()
            if hasattr(app, 'root') and app.root:
                app.root.current = "home"
        else:
            print("No existing login found, showing login screen")
    
    def check_existing_login(self):
        try:
            if self.store.exists('user'):
                user_data = self.store.get('user')
                refresh_token = user_data.get('refreshToken')
                
                if refresh_token:
                    # Try to refresh the token to verify it's still valid
                    try:
                        user = self.auth.refresh(refresh_token)
                        # Update stored tokens with fresh ones
                        self.store.put('user', 
                                     idToken=user['idToken'],
                                     refreshToken=user['refreshToken'],
                                     email=user_data.get('email', ''))
                        return True
                    except Exception as e:
                        print(f"Token refresh failed: {e}")
                        # Clear invalid data
                        self.clear_stored_data()
                        return False
            return False
        except Exception as e:
            print(f"Error checking existing login: {e}")
            return False
    
    def clear_stored_data(self):
        """Clear any stored authentication data"""
        try:
            if self.store.exists('user'):
                self.store.delete('user')
        except:
            pass
    
    def login(self):
        """Handle user login"""
        email = self.ids.username.text.strip()
        password = self.ids.password.text
        remember_me = self.ids.remember_me.active
        
        if not email or not password:
            App.get_running_app().show_contact_dialog("Error", "Please enter both email and password")
            return
        
        try:
            # Sign in with email and password
            user = self.auth.sign_in_with_email_and_password(email, password)
            
            # Store user data if "Remember Me" is checked
            if remember_me:
                self.store.put('user',
                             idToken=user['idToken'],
                             refreshToken=user['refreshToken'],
                             email=email)
                print("Login data stored for auto-login")
            else:
                # Clear any previously stored data if "Remember Me" is unchecked
                self.clear_stored_data()
                print("Login data not stored (Remember Me unchecked)")
            
            # Navigate to home screen
            app = App.get_running_app()
            if hasattr(app, 'root') and app.root:
                app.root.current = "home"
            
        except Exception as e:
            print(f"Login error: {e}")
            App.get_running_app().show_contact_dialog("Error", "Invalid email or password")
    
    def logout(self):
        """Logout user and clear stored data"""
        self.clear_stored_data()
        print("User logged out and data cleared")