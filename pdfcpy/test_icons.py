from flask import Flask
import os

app = Flask(__name__, static_folder='static')

with app.app_context():
    print('Static folder:', app.static_folder)
    static_icons_path = os.path.join(app.static_folder, 'icons')
    print('Icons path exists:', os.path.exists(static_icons_path))
    
    if os.path.exists(static_icons_path):
        icons = os.listdir(static_icons_path)
        print('Icons found:', len(icons))
        for icon in icons[:5]:  # Show first 5 icons
            print(f'  - {icon}')
    
    # Test merge.png specifically
    merge_path = os.path.join(static_icons_path, 'merge.png')
    print('merge.png exists:', os.path.exists(merge_path))
    if os.path.exists(merge_path):
        size = os.path.getsize(merge_path)
        print('merge.png size:', size, 'bytes')
