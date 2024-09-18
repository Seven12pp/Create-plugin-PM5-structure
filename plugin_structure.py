# Made by Seven12

from flask import Flask, request, send_file, render_template_string
import os
import zipfile
import shutil
import tempfile

app = Flask(__name__)

form_html = '''
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Créer un plugin</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
            text-align: center;
            position: relative;
        }
        h1 {
            font-size: 24px;
            margin-bottom: 20px;
        }
        label {
            font-weight: bold;
            display: block;
            margin-top: 10px;
        }
        input[type="text"], input[type="submit"] {
            width: calc(100% - 22px);
            padding: 10px;
            margin: 10px 0 20px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }
        input[type="submit"] {
            background-color: #007BFF;
            color: #fff;
            border: none;
            cursor: pointer;
        }
        input[type="submit"]:hover {
            background-color: #0056b3;
        }
        .footer {
            position: absolute;
            bottom: 10px;
            right: 10px;
            font-size: 12px;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Créer un plugin</h1>
        <form action="/" method="post">
            <label for="author_name">Nom de l'auteur:</label>
            <input type="text" id="author_name" name="author_name" required>
            <label for="plugin_name">Nom du plugin:</label>
            <input type="text" id="plugin_name" name="plugin_name" required>
            <input type="submit" value="Créer">
        </form>
        <div class="footer">Made by Seven12</div>
    </div>
</body>
</html>
'''

def create_structure(author_name, plugin_name):
    return {
        'src': {
            plugin_name: {
                author_name: ['Main.php']
            }
        },
        'resources': ['config.yml'],
        'plugin.yml': f'''name: {plugin_name}
version: 1.0.0
main: {plugin_name}\\{author_name}\\Main
api: [5.0.0]
author: {author_name}
'''
    }

def create_files(base_path, structure, author_name, plugin_name):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_files(path, content, author_name, plugin_name)
        elif isinstance(content, list):
            os.makedirs(path, exist_ok=True)
            for file_name in content:
                file_path = os.path.join(path, file_name)
                if file_name == 'Main.php':
                    with open(file_path, 'w') as f:
                        f.write(f'''<?php

namespace {plugin_name}\\{author_name};

use pocketmine\\event\\Listener;
use pocketmine\\plugin\\PluginBase;
use pocketmine\\Server;
use pocketmine\\utils\\SingletonTrait;

class Main extends PluginBase implements Listener{{

    use SingletonTrait;

    public function onEnable():void{{
        self::setInstance($this);
        $this->saveDefaultConfig();
        Server::getInstance()->getPluginManager()->registerEvents($this,$this);
    }}
}}
''')
                else:
                    open(file_path, 'w').close()
        else:
            with open(path, 'w') as f:
                f.write(content)

def create_zip(zip_name, structure, author_name, plugin_name):
    base_path = os.path.splitext(zip_name)[0]
    try:
        create_files(base_path, structure, author_name, plugin_name)
        with zipfile.ZipFile(zip_name, 'w') as z:
            for folder, _, files in os.walk(base_path):
                for file in files:
                    file_path = os.path.join(folder, file)
                    z.write(file_path, os.path.relpath(file_path, base_path))
    finally:
        shutil.rmtree(base_path)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        author_name = request.form['author_name']
        plugin_name = request.form['plugin_name']
        zip_name = f"{plugin_name}.zip"
        structure = create_structure(author_name, plugin_name)
        
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, zip_name)
        
        create_zip(zip_path, structure, author_name, plugin_name)
        
        return send_file(zip_path, as_attachment=True, download_name=zip_name)
    return render_template_string(form_html)

if __name__ == "__main__":
    app.run(debug=True)
