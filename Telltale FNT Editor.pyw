import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import threading
import traceback
import copy
import configparser

class LanguageManager:
    def __init__(self):
        self.settings_dir = "Settings"
        self.lang_files_dir = os.path.join(self.settings_dir, "Languages")
        self.user_settings_file = os.path.join(self.settings_dir, "User Settings.ini")
        self.current_language = "English"
        self.translations = {}
        
        # Criar diretórios se não existirem
        os.makedirs(self.settings_dir, exist_ok=True)
        os.makedirs(self.lang_files_dir, exist_ok=True)
        
        # Criar arquivo de idioma padrão se não existir
        self.create_default_language_file()
        
        # Carregar configurações do usuário
        self.load_user_settings()
        
        # Carregar traduções
        self.load_language(self.current_language)
    
    def load_user_settings(self):
        """Carrega as configurações do usuário a partir do arquivo INI"""
        self.user_settings = configparser.ConfigParser()
        
        if os.path.exists(self.user_settings_file):
            self.user_settings.read(self.user_settings_file)
            # Obter idioma selecionado
            if 'General' in self.user_settings and 'language' in self.user_settings['General']:
                self.current_language = self.user_settings['General']['language']
    
    def save_user_settings(self):
        """Salva as configurações do usuário no arquivo INI"""
        if 'General' not in self.user_settings:
            self.user_settings['General'] = {}
        
        self.user_settings['General']['language'] = self.current_language
        
        with open(self.user_settings_file, 'w') as f:
            self.user_settings.write(f)
    
    def load_language(self, language_name):
        """Carrega um arquivo de idioma específico"""
        lang_file = os.path.join(self.lang_files_dir, f"{language_name}.lang")
        self.translations = {}
        
        if os.path.exists(lang_file):
            try:
                # Analisar o arquivo de idioma
                with open(lang_file, 'r', encoding='utf-8') as f:
                    current_section = None
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                            
                        if line.startswith('Language:'):
                            # Não precisamos disso para a tradução
                            continue
                            
                        if line == 'Strings:':
                            current_section = 'Strings'
                            continue
                            
                        if current_section == 'Strings' and '=' in line:
                            key, value = line.split('=', 1)
                            self.translations[key.strip()] = value.strip()
            except Exception as e:
                print(f"Erro ao carregar idioma {language_name}: {e}")
                # Se falhar, usar inglês como fallback
                if language_name != "English":
                    self.load_language("English")
    
    def create_default_language_file(self):
        """Cria o arquivo de idioma padrão (English) se não existir"""
        default_file = os.path.join(self.lang_files_dir, "English.lang")
        if not os.path.exists(default_file):
            default_content = """# This will appear as the language name in selection
Language: English

# All application texts
Strings:

# Main window
MainTitle=Telltale FNT Editor

# Menu items
Menu.Edit=Edit
Menu.View=View
Menu.Tools=Tools
Menu.Help=Help
Menu.Settings=Settings
Menu.LanguageSettings=Language Settings

# Controls
Controls.Title=Controls
Button.LoadFNT=Load .fnt
Button.LoadImage=Load Image
Button.ReloadImage=↻
Button.ExportMarkings=Export markings
Check.AdvancedSettings=Advanced settings
Label.SelectCharacter=Select Character:
Label.CharacterProperties=Character Properties
Button.Undo=Undo
Button.Redo=Redo
Button.SaveChanges=Save Changes
Label.Zoom=Zoom:
Label.MappingArea=Mapping Area (drag to move)

# Character properties
Property.ID=ID
Property.x=x
Property.y=y
Property.width=width
Property.height=height
Property.xoffset=xoffset
Property.yoffset=yoffset
Property.xadvance=xadvance
Property.page=page
Label.Character=Character

# Status messages
Status.Ready=Ready
Status.LoadingFNT=Loading FNT file...
Status.LoadingImage=Loading image...
Status.ImageLoaded=Image loaded: {filename} ({width}x{height})
Status.ChangesSaved=Changes saved successfully!
Status.ExportComplete=Export completed successfully!
Status.Exporting=Exporting...

# Dialogs
Dialog.ConfirmExitTitle=Unsaved Changes
Dialog.ConfirmExitMessage=You have unsaved changes. Save before exiting?
Dialog.SaveOption=Save
Dialog.DontSaveOption=Don't Save
Dialog.CancelOption=Cancel
Dialog.LanguageSettings=Language Settings
Dialog.SelectLanguage=Select Language:
Dialog.ApplyLanguage=Apply

# Error messages
Error.Title=Error
Error.FileNotFound=File not found: {file}
Error.InvalidFNT=Invalid FNT file
Error.ImageLoadError=Error loading image
Error.SaveError=Error saving changes
Error.ExportError=Error during export

# Export window
Export.Title=Select Characters for Export
Button.SelectAll=Select All
Button.DeselectAll=Deselect All
Button.Confirm=Confirm
Button.ExportNow=Export Now

# Help window
Help.Title=Help
Help.WindowTitle=Help - Telltale FNT Editor
Help.Content=Telltale FNT Editor - User Guide\\n\\n1. Load .fnt file: Use the 'Load .fnt' button to open a font file\\n2. Load font image: Use the 'Load Image' button to open the corresponding font image\\n3. Edit characters: Select a character from the dropdown and edit its properties\\n4. Controls: Undo/Redo changes, save modifications, and adjust zoom level\\n5. Export: Select characters and export as marked image\\n6. Settings: Change language interface and show advanced controls\\n\\nKeyboard shortcuts:\\n- Ctrl+Z: Undo\\n- Ctrl+Y: Redo\\n\\nTip: You can drag the mapping area to reposition it within the window.
Button.Close=Close

# Tooltips and other texts
Text.CharacterDisplay=Character: {char}
Text.ExportFilename=marking.png
Text.ActionsCount=Actions: {count}
Text.Undone=Undone: {action}
Text.Redone=Redone: {action}
Text.NothingToUndo=Nothing more to undo
Text.NothingToRedo=Nothing more to redo
Text.LoadingAssociatedImage=Trying to load associated image: {file}
Text.ManualImageLoadRequired=FNT file loaded. Load image manually
"""
            with open(default_file, 'w', encoding='utf-8') as f:
                f.write(default_content)
    
    def get_available_languages(self):
        """Retorna a lista de idiomas disponíveis"""
        languages = []
        if os.path.exists(self.lang_files_dir):
            for file in os.listdir(self.lang_files_dir):
                if file.endswith(".lang"):
                    languages.append(file[:-5])
        return languages
    
    def set_language(self, language_name):
        """Define o idioma atual e salva a configuração"""
        if language_name in self.get_available_languages():
            self.current_language = language_name
            self.load_language(language_name)
            self.save_user_settings()
            return True
        return False
    
    def tr(self, key, default=None, **kwargs):
        """Retorna a tradução para uma chave específica com formatação"""
        text = self.translations.get(key, default if default is not None else key)
        
        # Aplica formatação se houver argumentos
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        
        return text

class FontMapViewer:
    # Mapeamento completo de IDs para caracteres
    ID_TO_CHAR = {
        0: '\x00', 1: '\x01', 2: '\x02', 3: '\x03', 4: '\x04', 5: '\x05', 6: '\x06', 7: '\x07',
        8: '\x08', 9: '\x09', 10: '\x0A', 11: '\x0B', 12: '\x0C', 13: '\x0D', 14: '\x0E', 15: '\x0F',
        16: '\x10', 17: '\x11', 18: '\x12', 19: '\x13', 20: '\x14', 21: '\x15', 22: '\x16', 23: '\x17',
        24: '\x18', 25: '\x19', 26: '\x1A', 27: '\x1B', 28: '\x1C', 29: '\x1D', 30: '\x1E', 31: '\x1F',
        32: ' ', 33: '!', 34: '"', 35: '#', 36: '$', 37: '%', 38: '&', 39: "'", 40: '(', 41: ')',
        42: '*', 43: '+', 44: ',', 45: '-', 46: '.', 47: '/', 48: '0', 49: '1', 50: '2', 51: '3',
        52: '4', 53: '5', 54: '6', 55: '7', 56: '8', 57: '9', 58: ':', 59: ';', 60: '<', 61: '=',
        62: '>', 63: '?', 64: '@', 65: 'A', 66: 'B', 67: 'C', 68: 'D', 69: 'E', 70: 'F', 71: 'G',
        72: 'H', 73: 'I', 74: 'J', 75: 'K', 76: 'L', 77: 'M', 78: 'N', 79: 'O', 80: 'P', 81: 'Q',
        82: 'R', 83: 'S', 84: 'T', 85: 'U', 86: 'V', 87: 'W', 88: 'X', 89: 'Y', 90: 'Z', 91: '[',
        92: '\\', 93: ']', 94: '^', 95: '_', 96: '`', 97: 'a', 98: 'b', 99: 'c', 100: 'd', 101: 'e',
        102: 'f', 103: 'g', 104: 'h', 105: 'i', 106: 'j', 107: 'k', 108: 'l', 109: 'm', 110: 'n',
        111: 'o', 112: 'p', 113: 'q', 114: 'r', 115: 's', 116: 't', 117: 'u', 118: 'v', 119: 'w',
        120: 'x', 121: 'y', 122: 'z', 123: '{', 124: '|', 125: '}', 126: '~', 127: '\x7f', 128: '€',
        129: '\x81', 130: '‚', 131: 'ƒ', 132: '„', 133: '…', 134: '†', 135: '‡', 136: 'ˆ', 137: '‰',
        138: 'Š', 139: '‹', 140: 'Œ', 141: '\x8d', 142: 'Ž', 143: '\x8f', 144: '\x90', 145: '‘',
        146: '’', 147: '“', 148: '”', 149: '•', 150: '–', 151: '—', 152: '˜', 153: '™', 154: 'š',
        155: '›', 156: 'œ', 157: '\x9d', 158: 'ž', 159: 'Ÿ', 160: '\xa0', 161: '¡', 162: '¢',
        163: '£', 164: '¤', 165: '¥', 166: '¦', 167: '§', 168: '¨', 169: '©', 170: 'ª', 171: '«',
        172: '¬', 173: '\xad', 174: '®', 175: '¯', 176: '°', 177: '±', 178: '²', 179: '³', 180: '´',
        181: 'µ', 182: '¶', 183: '·', 184: '¸', 185: '¹', 186: 'º', 187: '»', 188: '¼', 189: '½',
        190: '¾', 191: '¿', 192: 'À', 193: 'Á', 194: 'Â', 195: 'Ã', 196: 'Ä', 197: 'Å', 198: 'Æ',
        199: 'Ç', 200: 'È', 201: 'É', 202: 'Ê', 203: 'Ë', 204: 'Ì', 205: 'Í', 206: 'Î', 207: 'Ï',
        208: 'Ð', 209: 'Ñ', 210: 'Ò', 211: 'Ó', 212: 'Ô', 213: 'Õ', 214: 'Ö', 215: '×', 216: 'Ø',
        217: 'Ù', 218: 'Ú', 219: 'Û', 220: 'Ü', 221: 'Ý', 222: 'Þ', 223: 'ß', 224: 'à', 225: 'á',
        226: 'â', 227: 'ã', 228: 'ä', 229: 'å', 230: 'æ', 231: 'ç', 232: 'è', 233: 'é', 234: 'ê',
        235: 'ë', 236: 'ì', 237: 'í', 238: 'î', 239: 'ï', 240: 'ð', 241: 'ñ', 242: 'ò', 243: 'ó',
        244: 'ô', 245: 'õ', 246: 'ö', 247: '÷', 248: 'ø', 249: 'ù', 250: 'ú', 251: 'û', 252: 'ü',
        253: 'ý', 254: 'þ', 255: 'ÿ'
    }

    def __init__(self, root):
        self.root = root
        
        # Inicializar gerenciador de idiomas
        self.lang = LanguageManager()
        
        # Configurar janela principal com título traduzido
        self.root.title(self.lang.tr("MainTitle"))
        self.root.geometry("1200x800")
        self.root.configure(bg='#121212')
        
        # Flag para evitar recursão nos sliders
        self.programmatic_slider_update = False
        
        # Configurar sistema de desfazer/refazer
        self.undo_stack = []       # Pilha para ações desfeitas
        self.redo_stack = []        # Pilha para ações refeitas
        self.action_count = 0       # Contador de ações
        self.max_undo_actions = 0   # Sem limite máximo
        
        # Configurar atalhos de teclado
        self.root.bind("<Control-z>", self.undo)
        self.root.bind("<Control-y>", self.redo)
        self.root.bind("<Control-Z>", self.undo)
        self.root.bind("<Control-Y>", self.redo)
        
        # Conjunto para caracteres selecionados para exportação
        self.selected_chars = set()
        
        # Variável para controle de configurações avançadas
        self.advanced_settings = tk.BooleanVar(value=False)
        
        # Verificar se há alterações não salvas
        self.unsaved_changes = False
        
        self.setup_styles()
        self.create_widgets()
        
        self.font_data = {}
        self.page_files = {}
        self.image_references = {}
        self.current_image = None
        self.current_char_id = None
        self.fnt_path = None
        self.image_path = None
        self.image_zoom = 1.0
        self.scroll_start_x = 0
        self.scroll_start_y = 0
        
        # Variáveis para redimensionamento da área de mapeamento
        self.resizing = False
        self.moving = False
        self.resize_start_x = 0
        self.resize_start_y = 0
        self.move_start_x = 0
        self.move_start_y = 0
        
        # Variáveis para movimento e redimensionamento visual
        self.dragging = False
        self.resizing_rect = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.rect_start_coords = None
        self.resize_handle_size = 8
        
        # Indicador de carregamento
        self.loading = False
        self.loading_label = ttk.Label(
            self.root, 
            text=self.lang.tr("Status.LoadingFNT"), 
            background="#1e1e1e", 
            foreground="#ffcc00",
            padding=10,
            anchor="center"
        )
        
        # Barra de status
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            self.root, 
            textvariable=self.status_var, 
            anchor=tk.W,
            background='#2d2d2d',
            foreground='#ffcc00'
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var.set(self.lang.tr("Status.Ready"))
        
        # Configurar evento de fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self.confirm_exit)
        
        # Criar menu
        self.create_menu()
        
        # Forçar retradução da interface após inicialização
        self.retranslate_ui()

    def create_menu(self):
        """Cria a barra de menu com suporte a tradução"""
        menu_bar = tk.Menu(self.root)
        
        # Menu Configurações
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(
            label=self.lang.tr("Menu.LanguageSettings"), 
            command=self.open_language_settings
        )
        menu_bar.add_cascade(label=self.lang.tr("Menu.Settings"), menu=settings_menu)
        
        # Menu Ajuda
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(
            label=self.lang.tr("Help.Title"), 
            command=self.show_help
        )
        menu_bar.add_cascade(
            label=self.lang.tr("Menu.Help"), 
            menu=help_menu
        )
        
        self.root.config(menu=menu_bar)

    def show_help(self):
        """Mostra a janela de ajuda explicando a ferramenta"""
        help_win = tk.Toplevel(self.root)
        help_win.title(self.lang.tr("Help.WindowTitle"))
        help_win.geometry("600x400")
        help_win.transient(self.root)
        help_win.grab_set()
        
        main_frame = ttk.Frame(help_win)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Obter texto de ajuda formatado
        help_text = self.lang.tr("Help.Content")
        # Substituir \n por quebras de linha reais
        help_text = help_text.replace('\\n', '\n')
        
        # Frame com scroll para o conteúdo da ajuda
        scroll_frame = ttk.Frame(main_frame)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(
            scroll_frame, 
            wrap="word", 
            bg='#1e1e1e', 
            fg='#e0e0e0',
            font=("Arial", 10),
            padx=10,
            pady=10,
            yscrollcommand=scrollbar.set
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # Inserir texto com formatação preservada
        text_widget.insert("1.0", help_text)
        text_widget.config(state="disabled")
        
        # Botão de fechar
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            btn_frame, 
            text=self.lang.tr("Button.Close"), 
            command=help_win.destroy
        ).pack(side=tk.RIGHT)

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        bg_color = '#1e1e1e'
        fg_color = '#e0e0e0'
        accent_color = '#4a76cf'
        highlight_color = '#ff5555'
        
        self.style.configure('.', background=bg_color, foreground=fg_color)
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabel', background=bg_color, foreground=fg_color)
        self.style.configure('TButton', background='#333', foreground=fg_color, borderwidth=1)
        self.style.map('TButton', 
                      background=[('active', '#555'), ('pressed', accent_color)],
                      foreground=[('active', '#fff')])
        self.style.configure('TCombobox', fieldbackground=bg_color, background=bg_color, foreground='#e0e0e0')
        self.style.configure('TScrollbar', background='#333')
        self.style.configure('Treeview', background=bg_color, fieldbackground=bg_color, foreground=fg_color)
        self.style.map('Treeview', background=[('selected', accent_color)])
        self.style.configure('Treeview.Heading', background='#333', foreground=fg_color)
        self.style.configure('Edit.TEntry', fieldbackground='#333', foreground='#ffcc00')
        
        # Estilo para combobox no diálogo de idioma
        self.style.configure('Lang.TCombobox', fieldbackground='#1e1e1e', background='#1e1e1e', foreground='#e0e0e0')

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Painel de Controles
        self.control_frame = ttk.LabelFrame(main_frame, text=self.lang.tr("Controls.Title"))
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=10)
        
        btn_frame = ttk.Frame(self.control_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.load_fnt_btn = ttk.Button(btn_frame, text=self.lang.tr("Button.LoadFNT"), command=self.load_fnt)
        self.load_fnt_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Frame para os botões de imagem
        img_btn_frame = ttk.Frame(btn_frame)
        img_btn_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        self.load_image_btn = ttk.Button(img_btn_frame, text=self.lang.tr("Button.LoadImage"), command=self.load_image)
        self.load_image_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Botão de recarregar imagem
        self.reload_image_btn = ttk.Button(
            img_btn_frame, 
            text=self.lang.tr("Button.ReloadImage"), 
            width=3,
            command=self.reload_image
        )
        self.reload_image_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Botão de exportar marcações
        self.export_markings_btn = ttk.Button(
            btn_frame, 
            text=self.lang.tr("Button.ExportMarkings"), 
            command=self.select_chars_for_export
        )
        self.export_markings_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Checkbutton para configurações avançadas
        advanced_frame = ttk.Frame(self.control_frame)
        advanced_frame.pack(fill=tk.X, pady=(10, 5))
        self.advanced_check = ttk.Checkbutton(
            advanced_frame, 
            text=self.lang.tr("Check.AdvancedSettings"), 
            variable=self.advanced_settings,
            command=self.toggle_advanced_settings
        )
        self.advanced_check.pack(anchor=tk.W)
        
        self.select_char_label = ttk.Label(self.control_frame, text=self.lang.tr("Label.SelectCharacter"))
        self.select_char_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.char_combobox = ttk.Combobox(self.control_frame, state='readonly')
        self.char_combobox.pack(fill=tk.X)
        self.char_combobox.bind('<<ComboboxSelected>>', self.on_char_select)
        
        # Painel de Informações com barras de rolagem
        self.info_frame = ttk.LabelFrame(self.control_frame, text=self.lang.tr("Label.CharacterProperties"))
        self.info_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Usar propriedades definidas no arquivo de idioma
        properties = [
            self.lang.tr("Property.ID"),
            self.lang.tr("Property.x"),
            self.lang.tr("Property.y"),
            self.lang.tr("Property.width"),
            self.lang.tr("Property.height"),
            self.lang.tr("Property.xoffset"),
            self.lang.tr("Property.yoffset"),
            self.lang.tr("Property.xadvance"),
            self.lang.tr("Property.page")
        ]
        
        self.info_vars = {}
        self.entry_widgets = {}
        self.slider_widgets = {}  # Para armazenar as barras de rolagem
        
        for i, label in enumerate(properties):
            # Frame para cada propriedade
            prop_frame = ttk.Frame(self.info_frame)
            prop_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Label e campo de entrada
            frame = ttk.Frame(prop_frame)
            frame.pack(fill=tk.X, pady=(0, 2))
            
            lbl = ttk.Label(frame, text=f"{label}:", width=10, anchor=tk.W)
            lbl.pack(side=tk.LEFT)
            
            # Usar o nome da propriedade sem prefixo para chave
            prop_key = label.lower().replace(' ', '')  # Remover espaços para chave
            
            var = tk.StringVar(value="")
            self.info_vars[prop_key] = var
            
            if prop_key in ["id", "page"]:  # Campos não editáveis
                if prop_key == "id":
                    id_frame = ttk.Frame(frame)
                    id_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    id_label = ttk.Label(id_frame, textvariable=var, anchor=tk.W)
                    id_label.pack(side=tk.LEFT)
                    self.char_display_var = tk.StringVar()
                    char_label = ttk.Label(
                        id_frame, 
                        textvariable=self.char_display_var, 
                        foreground="#ffcc00", 
                        anchor=tk.W
                    )
                    char_label.pack(side=tk.LEFT, padx=(5, 0))
                else:
                    ttk.Label(frame, textvariable=var, anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True)
            else:
                entry = ttk.Entry(frame, textvariable=var, style='Edit.TEntry')
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.entry_widgets[prop_key] = entry
                entry.bind("<FocusOut>", self.update_char_data)
                entry.bind("<Return>", self.update_char_data)
                
                # Frame para a barra de rolagem (inicialmente oculta)
                slider_frame = ttk.Frame(prop_frame)
                slider_frame.pack(fill=tk.X, pady=(0, 2))
                
                # Criar barra de rolagem
                slider = ttk.Scale(
                    slider_frame, 
                    from_=0, 
                    to=100, 
                    orient=tk.HORIZONTAL,
                    command=lambda value, k=prop_key: self.on_slider_change(k, value)
                )
                slider.pack(fill=tk.X)
                self.slider_widgets[prop_key] = (slider_frame, slider)
                
                # Começar oculta
                slider_frame.pack_forget()

        # Botões de ação
        btn_save_frame = ttk.Frame(self.control_frame)
        btn_save_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.undo_btn = ttk.Button(btn_save_frame, text=f"← {self.lang.tr('Button.Undo')}", command=self.undo)
        self.undo_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.redo_btn = ttk.Button(btn_save_frame, text=f"{self.lang.tr('Button.Redo')} →", command=self.redo)
        self.redo_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.save_btn = ttk.Button(btn_save_frame, text=self.lang.tr("Button.SaveChanges"), command=self.save_changes)
        self.save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Controles de zoom
        zoom_frame = ttk.Frame(self.control_frame)
        zoom_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.zoom_label = ttk.Label(zoom_frame, text=f"{self.lang.tr('Label.Zoom')}:")
        self.zoom_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.zoom_var = tk.StringVar(value="100%")
        zoom_combo = ttk.Combobox(zoom_frame, textvariable=self.zoom_var, width=8, state='readonly')
        zoom_combo['values'] = ('50%', '75%', '100%', '125%', '150%', '200%')
        zoom_combo.current(2)
        zoom_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        zoom_combo.bind('<<ComboboxSelected>>', self.apply_zoom)

        # Área de Visualização com redimensionamento
        self.view_frame = ttk.Frame(main_frame)
        self.view_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Container para canvas e barras de rolagem
        canvas_container = ttk.Frame(self.view_frame)
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        # Barra de rolagem vertical
        self.scroll_y = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Barra de rolagem horizontal
        self.scroll_x = ttk.Scrollbar(canvas_container, orient=tk.HORIZONTAL)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Canvas com barras de rolagem
        self.canvas = tk.Canvas(
            canvas_container, 
            bg='#2d2d2d', 
            highlightthickness=0,
            yscrollcommand=self.scroll_y.set,
            xscrollcommand=self.scroll_x.set
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scroll_y.config(command=self.canvas.yview)
        self.scroll_x.config(command=self.canvas.xview)
        
        # Configurar eventos de rolagem
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)
        self.canvas.bind("<Button-5>", self.on_mousewheel)
        self.canvas.bind("<ButtonPress-1>", self.scroll_start)
        self.canvas.bind("<B1-Motion>", self.scroll_move)
        
        # Configurar eventos para redimensionar e mover a área de visualização
        resize_grip = ttk.Sizegrip(self.view_frame)
        resize_grip.place(relx=1.0, rely=1.0, anchor="se")
        resize_grip.bind("<ButtonPress-1>", self.start_resize)
        resize_grip.bind("<B1-Motion>", self.on_resize)
        
        # Área para mover (barra de título da área de visualização)
        title_frame = ttk.Frame(self.view_frame, height=20)
        title_frame.pack(fill=tk.X)
        title_frame.bind("<ButtonPress-1>", self.start_move)
        title_frame.bind("<B1-Motion>", self.on_move)
        
        self.title_label = ttk.Label(title_frame, text=self.lang.tr("Label.MappingArea"))
        self.title_label.pack(side=tk.LEFT, padx=5)
        
        # Bind para movimento e redimensionamento visual
        self.canvas.tag_bind("move_handle", "<ButtonPress-1>", self.start_move_rect)
        self.canvas.tag_bind("resize_handle", "<ButtonPress-1>", self.start_resize_rect)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

    def reload_image(self):
        """Recarrega a imagem atual (útil após mudança de zoom)"""
        if self.image_path:
            self.load_image(self.image_path)

    def open_language_settings(self):
        """Abre a janela de configurações de idioma"""
        settings_win = tk.Toplevel(self.root)
        settings_win.title(self.lang.tr("Dialog.LanguageSettings"))
        settings_win.geometry("300x200")
        settings_win.transient(self.root)
        settings_win.grab_set()
        settings_win.configure(bg='#121212')
        
        main_frame = ttk.Frame(settings_win)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(main_frame, text=self.lang.tr("Dialog.SelectLanguage")).pack(anchor=tk.W, pady=(10, 5))
        
        # Usar estilo customizado para melhor legibilidade
        lang_combo = ttk.Combobox(main_frame, state='readonly', style='Lang.TCombobox')
        lang_combo['values'] = self.lang.get_available_languages()
        lang_combo.set(self.lang.current_language)
        lang_combo.pack(fill=tk.X, pady=5)
        
        def apply_language():
            new_lang = lang_combo.get()
            if new_lang != self.lang.current_language:
                self.lang.set_language(new_lang)
                self.retranslate_ui()
                settings_win.destroy()
        
        ttk.Button(
            main_frame, 
            text=self.lang.tr("Dialog.ApplyLanguage"), 
            command=apply_language
        ).pack(side=tk.BOTTOM, pady=10)

    def retranslate_ui(self):
        """Atualiza todos os textos da interface com o novo idioma"""
        # Atualizar título da janela principal
        self.root.title(self.lang.tr("MainTitle"))
        
        # Atualizar barra de menu
        self.create_menu()
        
        # Atualizar barra de status
        self.status_var.set(self.lang.tr("Status.Ready"))
        self.loading_label.config(text=self.lang.tr("Status.LoadingFNT"))
        
        # Atualizar widgets principais
        self.control_frame.config(text=self.lang.tr("Controls.Title"))
        self.load_fnt_btn.config(text=self.lang.tr("Button.LoadFNT"))
        self.load_image_btn.config(text=self.lang.tr("Button.LoadImage"))
        self.reload_image_btn.config(text=self.lang.tr("Button.ReloadImage"))
        self.export_markings_btn.config(text=self.lang.tr("Button.ExportMarkings"))
        self.advanced_check.config(text=self.lang.tr("Check.AdvancedSettings"))
        self.select_char_label.config(text=self.lang.tr("Label.SelectCharacter"))
        self.info_frame.config(text=self.lang.tr("Label.CharacterProperties"))
        self.undo_btn.config(text=f"← {self.lang.tr('Button.Undo')}")
        self.redo_btn.config(text=f"{self.lang.tr('Button.Redo')} →")
        self.save_btn.config(text=self.lang.tr("Button.SaveChanges"))
        self.zoom_label.config(text=f"{self.lang.tr('Label.Zoom')}:")
        self.title_label.config(text=self.lang.tr("Label.MappingArea"))
        
        # Atualizar propriedades dos caracteres
        properties = [
            self.lang.tr("Property.ID"),
            self.lang.tr("Property.x"),
            self.lang.tr("Property.y"),
            self.lang.tr("Property.width"),
            self.lang.tr("Property.height"),
            self.lang.tr("Property.xoffset"),
            self.lang.tr("Property.yoffset"),
            self.lang.tr("Property.xadvance"),
            self.lang.tr("Property.page")
        ]
        
        for i, (label, prop_frame) in enumerate(zip(properties, self.info_frame.winfo_children())):
            frame = prop_frame.winfo_children()[0]  # O frame interno que contém os widgets
            label_widget = frame.winfo_children()[0]
            label_widget.config(text=f"{label}:")

    def toggle_advanced_settings(self):
        """Mostra ou esconde as barras de rolagem avançadas"""
        show = self.advanced_settings.get()
        for slider_frame, _ in self.slider_widgets.values():
            if show:
                slider_frame.pack(fill=tk.X, pady=(0, 2))
            else:
                slider_frame.pack_forget()
                
        # Atualizar limites dos sliders quando ativados
        if show:
            self.update_sliders_limits()

    def on_slider_change(self, key, value):
        """Atualiza o campo quando a barra de rolagem é movida"""
        if self.programmatic_slider_update:
            return
            
        try:
            # Converter valor para inteiro
            int_value = int(float(value))
            self.info_vars[key].set(str(int_value))
            self.update_char_data()
        except ValueError:
            pass

    def start_resize(self, event):
        """Inicia o redimensionamento da área de visualização"""
        self.resizing = True
        self.resize_start_x = event.x_root
        self.resize_start_y = event.y_root
        self.original_width = self.view_frame.winfo_width()
        self.original_height = self.view_frame.winfo_height()

    def on_resize(self, event):
        """Redimensiona a área de visualização durante o arraste"""
        if self.resizing:
            delta_x = event.x_root - self.resize_start_x
            delta_y = event.y_root - self.resize_start_y
            
            new_width = max(300, self.original_width + delta_x)
            new_height = max(300, self.original_height + delta_y)
            
            self.view_frame.config(width=new_width, height=new_height)

    def start_move(self, event):
        """Inicia o movimento da área de visualização"""
        self.moving = True
        self.move_start_x = event.x
        self.move_start_y = event.y

    def on_move(self, event):
        """Move a área de visualização durante o arraste"""
        if self.moving:
            # Calcular deslocamento
            delta_x = event.x - self.move_start_x
            delta_y = event.y - self.move_start_y
            
            # Obter posição atual
            x = self.view_frame.winfo_x() + delta_x
            y = self.view_frame.winfo_y() + delta_y
            
            # Limitar movimento à área da janela principal
            x = max(0, min(x, self.root.winfo_width() - self.view_frame.winfo_width()))
            y = max(0, min(y, self.root.winfo_height() - self.view_frame.winfo_height()))
            
            # Reposicionar o frame
            self.view_frame.place(x=x, y=y)
            
            # Atualizar ponto de início para o próximo movimento
            self.move_start_x = event.x
            self.move_start_y = event.y

    def on_mousewheel(self, event):
        """Manipula o scroll do mouse com suporte multiplataforma"""
        if event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):
            # Scroll para baixo ou direita
            if event.state & 0x1:  # Shift pressionado -> horizontal
                self.canvas.xview_scroll(1, "units")
            else:
                self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):
            # Scroll para cima ou esquerda
            if event.state & 0x1:  # Shift pressionado -> horizontal
                self.canvas.xview_scroll(-1, "units")
            else:
                self.canvas.yview_scroll(-1, "units")

    def scroll_start(self, event):
        """Inicia o arraste para rolagem"""
        self.canvas.scan_mark(event.x, event.y)
        self.scroll_start_x = event.x
        self.scroll_start_y = event.y

    def scroll_move(self, event):
        """Move o canvas durante o arraste"""
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def apply_zoom(self, event=None):
        """Aplica o fator de zoom selecionado"""
        zoom_str = self.zoom_var.get().replace('%', '')
        try:
            self.image_zoom = float(zoom_str) / 100.0
            if self.current_image and self.image_path:
                # Recarrega a imagem com o novo zoom
                threading.Thread(
                    target=self._load_image_thread, 
                    args=(self.image_path,),
                    daemon=True
                ).start()
        except ValueError:
            self.image_zoom = 1.0

    def load_fnt(self):
        file_path = filedialog.askopenfilename(filetypes=[("FNT files", "*.fnt")])
        if not file_path:
            return
            
        # Salvar estado antes de carregar novo arquivo
        if self.font_data:
            self.save_state("Before loading new FNT file")
            
        self.status_var.set(self.lang.tr("Status.LoadingFNT"))
        self.show_loading(True)
        
        threading.Thread(
            target=self._load_fnt_thread, 
            args=(file_path,),
            daemon=True
        ).start()

    def _load_fnt_thread(self, file_path):
        try:
            font_data = {}
            page_files = {}
            char_ids = []
            char_display = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                if not lines:
                    raise ValueError(self.lang.tr("Error.InvalidFNT"))
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    if line.startswith('info'):
                        continue
                        
                    elif line.startswith('common'):
                        parts = line.split()
                        for part in parts[1:]:
                            if '=' in part:
                                key, value = part.split('=')
                                if key == 'scaleW':
                                    self.image_width = int(value)
                                elif key == 'scaleH':
                                    self.image_height = int(value)
                    
                    elif line.startswith('page'):
                        parts = line.split()
                        if len(parts) < 3:
                            raise ValueError(f"Invalid page line: {line}")
                            
                        page_id = None
                        file_name = None
                        
                        for part in parts[1:]:
                            if '=' in part:
                                key, value = part.split('=')
                                if key == 'id':
                                    page_id = int(value)
                                elif key == 'file':
                                    file_name = value.strip('"')
                        
                        if page_id is None or file_name is None:
                            raise ValueError(f"Incomplete page line: {line}")
                            
                        page_files[page_id] = file_name
                    
                    elif line.startswith('char '):
                        parts = line.split()
                        if len(parts) < 10:
                            raise ValueError(f"Invalid char line: {line}")
                            
                        char_info = {}
                        for part in parts[1:]:
                            if '=' in part:
                                key, value = part.split('=')
                                try:
                                    char_info[key] = int(value)
                                except ValueError:
                                    continue
                        
                        if 'id' not in char_info:
                            raise ValueError(f"Char without ID: {line}")
                            
                        char_id = char_info['id']
                        font_data[char_id] = char_info
                        char_ids.append(char_id)
                        
                        char = self.ID_TO_CHAR.get(char_id, f'[{char_id}]')
                        char_display.append(f"{char} (ID: {char_id})")
            
            self.root.after(0, self._load_fnt_complete, file_path, font_data, page_files, char_ids, char_display)
                
        except Exception as e:
            error_msg = f"{self.lang.tr('Error.Title')}: {str(e)}\n\n{traceback.format_exc()}"
            self.root.after(0, self._load_fnt_error, error_msg)

    def _load_fnt_complete(self, file_path, font_data, page_files, char_ids, char_display):
        try:
            self.fnt_path = file_path
            self.font_data = font_data
            self.page_files = page_files
            
            self.char_combobox['values'] = char_display
            if char_ids:
                self.char_combobox.current(0)
                self.on_char_select()
            else:
                self.status_var.set(self.lang.tr("Error.InvalidFNT"))
            
            self.selected_chars = set(char_ids)
            self.unsaved_changes = False
            
            # Tentar carregar imagem automaticamente se houver apenas 1 página
            if len(page_files) == 1:
                page_file = list(page_files.values())[0]
                fnt_dir = os.path.dirname(self.fnt_path)
                img_path = os.path.join(fnt_dir, page_file)
                
                if os.path.exists(img_path):
                    self.status_var.set(self.lang.tr(
                        "Text.LoadingAssociatedImage", 
                        file=page_file
                    ))
                    self.load_image(img_path)
                else:
                    self.status_var.set(self.lang.tr(
                        "Error.FileNotFound", 
                        file=page_file
                    ))
            else:
                self.status_var.set(self.lang.tr("Text.ManualImageLoadRequired"))
                
        except Exception as e:
            error_msg = f"{self.lang.tr('Error.Title')}: {str(e)}\n\n{traceback.format_exc()}"
            messagebox.showerror(self.lang.tr("Error.Title"), error_msg)
        finally:
            self.show_loading(False)

    def _load_fnt_error(self, error):
        messagebox.showerror(self.lang.tr("Error.Title"), error)
        self.status_var.set(self.lang.tr("Error.InvalidFNT"))
        self.show_loading(False)

    def load_image(self, file_path=None):
        # Salvar estado antes de carregar nova imagem
        if self.current_image:
            self.save_state("Before loading new image")
            
        if not file_path:
            file_path = filedialog.askopenfilename(
                filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.dds")]
            )
            
        if not file_path:
            return
            
        self.image_path = file_path
        self.status_var.set(self.lang.tr("Status.LoadingImage"))
        self.show_loading(True)
        
        threading.Thread(
            target=self._load_image_thread, 
            args=(file_path,),
            daemon=True
        ).start()

    def _load_image_thread(self, file_path):
        try:
            img = Image.open(file_path)
            self.root.after(0, self._display_image, img, file_path)
        except Exception as e:
            error_msg = f"{self.lang.tr('Error.ImageLoadError')}:\n{str(e)}\n\n{traceback.format_exc()}"
            self.root.after(0, self._load_image_error, error_msg)
        finally:
            self.root.after(0, self.show_loading, False)

    def _display_image(self, img, file_path):
        try:
            self.canvas.delete("all")
            self.current_image = img.copy()
            
            if self.image_zoom != 1.0:
                new_width = int(img.width * self.image_zoom)
                new_height = int(img.height * self.image_zoom)
                zoomed_img = img.resize((new_width, new_height), Image.LANCZOS)
            else:
                zoomed_img = img.copy()
                
            tk_img = ImageTk.PhotoImage(zoomed_img)
            self.image_references["current"] = tk_img
            
            self.canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)
            self.canvas.config(
                scrollregion=(0, 0, zoomed_img.width, zoomed_img.height)
            )
            
            self.canvas.xview_moveto(0)
            self.canvas.yview_moveto(0)
            
            filename = os.path.basename(file_path)
            status_text = self.lang.tr(
                "Status.ImageLoaded", 
                filename=filename, 
                width=img.width, 
                height=img.height
            )
            self.status_var.set(status_text)
            
            if self.current_char_id:
                self.highlight_char(self.current_char_id)
            elif self.font_data:
                first_char_id = next(iter(self.font_data.keys()), None)
                if first_char_id:
                    self.current_char_id = first_char_id
                    self.highlight_char(first_char_id)
                    
        except Exception as e:
            error_msg = f"{self.lang.tr('Error.Title')}:\n{str(e)}\n\n{traceback.format_exc()}"
            messagebox.showerror(self.lang.tr("Error.Title"), error_msg)

    def _load_image_error(self, error):
        messagebox.showerror(self.lang.tr("Error.Title"), error)
        self.status_var.set(self.lang.tr("Error.ImageLoadError"))

    def on_char_select(self, event=None):
        try:
            selection = self.char_combobox.get()
            if not selection:
                return
                
            char_id_str = selection.split('(ID: ')[-1].rstrip(')')
            char_id = int(char_id_str)
            self.current_char_id = char_id
            
            char_info = self.font_data.get(char_id)
            if not char_info:
                return
                
            # Atualizar todas as propriedades
            for key, var in self.info_vars.items():
                var.set(str(char_info.get(key, '')))
            
            # Atualizar display do caractere
            char_display = self.ID_TO_CHAR.get(char_id, f'[{char_id}]')
            self.char_display_var.set(
                self.lang.tr("Text.CharacterDisplay", char=char_display)
            )
            
            self.update_sliders_limits()
            
            if self.current_image:
                self.highlight_char(char_id)
        except (ValueError, IndexError) as e:
            print(f"Error selecting character: {e}")

    def highlight_char(self, char_id):
        char_info = self.font_data.get(char_id)
        if not char_info or not self.current_image:
            return
            
        self.canvas.delete("highlight")
        
        x = char_info['x'] * self.image_zoom
        y = char_info['y'] * self.image_zoom
        width = char_info['width'] * self.image_zoom
        height = char_info['height'] * self.image_zoom
        
        rect_id = self.canvas.create_rectangle(
            x, y, x + width, y + height,
            outline="#ff5555", width=2, tags=("highlight", "rect", "move_handle")
        )
        
        center_x = x + width // 2
        center_y = y + height // 2
        self.canvas.create_oval(
            center_x - 3, center_y - 3,
            center_x + 3, center_y + 3,
            fill="#55ff55", outline="", tags="highlight"
        )
        
        self.canvas.create_text(
            x, y - 10, 
            text=f"{char_info['width']}x{char_info['height']}", 
            fill="#ffcc00", anchor=tk.NW, tags="highlight"
        )
        
        handle_x = x + width - self.resize_handle_size/2
        handle_y = y + height - self.resize_handle_size/2
        self.canvas.create_rectangle(
            handle_x, handle_y, 
            handle_x + self.resize_handle_size, handle_y + self.resize_handle_size,
            fill="#55ff55", outline="#ffffff", tags=("highlight", "resize_handle")
        )
        
        bbox = (x, y, x + width, y + height)
        self.center_view(bbox)

    def center_view(self, bbox):
        x1, y1, x2, y2 = bbox
        img_width = self.current_image.width * self.image_zoom
        img_height = self.current_image.height * self.image_zoom
        
        visible_width = self.canvas.winfo_width()
        visible_height = self.canvas.winfo_height()
        
        scroll_x = max(0, min(x1 - (visible_width - (x2 - x1)) / 2, img_width - visible_width))
        scroll_y = max(0, min(y1 - (visible_height - (y2 - y1)) / 2, img_height - visible_height))
        
        self.canvas.xview_moveto(scroll_x / img_width)
        self.canvas.yview_moveto(scroll_y / img_height)

    def save_state(self, action_description=None):
        """Salva o estado atual para desfazer/refazer"""
        # Criar uma cópia profunda do estado atual
        state = {
            'font_data': copy.deepcopy(self.font_data) if self.font_data else {},
            'current_char_id': self.current_char_id,
            'action_description': action_description or f"Action {self.action_count}",
            'action_count': self.action_count
        }
        
        self.undo_stack.append(state)
        self.redo_stack = []  # Limpar pilha de refazer ao fazer nova ação
        self.action_count += 1
        self.unsaved_changes = True
        
        # Atualizar título da janela para mostrar o contador de ações
        self.root.title(
            f"{self.lang.tr('MainTitle')} "
            f"({self.lang.tr('Text.ActionsCount', count=self.action_count)})"
        )

    def undo(self, event=None):
        """Desfaz a última alteração"""
        if not self.undo_stack:
            return
            
        # Salvar estado atual na pilha de refazer
        current_state = {
            'font_data': copy.deepcopy(self.font_data) if self.font_data else {},
            'current_char_id': self.current_char_id,
            'action_description': f"Current state before undo",
            'action_count': self.action_count
        }
        self.redo_stack.append(current_state)
        
        # Restaurar estado anterior
        state = self.undo_stack.pop()
        self.font_data = copy.deepcopy(state['font_data'])
        self.current_char_id = state['current_char_id']
        
        # Atualizar interface
        if self.current_char_id and self.current_char_id in self.font_data:
            char_info = self.font_data[self.current_char_id]
            for key, var in self.info_vars.items():
                var.set(str(char_info.get(key, '')))
            self.update_sliders_limits()
            
            if self.current_image:
                self.highlight_char(self.current_char_id)
        
        # Atualizar contador
        self.action_count = state['action_count']
        self.root.title(
            f"{self.lang.tr('MainTitle')} "
            f"({self.lang.tr('Text.ActionsCount', count=self.action_count)})"
        )
        self.status_var.set(
            self.lang.tr("Text.Undone", action=state['action_description'])
        )
        
        # Se ainda houver ações para desfazer, atualizar o botão
        if not self.undo_stack:
            self.status_var.set(self.lang.tr("Text.NothingToUndo"))

    def redo(self, event=None):
        """Refaz a última ação desfeita"""
        if not self.redo_stack:
            return
            
        # Salvar estado atual na pilha de desfazer
        current_state = {
            'font_data': copy.deepcopy(self.font_data) if self.font_data else {},
            'current_char_id': self.current_char_id,
            'action_description': f"Current state before redo",
            'action_count': self.action_count
        }
        self.undo_stack.append(current_state)
        
        # Restaurar estado refeito
        state = self.redo_stack.pop()
        self.font_data = copy.deepcopy(state['font_data'])
        self.current_char_id = state['current_char_id']
        
        # Atualizar interface
        if self.current_char_id and self.current_char_id in self.font_data:
            char_info = self.font_data[self.current_char_id]
            for key, var in self.info_vars.items():
                var.set(str(char_info.get(key, '')))
            self.update_sliders_limits()
            
            if self.current_image:
                self.highlight_char(self.current_char_id)
        
        # Atualizar contador
        self.action_count = state['action_count']
        self.root.title(
            f"{self.lang.tr('MainTitle')} "
            f"({self.lang.tr('Text.ActionsCount', count=self.action_count)})"
        )
        self.status_var.set(
            self.lang.tr("Text.Redone", action=state['action_description'])
        )
        
        # Se ainda houver ações para refazer, atualizar o botão
        if not self.redo_stack:
            self.status_var.set(self.lang.tr("Text.NothingToRedo"))

    def update_char_data(self, event=None):
        """Atualiza os dados do caractere com base nos campos editados"""
        if not self.current_char_id:
            return
            
        char_id = self.current_char_id
        char_info = self.font_data.get(char_id)
        if not char_info:
            return
            
        # Salvar estado antes das alterações
        self.save_state(f"Manual edit of character ID {char_id}")
            
        # Atualiza apenas os campos editáveis
        for key in self.entry_widgets:
            try:
                new_value = int(self.info_vars[key].get())
                char_info[key] = new_value
            except ValueError:
                # Mantém o valor anterior se inválido
                self.info_vars[key].set(str(char_info.get(key, 0)))
        
        # Atualiza sliders
        self.sync_slider(key)
        
        # Atualiza limites dependentes
        if key == 'x':
            self.update_slider_limits('width')
        elif key == 'y':
            self.update_slider_limits('height')
        
        # Atualiza imediatamente a visualização
        self.highlight_char(char_id)

    def save_changes(self):
        """Salva as alterações no arquivo .fnt mantendo a seleção atual"""
        if not self.fnt_path or not self.font_data:
            messagebox.showwarning(
                self.lang.tr("Error.Title"), 
                self.lang.tr("Error.InvalidFNT")
            )
            return
            
        # Salvar estado antes de salvar alterações
        self.save_state("Before saving changes to file")
            
        try:
            # Preserva o caractere selecionado
            current_char = self.current_char_id
            
            # Reconstroi o conteúdo do arquivo .fnt
            new_lines = []
            with open(self.fnt_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('char '):
                        parts = line.split()
                        char_id = int(parts[1].split('=')[1])
                        if char_id in self.font_data:
                            # Reconstrói a linha com os dados atualizados
                            char_info = self.font_data[char_id]
                            new_line = "char "
                            for key, value in char_info.items():
                                new_line += f"{key}={value} "
                            new_lines.append(new_line.strip())
                        else:
                            new_lines.append(line)
                    else:
                        new_lines.append(line)
            
            # Salva o arquivo atualizado
            with open(self.fnt_path, 'w', encoding='utf-8') as f:
                for line in new_lines:
                    f.write(line + "\n")
                
            # Restaura a seleção
            self.current_char_id = current_char
            if current_char:
                # Atualiza a combobox para mostrar o item correto
                char_display = f"{self.ID_TO_CHAR.get(current_char, f'[{current_char}]')} (ID: {current_char})"
                self.char_combobox.set(char_display)
                self.on_char_select()
                
            messagebox.showinfo(
                self.lang.tr("Status.Ready"), 
                self.lang.tr("Status.ChangesSaved")
            )
            self.unsaved_changes = False
            return True
            
        except Exception as e:
            messagebox.showerror(
                self.lang.tr("Error.Title"), 
                self.lang.tr("Error.SaveError") + f":\n{str(e)}"
            )
            return False

    def select_chars_for_export(self):
        """Abre uma janela para selecionar quais caracteres exportar"""
        if not self.font_data:
            messagebox.showwarning(
                self.lang.tr("Error.Title"), 
                self.lang.tr("Error.InvalidFNT")
            )
            return
            
        # Criar janela de seleção
        selection_window = tk.Toplevel(self.root)
        selection_window.title(self.lang.tr("Export.Title"))
        selection_window.geometry("500x600")
        selection_window.transient(self.root)
        selection_window.grab_set()
        selection_window.configure(bg='#121212')
        
        # Frame principal
        main_frame = ttk.Frame(selection_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas para rolagem
        canvas = tk.Canvas(main_frame, bg='#1e1e1e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empacotar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Vincular evento de scroll do mouse
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        
        # Variáveis para checkboxes
        self.check_vars = {}
        
        # Adicionar checkboxes para cada caractere
        for char_id in sorted(self.font_data.keys()):
            char = self.ID_TO_CHAR.get(char_id, f'[{char_id}]')
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            var = tk.BooleanVar(value=(char_id in self.selected_chars))
            self.check_vars[char_id] = var
            
            checkbox = ttk.Checkbutton(
                frame, 
                text=f"{char} (ID: {char_id})",
                variable=var,
                command=lambda cid=char_id: self.toggle_char_selection(cid)
            )
            checkbox.pack(side=tk.LEFT, anchor=tk.W)
        
        # Botões de ação
        btn_frame = ttk.Frame(selection_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            btn_frame, 
            text=self.lang.tr("Button.SelectAll"), 
            command=self.select_all_chars
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text=self.lang.tr("Button.DeselectAll"), 
            command=self.deselect_all_chars
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text=self.lang.tr("Button.Confirm"), 
            command=selection_window.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text=self.lang.tr("Button.ExportNow"), 
            command=lambda: [self.export_boxes(), selection_window.destroy()]
        ).pack(side=tk.RIGHT, padx=5)

    def toggle_char_selection(self, char_id):
        """Alterna a seleção de um caractere específico"""
        if self.check_vars[char_id].get():
            self.selected_chars.add(char_id)
        else:
            self.selected_chars.discard(char_id)

    def select_all_chars(self):
        """Seleciona todos os caracteres para exportação"""
        for char_id, var in self.check_vars.items():
            var.set(True)
            self.selected_chars.add(char_id)

    def deselect_all_chars(self):
        """Desseleciona todos os caracteres para exportação"""
        for char_id, var in self.check_vars.items():
            var.set(False)
            self.selected_chars.discard(char_id)

    def export_boxes(self):
        """Exporta as marcações dos caracteres como imagem PNG com fundo transparente"""
        if not self.current_image or not self.font_data:
            messagebox.showwarning(
                self.lang.tr("Error.Title"), 
                self.lang.tr("Error.InvalidFNT")
            )
            return
            
        # Salvar estado antes de exportar
        self.save_state("Before exporting markings")
            
        # Define o nome padrão do arquivo usando tradução
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            initialfile=self.lang.tr("Text.ExportFilename")
        )
        if not file_path:
            return
            
        self.status_var.set(self.lang.tr("Status.Exporting"))
        self.show_loading(True)
        
        threading.Thread(
            target=self._export_boxes_thread, 
            args=(file_path,),
            daemon=True
        ).start()

    def _export_boxes_thread(self, file_path):
        try:
            # Cria uma imagem transparente do mesmo tamanho
            img = Image.new("RGBA", self.current_image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Cor das marcações (vermelho puro - mesma cor do visualizador)
            box_color = (255, 0, 0, 255)  # Vermelho RGBA
            
            # Configurar a fonte Calibri tamanho 12
            try:
                # Tentar carregar Calibri
                font = ImageFont.truetype("calibri.ttf", 12)
            except:
                try:
                    # Tentar carregar Calibri alternativa
                    font = ImageFont.truetype("calibri", 12)
                except:
                    try:
                        # Tentar Arial como fallback
                        font = ImageFont.truetype("arial.ttf", 12)
                    except:
                        # Fallback para fonte padrão
                        font = ImageFont.load_default()
            
            # Desenha as caixas delimitadoras apenas para caracteres selecionados
            for char_id in self.selected_chars:
                char_info = self.font_data.get(char_id)
                if not char_info:
                    continue
                    
                x = char_info['x']
                y = char_info['y']
                width = char_info['width']
                height = char_info['height']
                
                # Desenha o retângulo
                draw.rectangle(
                    [x, y, x + width, y + height],
                    outline=box_color,
                    width=1
                )
                
                # Desenha cruz no centro
                center_x = x + width // 2
                center_y = y + height // 2
                draw.line(
                    [(center_x - 5, center_y), (center_x + 5, center_y)],
                    fill=box_color,
                    width=1
                )
                draw.line(
                    [(center_x, center_y - 5), (center_x, center_y + 5)],
                    fill=box_color,
                    width=1
                )
                
                # Desenha o caractere abaixo da cruz
                char_text = self.ID_TO_CHAR.get(char_id, '?')
                
                # Posiciona o texto abaixo da cruz (centralizado horizontalmente)
                text_x = center_x
                text_y = center_y + 10  # 10 pixels abaixo da cruz
                
                # Desenha o caractere em preto para melhor contraste
                draw.text(
                    (text_x, text_y), 
                    char_text, 
                    fill=(0, 0, 0, 255), 
                    anchor="mt",  # Centraliza horizontalmente, alinha topo verticalmente
                    font=font
                )
            
            # Salva a imagem
            img.save(file_path, "PNG")
            self.root.after(0, self._export_boxes_complete, file_path)
            
        except Exception as e:
            error_msg = f"{self.lang.tr('Error.ExportError')}:\n{str(e)}\n\n{traceback.format_exc()}"
            self.root.after(0, self._export_boxes_error, error_msg)
        finally:
            self.root.after(0, self.show_loading, False)

    def _export_boxes_complete(self, file_path):
        messagebox.showinfo(
            self.lang.tr("Status.Ready"), 
            self.lang.tr("Status.ExportComplete") + f":\n{file_path}"
        )
        self.status_var.set(self.lang.tr("Status.ExportComplete"))

    def _export_boxes_error(self, error):
        messagebox.showerror(self.lang.tr("Error.Title"), error)
        self.status_var.set(self.lang.tr("Error.ExportError"))

    def start_move_rect(self, event):
        """Inicia o movimento do retângulo de mapeamento"""
        self.dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        # Obter as coordenadas atuais do retângulo (em coordenadas de tela)
        self.rect_start_coords = self.canvas.coords("rect")

    def start_resize_rect(self, event):
        """Inicia o redimensionamento do retângulo de mapeamento"""
        self.resizing_rect = True
        self.resize_start_x = event.x
        self.resize_start_y = event.y
        self.rect_start_coords = self.canvas.coords("rect")

    def on_mouse_drag(self, event):
        """Manipula o arraste do mouse para movimento e redimensionamento"""
        if self.dragging:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            # Mover todos os itens com tag "highlight" (incluindo retângulo, texto, ponto central, alça)
            self.canvas.move("highlight", dx, dy)
            # Atualizar o ponto de início para o próximo evento
            self.drag_start_x = event.x
            self.drag_start_y = event.y

        elif self.resizing_rect:
            dx = event.x - self.resize_start_x
            dy = event.y - self.resize_start_y
            # Vamos redimensionar o retângulo: a nova largura e altura será a original + dx, dy
            # Mas note: as coordenadas iniciais do retângulo estão em self.rect_start_coords: [x0, y0, x1, y1]
            x0, y0, x1, y1 = self.rect_start_coords
            new_x1 = x1 + dx
            new_y1 = y1 + dy
            # Atualizar as coordenadas do retângulo
            self.canvas.coords("rect", x0, y0, new_x1, new_y1)
            # Atualizar a posição da alça de redimensionamento (que está no canto inferior direito)
            handle_x = new_x1 - self.resize_handle_size/2
            handle_y = new_y1 - self.resize_handle_size/2
            # A alça de redimensionamento tem a tag "resize_handle", mas pode ser a única com essa tag.
            self.canvas.coords("resize_handle", 
                              handle_x, handle_y, 
                              handle_x + self.resize_handle_size, handle_y + self.resize_handle_size)

    def on_mouse_release(self, event):
        """Finaliza o movimento ou redimensionamento do retângulo"""
        if self.dragging or self.resizing_rect:
            # Obter as coordenadas atuais do retângulo
            coords = self.canvas.coords("rect")
            # Converter para coordenadas da imagem original (dividir pelo zoom)
            x0 = coords[0] / self.image_zoom
            y0 = coords[1] / self.image_zoom
            x1 = coords[2] / self.image_zoom
            y1 = coords[3] / self.image_zoom

            width = x1 - x0
            height = y1 - y0

            # Salvar estado ANTES da alteração (para poder desfazer)
            action_type = "Move" if self.dragging else "Resize"
            self.save_state(f"{action_type} of character ID {self.current_char_id}")

            # Atualizar os dados do caractere
            if self.current_char_id:
                char_info = self.font_data.get(self.current_char_id)
                if char_info:
                    char_info['x'] = int(x0)
                    char_info['y'] = int(y0)
                    char_info['width'] = int(width)
                    char_info['height'] = int(height)

                    # Atualizar as variáveis de entrada
                    self.info_vars['x'].set(str(int(x0)))
                    self.info_vars['y'].set(str(int(y0)))
                    self.info_vars['width'].set(str(int(width)))
                    self.info_vars['height'].set(str(int(height)))

                    # Redesenhar o destaque (para incluir o ponto central e o texto)
                    self.highlight_char(self.current_char_id)

            # Resetar as flags
            self.dragging = False
            self.resizing_rect = False
            self.rect_start_coords = None

    def update_sliders_limits(self):
        """Atualiza os limites máximos de todos os sliders"""
        if not self.current_image:
            return
            
        img_width = self.current_image.width
        img_height = self.current_image.height
        
        for key, (_, slider) in self.slider_widgets.items():
            if key == 'x':
                slider.configure(to=img_width-1)
            elif key == 'y':
                slider.configure(to=img_height-1)
            elif key == 'width':
                try:
                    x_val = int(self.info_vars['x'].get())
                    slider.configure(to=img_width - x_val)
                except:
                    slider.configure(to=img_width)
            elif key == 'height':
                try:
                    y_val = int(self.info_vars['y'].get())
                    slider.configure(to=img_height - y_val)
                except:
                    slider.configure(to=img_height)
            else:
                # Para as outras, configurar to=500
                slider.configure(to=500)
                
            # Sincronizar o valor atual
            self.sync_slider(key)

    def update_slider_limits(self, key):
        """Atualiza os limites de um slider específico"""
        if not self.current_image or key not in self.slider_widgets:
            return
            
        img_width = self.current_image.width
        img_height = self.current_image.height
        
        _, slider = self.slider_widgets[key]
        
        if key == 'x':
            slider.configure(to=img_width-1)
        elif key == 'y':
            slider.configure(to=img_height-1)
        elif key == 'width':
            try:
                x_val = int(self.info_vars['x'].get())
                slider.configure(to=img_width - x_val)
            except:
                slider.configure(to=img_width)
        elif key == 'height':
            try:
                y_val = int(self.info_vars['y'].get())
                slider.configure(to=img_height - y_val)
            except:
                slider.configure(to=img_height)
        else:
            slider.configure(to=500)

    def sync_slider(self, key):
        """Sincroniza a posição do slider com o valor do campo de entrada"""
        if key in self.slider_widgets:
            try:
                # Bloquear recursão
                self.programmatic_slider_update = True
                
                # Obter valor atual
                value = int(self.info_vars[key].get())
                
                # Obter slider
                _, slider = self.slider_widgets[key]
                
                # Verificar limites
                current_min = slider.cget("from")
                current_max = slider.cget("to")
                if value < current_min:
                    value = current_min
                elif value > current_max:
                    value = current_max
                
                # Atualizar slider
                slider.set(value)
                
            except ValueError:
                pass
            except Exception as e:
                print(f"Error syncing slider {key}: {str(e)}")
            finally:
                self.programmatic_slider_update = False

    def show_loading(self, show):
        """Mostra ou oculta o indicador de carregamento"""
        if show:
            self.loading_label.place(relx=0.5, rely=0.5, anchor="center")
            self.root.update()
        else:
            self.loading_label.place_forget()
            
    def confirm_exit(self):
        """Exibe confirmação antes de sair se houver alterações não salvas"""
        if self.unsaved_changes:
            # Criar diálogo personalizado para manter a internacionalização
            dialog = tk.Toplevel(self.root)
            dialog.title(self.lang.tr("Dialog.ConfirmExitTitle"))
            dialog.transient(self.root)
            dialog.grab_set()
            dialog.resizable(False, False)
            
            # Centralizar na tela
            dialog_width = 400
            dialog_height = 150
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width - dialog_width) // 2
            y = (screen_height - dialog_height) // 2
            dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
            
            # Configurar layout
            main_frame = ttk.Frame(dialog, padding=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Mensagem
            message = ttk.Label(
                main_frame, 
                text=self.lang.tr("Dialog.ConfirmExitMessage"),
                wraplength=350,
                justify=tk.CENTER
            )
            message.pack(pady=(0, 20))
            
            # Botões
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X)
            
            save_btn = ttk.Button(
                button_frame, 
                text=self.lang.tr("Dialog.SaveOption"),
                command=lambda: self.save_and_exit(dialog)
            )
            save_btn.pack(side=tk.LEFT, expand=True, padx=5)
            
            dont_save_btn = ttk.Button(
                button_frame, 
                text=self.lang.tr("Dialog.DontSaveOption"),
                command=lambda: self.exit_without_saving(dialog)
            )
            dont_save_btn.pack(side=tk.LEFT, expand=True, padx=5)
            
            cancel_btn = ttk.Button(
                button_frame, 
                text=self.lang.tr("Dialog.CancelOption"),
                command=dialog.destroy
            )
            cancel_btn.pack(side=tk.LEFT, expand=True, padx=5)
        else:
            self.root.destroy()

    def save_and_exit(self, dialog):
        if self.save_changes():
            dialog.destroy()
            self.root.destroy()

    def exit_without_saving(self, dialog):
        dialog.destroy()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FontMapViewer(root)
    root.mainloop()
